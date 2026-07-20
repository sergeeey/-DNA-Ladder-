#!/usr/bin/env python3
"""T2 positive-control gate: CTCF enrichment at Hi-C loop anchors.

Pipeline sanity only — NOT the primary TE claim.

Method (pre-registered in controls.md / this script):
  1. Extract unique anchors from Hi-C bedpe (ENCFF693XIL).
  2. Overlap anchors with CTCF K562 IDR peaks (ENCFF769AUF).
  3. Chromosome-preserving shuffle of CTCF peaks (same lengths, random starts
     within chrom span observed in data; n_shuffles replicates → mean null rate).
  4. Build 2x2 contingency for Fisher exact:
       observed: anchors overlapping real CTCF vs not
       null:     same n_anchors with expected overlap rate from shuffle
     Practically: compare observed overlap count vs mean shuffle overlap via
     Fisher on [obs_hit, obs_miss; null_hit, null_miss] where null uses the
     mean shuffled hit rate × n_anchors (rounded) — plus report empirical
     enrichment OR = (obs_rate / null_rate).

Gate: Fisher OR ≥ 2.0 → PASS (expected ≥5 for CTCF×Hi-C); OR < 2.0 → BLOCKED.

Does NOT invent primary TE ORs.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"

DEFAULT_HIC = DATA / "ENCFF693XIL.bedpe.gz"
DEFAULT_CTCF = DATA / "ENCFF769AUF.bed.gz"
GATE_OR_THRESHOLD = 2.0
N_SHUFFLES = 50
SEED = 42
CANON_CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX"}


Interval = tuple[str, int, int]


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("rt")


def load_bed_intervals(path: Path, min_cols: int = 3) -> list[Interval]:
    out: list[Interval] = []
    with open_text(path) as f:
        for line in f:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < min_cols:
                continue
            chrom, start, end = cols[0], int(cols[1]), int(cols[2])
            if chrom not in CANON_CHROMS:
                continue
            if end <= start:
                continue
            out.append((chrom, start, end))
    return out


def load_bedpe_anchors(path: Path) -> list[Interval]:
    """Unique (chrom, start, end) anchors from both ends of each loop."""
    seen: set[Interval] = set()
    with open_text(path) as f:
        for line in f:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 6:
                continue
            for chrom, s, e in (
                (cols[0], int(cols[1]), int(cols[2])),
                (cols[3], int(cols[4]), int(cols[5])),
            ):
                if chrom not in CANON_CHROMS or e <= s:
                    continue
                seen.add((chrom, s, e))
    return sorted(seen)


def chrom_spans(intervals: Iterable[Interval]) -> dict[str, int]:
    """Max end per chrom as a proxy span for shuffling (no chrom.sizes required)."""
    spans: dict[str, int] = {}
    for chrom, _s, e in intervals:
        spans[chrom] = max(spans.get(chrom, 0), e)
    # pad so shuffled peaks near the end still fit
    return {c: max(e + 1_000_000, e) for c, e in spans.items()}


def build_interval_index(intervals: list[Interval]) -> dict[str, list[tuple[int, int]]]:
    by: dict[str, list[tuple[int, int]]] = {}
    for chrom, s, e in intervals:
        by.setdefault(chrom, []).append((s, e))
    for chrom in by:
        by[chrom].sort()
    return by


def overlaps_any(chrom: str, start: int, end: int, index: dict[str, list[tuple[int, int]]]) -> bool:
    """True if [start, end) overlaps any interval on chrom (sorted list scan with early stop)."""
    intervals = index.get(chrom)
    if not intervals:
        return False
    # binary-search-ish: find first interval with end > start
    lo, hi = 0, len(intervals)
    while lo < hi:
        mid = (lo + hi) // 2
        if intervals[mid][1] <= start:
            lo = mid + 1
        else:
            hi = mid
    for i in range(lo, len(intervals)):
        s, e = intervals[i]
        if s >= end:
            break
        if s < end and e > start:
            return True
    return False


def count_overlapping_anchors(
    anchors: list[Interval], peak_index: dict[str, list[tuple[int, int]]]
) -> int:
    return sum(1 for c, s, e in anchors if overlaps_any(c, s, e, peak_index))


def shuffle_peaks(
    peaks: list[Interval], spans: dict[str, int], rng: random.Random
) -> list[Interval]:
    out: list[Interval] = []
    for chrom, s, e in peaks:
        length = e - s
        chrom_end = spans.get(chrom, e)
        max_start = chrom_end - length
        if max_start <= 0:
            out.append((chrom, s, e))
            continue
        ns = rng.randint(0, max_start)
        out.append((chrom, ns, ns + length))
    return out


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """Fisher exact test OR and two-sided p-value (hypergeometric).

    Table:
        a b
        c d
    OR = (a/b)/(c/d) = ad/bc
    """
    # Haldane-Anscombe correction for OR if any zero cell
    a1, b1, c1, d1 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    odds_ratio = (a1 * d1) / (b1 * c1)

    n = a + b + c + d
    if n == 0:
        return float("nan"), 1.0

    # Two-sided Fisher via summing hypergeometric probs ≤ observed
    # Row1 = a+b fixed, Col1 = a+c fixed
    row1 = a + b
    col1 = a + c
    # Support for a: max(0, row1+col1-n) .. min(row1, col1)
    lo = max(0, row1 + col1 - n)
    hi = min(row1, col1)

    def log_choose(n_: int, k_: int) -> float:
        if k_ < 0 or k_ > n_:
            return float("-inf")
        return math.lgamma(n_ + 1) - math.lgamma(k_ + 1) - math.lgamma(n_ - k_ + 1)

    def log_hyper(k: int) -> float:
        # P(K=k) = C(col1,k)*C(n-col1, row1-k) / C(n, row1)
        return (
            log_choose(col1, k)
            + log_choose(n - col1, row1 - k)
            - log_choose(n, row1)
        )

    log_p_obs = log_hyper(a)
    p = 0.0
    for k in range(lo, hi + 1):
        lp = log_hyper(k)
        if lp <= log_p_obs + 1e-12:
            p += math.exp(lp)
    p = min(1.0, max(0.0, p))
    return odds_ratio, p


def woolf_or_ci(a: int, b: int, c: int, d: int, z: float = 1.96) -> tuple[float, float, float]:
    """Logit / Woolf CI for OR with Haldane-Anscombe 0.5 continuity."""
    a1, b1, c1, d1 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    log_or = math.log((a1 * d1) / (b1 * c1))
    se = math.sqrt(1 / a1 + 1 / b1 + 1 / c1 + 1 / d1)
    lo = math.exp(log_or - z * se)
    hi = math.exp(log_or + z * se)
    return math.exp(log_or), lo, hi


def run_gate(
    hic_path: Path,
    ctcf_path: Path,
    n_shuffles: int = N_SHUFFLES,
    seed: int = SEED,
    threshold: float = GATE_OR_THRESHOLD,
) -> dict:
    anchors = load_bedpe_anchors(hic_path)
    peaks = load_bed_intervals(ctcf_path)
    if not anchors:
        raise SystemExit(f"No anchors parsed from {hic_path}")
    if not peaks:
        raise SystemExit(f"No CTCF peaks parsed from {ctcf_path}")

    peak_index = build_interval_index(peaks)
    obs_hit = count_overlapping_anchors(anchors, peak_index)
    n_anchors = len(anchors)
    obs_miss = n_anchors - obs_hit
    obs_rate = obs_hit / n_anchors

    spans = chrom_spans(list(anchors) + list(peaks))
    rng = random.Random(seed)
    shuffle_hits: list[int] = []
    for _ in range(n_shuffles):
        shuf = shuffle_peaks(peaks, spans, rng)
        shuf_index = build_interval_index(shuf)
        shuffle_hits.append(count_overlapping_anchors(anchors, shuf_index))

    mean_null_hit = sum(shuffle_hits) / len(shuffle_hits)
    # Round for contingency; keep fractional rate for enrichment ratio
    null_hit = int(round(mean_null_hit))
    null_hit = min(max(null_hit, 0), n_anchors)
    null_miss = n_anchors - null_hit
    null_rate = mean_null_hit / n_anchors if n_anchors else float("nan")

    # Contingency: rows = real CTCF vs shuffled-mean null; cols = hit vs miss
    # Enrichment of hits under real CTCF relative to null expectation
    fisher_or, fisher_p = fisher_exact_two_sided(obs_hit, obs_miss, null_hit, null_miss)
    woolf_or, ci_lo, ci_hi = woolf_or_ci(obs_hit, obs_miss, null_hit, null_miss)
    empiric_or = (obs_rate / null_rate) if null_rate > 0 else float("inf")

    gate_or = fisher_or  # primary gate statistic
    if gate_or >= threshold:
        verdict = "PASS"
        decision_status = "PENDING_PRIMARY"
    else:
        verdict = "BLOCKED"
        decision_status = "BLOCKED_PIPELINE"

    return {
        "script": "t2_positive_control_ctcf_gate",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembly": "GRCh38",
        "inputs": {
            "hic_bedpe": str(hic_path),
            "hic_accession": "ENCFF693XIL",
            "ctcf_peaks": str(ctcf_path),
            "ctcf_accession": "ENCFF769AUF",
            "ctcf_experiment": "ENCSR000AKO",
        },
        "parameters": {
            "n_shuffles": n_shuffles,
            "seed": seed,
            "gate_or_threshold": threshold,
            "chroms": "canonical chr1-22,X",
            "null": "chromosome-preserving peak-length shuffle within observed chrom spans",
        },
        "counts": {
            "n_hic_anchors_unique": n_anchors,
            "n_ctcf_peaks": len(peaks),
            "obs_anchors_overlapping_ctcf": obs_hit,
            "obs_anchors_not_overlapping": obs_miss,
            "obs_overlap_rate": obs_rate,
            "shuffle_hit_counts": shuffle_hits,
            "mean_null_hit": mean_null_hit,
            "null_hit_rounded": null_hit,
            "null_miss_rounded": null_miss,
            "null_overlap_rate": null_rate,
        },
        "statistics": {
            "fisher_odds_ratio": gate_or,
            "fisher_p_two_sided": fisher_p,
            "woolf_or": woolf_or,
            "woolf_or_ci95": [ci_lo, ci_hi],
            "empirical_rate_ratio": empiric_or,
            "contingency_ab_cd": [obs_hit, obs_miss, null_hit, null_miss],
        },
        "gate": {
            "threshold_or": threshold,
            "verdict": verdict,
            "decision_status": decision_status,
            "note": (
                "PASS means pipeline recovers CTCF enrichment at Hi-C anchors; "
                "does NOT authorize primary TE OR claims."
                if verdict == "PASS"
                else "BLOCKED: CTCF positive gate failed — do not interpret TE biology."
            ),
        },
        "primary_te_or": None,
        "explicit_non_claims": [
            "No primary TE subfamily OR computed",
            "Holdout untouched",
            "No C1 E/P or wet-lab GO",
        ],
    }


def write_markdown(result: dict, path: Path) -> None:
    st = result["statistics"]
    c = result["counts"]
    g = result["gate"]
    lines = [
        "# Positive control — CTCF gate (T2)",
        "",
        f"**Computed:** `{result['computed_at_utc']}`  ",
        f"**Verdict:** `{g['verdict']}`  ",
        f"**Decision status:** `{g['decision_status']}`  ",
        "",
        "## Inputs",
        "",
        f"- Hi-C loops: `{result['inputs']['hic_accession']}` ({result['inputs']['hic_bedpe']})",
        f"- CTCF peaks: `{result['inputs']['ctcf_accession']}` / `{result['inputs']['ctcf_experiment']}`",
        f"- Assembly: {result['assembly']}",
        "",
        "## Counts",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Unique Hi-C anchors (chr1–22,X) | {c['n_hic_anchors_unique']} |",
        f"| CTCF peaks | {c['n_ctcf_peaks']} |",
        f"| Anchors overlapping CTCF (obs) | {c['obs_anchors_overlapping_ctcf']} ({c['obs_overlap_rate']:.4f}) |",
        f"| Mean null overlaps (chr-preserving shuffle, n={result['parameters']['n_shuffles']}) | {c['mean_null_hit']:.2f} ({c['null_overlap_rate']:.4f}) |",
        "",
        "## Statistics",
        "",
        f"| Statistic | Value |",
        f"|-----------|-------|",
        f"| Fisher OR (gate) | {st['fisher_odds_ratio']:.4f} |",
        f"| Fisher p (two-sided) | {st['fisher_p_two_sided']:.4e} |",
        f"| Woolf OR (95% CI) | {st['woolf_or']:.4f} ({st['woolf_or_ci95'][0]:.4f}–{st['woolf_or_ci95'][1]:.4f}) |",
        f"| Empirical rate ratio | {st['empirical_rate_ratio']:.4f} |",
        f"| Gate threshold | OR ≥ {g['threshold_or']} |",
        "",
        f"**Gate note:** {g['note']}",
        "",
        "## What this does NOT mean",
        "",
        "1. NOT a primary TE enrichment result (none computed).",
        "2. NOT causal CTCF → loop proof.",
        "3. NOT authorization to unseal holdout, edit C1 E/P, or order oligos.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hic", type=Path, default=DEFAULT_HIC)
    ap.add_argument("--ctcf", type=Path, default=DEFAULT_CTCF)
    ap.add_argument("--n-shuffles", type=int, default=N_SHUFFLES)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--threshold", type=float, default=GATE_OR_THRESHOLD)
    args = ap.parse_args()

    if not args.hic.exists():
        print(f"Missing Hi-C bedpe: {args.hic}", file=sys.stderr)
        return 1
    if not args.ctcf.exists():
        print(f"Missing CTCF peaks: {args.ctcf}", file=sys.stderr)
        return 1

    RESULTS.mkdir(parents=True, exist_ok=True)
    result = run_gate(
        args.hic, args.ctcf, n_shuffles=args.n_shuffles, seed=args.seed, threshold=args.threshold
    )
    json_path = RESULTS / "positive_control_ctcf_gate.json"
    md_path = RESULTS / "positive_control_ctcf_gate.md"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, md_path)
    print(json.dumps({"verdict": result["gate"]["verdict"], **result["statistics"]}, indent=2))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
