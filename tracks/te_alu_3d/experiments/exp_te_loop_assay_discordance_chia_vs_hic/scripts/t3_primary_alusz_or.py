#!/usr/bin/env python3
"""T3 primary desk analysis: AluSz enrichment Pol II ChIA-PET vs Hi-C anchors.

Preregistered single-cell-type (K562) stage:
  - Unit: non-redundant merged anchors, padded to ≥1 kb
  - Primary TE: AluSz only (exact RepeatMasker repName)
  - Statistic: Fisher exact OR + Woolf 95% CI; chromosome block-bootstrap CI
  - Matched null: ≥200 chromosome-preserving label permutations stratified on
    chromosome + width bin (GC skipped — no genome FASTA; PENDING_GC)
  - MAPQ: processed bedpe lacks MAPQ → PENDING_MAPPABILITY (umap not used)
  - Exploratory secondary (NOT primary): SVA_F, AluJo

Does NOT claim mechanism. Does NOT touch holdout / C1 / wet GO.
Does NOT change primary subfamily post-hoc.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"

CANON = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
PRIMARY_TE = "AluSz"
EXPLORATORY_TES = ("SVA_F", "AluJo")
MIN_ANCHOR_BP = 1000
N_PERM_DEFAULT = 200
N_BOOT_DEFAULT = 500
SEED = 42
MCID_SUPPORT = 1.3
MCID_FAIL = 1.1

# UCSC rmsk columns
RMSK_CHROM, RMSK_START, RMSK_END, RMSK_NAME = 5, 6, 7, 10

Interval = tuple[str, int, int]
Anchor = tuple[str, int, int]  # chrom, start, end


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("rt")


def load_bedpe_anchors(path: Path) -> list[Anchor]:
    seen: set[Anchor] = set()
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
                if chrom in CANON and e > s:
                    seen.add((chrom, s, e))
    return sorted(seen)


def merge_intervals(anchors: list[Anchor]) -> list[Anchor]:
    by: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for c, s, e in anchors:
        by[c].append((s, e))
    out: list[Anchor] = []
    for chrom, ivs in by.items():
        ivs.sort()
        cs, ce = ivs[0]
        for s, e in ivs[1:]:
            if s <= ce:  # overlap or book-ended
                ce = max(ce, e)
            else:
                out.append((chrom, cs, ce))
                cs, ce = s, e
        out.append((chrom, cs, ce))
    return sorted(out)


def pad_min_width(anchors: list[Anchor], min_bp: int = MIN_ANCHOR_BP) -> list[Anchor]:
    out: list[Anchor] = []
    for chrom, s, e in anchors:
        w = e - s
        if w >= min_bp:
            out.append((chrom, s, e))
            continue
        mid = (s + e) // 2
        half = min_bp // 2
        s2 = max(0, mid - half)
        e2 = s2 + min_bp
        out.append((chrom, s2, e2))
    return out


def build_units(raw: list[Anchor], min_bp: int = MIN_ANCHOR_BP) -> list[Anchor]:
    return pad_min_width(merge_intervals(raw), min_bp=min_bp)


def midpoint_windows(anchors: list[Anchor], win_bp: int = MIN_ANCHOR_BP) -> list[Anchor]:
    """Fixed-width analysis windows at merged-anchor midpoints (equalizes span)."""
    out: list[Anchor] = []
    half = win_bp // 2
    for chrom, s, e in anchors:
        mid = (s + e) // 2
        s2 = max(0, mid - half)
        out.append((chrom, s2, s2 + win_bp))
    return out


def load_rmsk_by_name(path: Path, names: set[str]) -> dict[str, list[tuple[int, int]]]:
    """Return chrom -> sorted (start,end) for exact repName matches."""
    by: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with gzip.open(path, "rt") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= RMSK_NAME:
                continue
            chrom = cols[RMSK_CHROM]
            if chrom not in CANON:
                continue
            name = cols[RMSK_NAME]
            if name not in names:
                continue
            try:
                start, end = int(cols[RMSK_START]), int(cols[RMSK_END])
            except ValueError:
                continue
            if end > start:
                by[f"{chrom}\t{name}"].append((start, end))
    # sort each list
    out: dict[str, list[tuple[int, int]]] = {}
    for key, ivs in by.items():
        ivs.sort()
        out[key] = ivs
    return out


def build_index(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return intervals  # already sorted


def overlaps_any(start: int, end: int, intervals: list[tuple[int, int]]) -> bool:
    if not intervals:
        return False
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


def annotate_overlaps(
    anchors: list[Anchor], rmsk_by: dict[str, list[tuple[int, int]]], te_name: str
) -> list[bool]:
    hits: list[bool] = []
    for chrom, s, e in anchors:
        ivs = rmsk_by.get(f"{chrom}\t{te_name}", [])
        hits.append(overlaps_any(s, e, ivs))
    return hits


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    a1, b1, c1, d1 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    odds_ratio = (a1 * d1) / (b1 * c1)
    n = a + b + c + d
    if n == 0:
        return float("nan"), 1.0
    row1 = a + b
    col1 = a + c
    lo = max(0, row1 + col1 - n)
    hi = min(row1, col1)

    def log_choose(n_: int, k_: int) -> float:
        if k_ < 0 or k_ > n_:
            return float("-inf")
        return math.lgamma(n_ + 1) - math.lgamma(k_ + 1) - math.lgamma(n_ - k_ + 1)

    def log_hyper(k: int) -> float:
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
    return odds_ratio, min(1.0, max(0.0, p))


def woolf_or_ci(a: int, b: int, c: int, d: int, z: float = 1.96) -> tuple[float, float, float]:
    a1, b1, c1, d1 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    log_or = math.log((a1 * d1) / (b1 * c1))
    se = math.sqrt(1 / a1 + 1 / b1 + 1 / c1 + 1 / d1)
    return math.exp(log_or), math.exp(log_or - z * se), math.exp(log_or + z * se)


def contingency_or(pol2_hits: list[bool], hic_hits: list[bool]) -> dict:
    a = sum(pol2_hits)
    b = len(pol2_hits) - a
    c = sum(hic_hits)
    d = len(hic_hits) - c
    fisher_or, fisher_p = fisher_exact_two_sided(a, b, c, d)
    woolf_or, ci_lo, ci_hi = woolf_or_ci(a, b, c, d)
    return {
        "a_pol2_te_pos": a,
        "b_pol2_te_neg": b,
        "c_hic_te_pos": c,
        "d_hic_te_neg": d,
        "n_pol2": len(pol2_hits),
        "n_hic": len(hic_hits),
        "pol2_rate": a / len(pol2_hits) if pol2_hits else float("nan"),
        "hic_rate": c / len(hic_hits) if hic_hits else float("nan"),
        "fisher_or": fisher_or,
        "fisher_p_two_sided": fisher_p,
        "woolf_or": woolf_or,
        "woolf_ci95_lo": ci_lo,
        "woolf_ci95_hi": ci_hi,
    }


def width_bin(width: int, edges: list[int]) -> int:
    for i, e in enumerate(edges):
        if width <= e:
            return i
    return len(edges)


def compute_width_edges(widths: Iterable[int], n_bins: int = 4) -> list[int]:
    ws = sorted(widths)
    if not ws:
        return [MIN_ANCHOR_BP]
    edges: list[int] = []
    for q in range(1, n_bins):
        idx = min(len(ws) - 1, int(round(q * len(ws) / n_bins)) - 1)
        edges.append(ws[max(0, idx)])
    # unique increasing
    uniq: list[int] = []
    for e in edges:
        if not uniq or e > uniq[-1]:
            uniq.append(e)
    if not uniq:
        uniq = [ws[len(ws) // 2]]
    return uniq


def matched_null_permutations(
    pol2: list[Anchor],
    hic: list[Anchor],
    pol2_hits: list[bool],
    hic_hits: list[bool],
    n_perm: int,
    seed: int,
) -> dict:
    """Shuffle TE labels within (chrom, width_bin) strata across both arms."""
    records: list[tuple[str, int, str, bool]] = []  # chrom, wbin, arm, hit
    all_widths = [e - s for _, s, e in pol2] + [e - s for _, s, e in hic]
    edges = compute_width_edges(all_widths, n_bins=4)
    for (c, s, e), hit in zip(pol2, pol2_hits):
        records.append((c, width_bin(e - s, edges), "pol2", hit))
    for (c, s, e), hit in zip(hic, hic_hits):
        records.append((c, width_bin(e - s, edges), "hic", hit))

    strata: dict[tuple[str, int], list[int]] = defaultdict(list)
    for i, (c, wb, _arm, _hit) in enumerate(records):
        strata[(c, wb)].append(i)

    obs = contingency_or(pol2_hits, hic_hits)["fisher_or"]
    rng = random.Random(seed)
    null_ors: list[float] = []
    hits_arr = [r[3] for r in records]
    arms = [r[2] for r in records]

    for _ in range(n_perm):
        shuffled = hits_arr[:]
        for idxs in strata.values():
            labels = [shuffled[i] for i in idxs]
            rng.shuffle(labels)
            for i, lab in zip(idxs, labels):
                shuffled[i] = lab
        p2 = [shuffled[i] for i, arm in enumerate(arms) if arm == "pol2"]
        hc = [shuffled[i] for i, arm in enumerate(arms) if arm == "hic"]
        null_ors.append(contingency_or(p2, hc)["fisher_or"])

    ge = sum(1 for x in null_ors if x >= obs)
    le = sum(1 for x in null_ors if x <= obs)
    # two-sided empirical
    emp_p = (min(ge, le) * 2 + 1) / (n_perm + 1)
    emp_p = min(1.0, emp_p)
    null_ors_sorted = sorted(null_ors)
    return {
        "n_perm": n_perm,
        "seed": seed,
        "matching": "chromosome + width quartile (pooled arms); GC PENDING (no FASTA)",
        "width_bin_edges_bp": edges,
        "n_strata": len(strata),
        "observed_fisher_or": obs,
        "null_or_mean": sum(null_ors) / len(null_ors),
        "null_or_median": null_ors_sorted[len(null_ors_sorted) // 2],
        "null_or_p025": null_ors_sorted[max(0, int(0.025 * n_perm) - 1)],
        "null_or_p975": null_ors_sorted[min(n_perm - 1, int(0.975 * n_perm))],
        "emp_p_two_sided": emp_p,
        "frac_null_ge_obs": ge / n_perm,
        "frac_null_le_obs": le / n_perm,
    }


def chrom_block_bootstrap_ci(
    pol2: list[Anchor],
    hic: list[Anchor],
    pol2_hits: list[bool],
    hic_hits: list[bool],
    n_boot: int,
    seed: int,
) -> dict:
    by_pol2: dict[str, list[bool]] = defaultdict(list)
    by_hic: dict[str, list[bool]] = defaultdict(list)
    for (c, _s, _e), hit in zip(pol2, pol2_hits):
        by_pol2[c].append(hit)
    for (c, _s, _e), hit in zip(hic, hic_hits):
        by_hic[c].append(hit)
    chroms = sorted(set(by_pol2) | set(by_hic))
    rng = random.Random(seed + 7)
    ors: list[float] = []
    for _ in range(n_boot):
        sample = [rng.choice(chroms) for _ in chroms]
        p2: list[bool] = []
        hc: list[bool] = []
        for c in sample:
            p2.extend(by_pol2.get(c, []))
            hc.extend(by_hic.get(c, []))
        if not p2 or not hc:
            continue
        ors.append(contingency_or(p2, hc)["fisher_or"])
    ors.sort()
    n = len(ors)
    if n == 0:
        return {"n_boot": n_boot, "status": "FAILED_EMPTY"}
    return {
        "n_boot": n_boot,
        "seed": seed + 7,
        "method": "chromosome block bootstrap (resample chroms w/ replacement)",
        "or_mean": sum(ors) / n,
        "ci95_lo": ors[max(0, int(0.025 * n) - 1)],
        "ci95_hi": ors[min(n - 1, int(0.975 * n))],
        "n_successful": n,
    }


def desk_verdict(or_value: float, ci_lo: float, ci_hi: float) -> dict:
    """Single-cell-type desk thresholds; full REJECT needs MAPQ+replication."""
    if or_value >= MCID_SUPPORT:
        label = "SUPPORT_DESK"
        note = (
            f"OR={or_value:.4f} ≥ MCID {MCID_SUPPORT}; single-cell-type (K562) desk support "
            "only — pending independent replication cell type / biorep before claim upgrade. "
            "MAPQ/mappability kill-test still PENDING_MAPPABILITY."
        )
    elif or_value < MCID_FAIL:
        label = "FAIL_DESK_PRIMARY"
        note = (
            f"OR={or_value:.4f} < falsify threshold {MCID_FAIL} at desk primary stage. "
            "Full claim REJECT per claim.md still requires MAPQ≥30 (or equivalent) + "
            "replication — not filed as null_results REJECT yet."
        )
    else:
        label = "INCONCLUSIVE_DESK"
        note = (
            f"OR={or_value:.4f} between falsify ({MCID_FAIL}) and support ({MCID_SUPPORT}); "
            "inconclusive at single-cell-type desk stage pending replication / mappability."
        )
    return {
        "verdict": label,
        "mcid_support": MCID_SUPPORT,
        "mcid_fail": MCID_FAIL,
        "or": or_value,
        "woolf_ci95": [ci_lo, ci_hi],
        "note": note,
    }


def run_analysis(
    pol2_path: Path,
    hic_path: Path,
    rmsk_path: Path,
    n_perm: int = N_PERM_DEFAULT,
    n_boot: int = N_BOOT_DEFAULT,
    seed: int = SEED,
    min_bp: int = MIN_ANCHOR_BP,
) -> dict:
    raw_pol2 = load_bedpe_anchors(pol2_path)
    raw_hic = load_bedpe_anchors(hic_path)
    pol2_units = build_units(raw_pol2, min_bp=min_bp)
    hic_units = build_units(raw_hic, min_bp=min_bp)
    # Primary scoring windows: fixed 1 kb at midpoint (assay span distributions
    # otherwise non-overlapping: Hi-C ~5–25 kb vs Pol II ~1 kb after pad).
    pol2 = midpoint_windows(pol2_units, win_bp=min_bp)
    hic = midpoint_windows(hic_units, win_bp=min_bp)

    te_names = {PRIMARY_TE, *EXPLORATORY_TES}
    rmsk_by = load_rmsk_by_name(rmsk_path, te_names)

    pol2_primary = annotate_overlaps(pol2, rmsk_by, PRIMARY_TE)
    hic_primary = annotate_overlaps(hic, rmsk_by, PRIMARY_TE)
    primary = contingency_or(pol2_primary, hic_primary)

    # Sensitivity: full merged-span overlap (known width-confounded)
    pol2_full = annotate_overlaps(pol2_units, rmsk_by, PRIMARY_TE)
    hic_full = annotate_overlaps(hic_units, rmsk_by, PRIMARY_TE)
    full_span_sensitivity = contingency_or(pol2_full, hic_full)
    full_span_sensitivity["role"] = "SENSITIVITY_FULL_SPAN"
    full_span_sensitivity["note"] = (
        "Full merged-interval overlap; confounded by non-overlapping width "
        "distributions across assays. Not the primary estimand."
    )

    boot = chrom_block_bootstrap_ci(pol2, hic, pol2_primary, hic_primary, n_boot, seed)
    perm = matched_null_permutations(
        pol2, hic, pol2_primary, hic_primary, n_perm=n_perm, seed=seed
    )
    verdict = desk_verdict(
        primary["fisher_or"], primary["woolf_ci95_lo"], primary["woolf_ci95_hi"]
    )

    exploratory = []
    for te in EXPLORATORY_TES:
        p_hits = annotate_overlaps(pol2, rmsk_by, te)
        h_hits = annotate_overlaps(hic, rmsk_by, te)
        row = contingency_or(p_hits, h_hits)
        row["te"] = te
        row["role"] = "EXPLORATORY_SECONDARY"
        row["note"] = (
            "Exploratory only — not primary claim. AluJo is negative/contrast control "
            "(expectation ~OR≈1 under young-TE narrative)."
            if te == "AluJo"
            else "Exploratory only — not primary claim."
        )
        exploratory.append(row)

    mapq_status = "PENDING_MAPPABILITY"
    mapq_note = (
        "Processed ENCODE bedpe (ENCFF511QFN / ENCFF693XIL) lack per-anchor MAPQ fields "
        "usable for MAPQ≥30 filtering; umap track not available in this worktree. "
        "Primary OR reported with PENDING_MAPPABILITY caveat; MAPQ/umap sensitivity deferred."
    )

    return {
        "script": "t3_primary_alusz_or",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembly": "GRCh38",
        "primary_te": PRIMARY_TE,
        "unit_definition": {
            "description": (
                "non-redundant merged anchors ≥1 kb; primary TE overlap scored on "
                "fixed 1 kb midpoint windows to equalize span across assays"
            ),
            "min_anchor_bp": min_bp,
            "merge": "overlap or book-ended within assay",
            "scoring_window_bp": min_bp,
            "scoring_window": "midpoint ± 500 bp (1 kb)",
        },
        "inputs": {
            "pol2_bedpe": str(pol2_path),
            "pol2_accession": "ENCFF511QFN",
            "hic_bedpe": str(hic_path),
            "hic_accession": "ENCFF693XIL",
            "rmsk": str(rmsk_path),
            "te_source": "UCSC hg38 RepeatMasker rmsk.txt.gz",
        },
        "anchor_counts": {
            "pol2_raw_unique": len(raw_pol2),
            "hic_raw_unique": len(raw_hic),
            "pol2_merged_ge1kb": len(pol2_units),
            "hic_merged_ge1kb": len(hic_units),
            "pol2_scoring_windows_1kb": len(pol2),
            "hic_scoring_windows_1kb": len(hic),
        },
        "mapq_mappability": {
            "status": mapq_status,
            "note": mapq_note,
        },
        "primary_result": {
            **primary,
            "te": PRIMARY_TE,
            "estimand": (
                "Fisher OR for AluSz overlap in 1 kb midpoint windows of merged "
                "anchors: Pol II ChIA-PET vs Hi-C (K562, GRCh38)"
            ),
            "block_bootstrap": boot,
            "desk_verdict": verdict,
            "full_span_sensitivity": full_span_sensitivity,
        },
        "permutation_null": perm,
        "exploratory_secondary": exploratory,
        "explicit_non_claims": [
            "No causal TE → loop mechanism",
            "Holdout untouched",
            "No C1 E/P or wet-lab GO",
            "AluJo / SVA_F are exploratory only",
            "Primary subfamily frozen as AluSz (not changed post-hoc)",
        ],
    }


def write_outputs(result: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    primary = result["primary_result"]
    verdict = primary["desk_verdict"]

    # TSV
    tsv_path = RESULTS / "primary_result_OR_CI.tsv"
    headers = [
        "te",
        "role",
        "n_pol2",
        "n_hic",
        "pol2_te_pos",
        "hic_te_pos",
        "pol2_rate",
        "hic_rate",
        "fisher_or",
        "fisher_p",
        "woolf_or",
        "woolf_ci95_lo",
        "woolf_ci95_hi",
        "boot_ci95_lo",
        "boot_ci95_hi",
        "desk_verdict",
        "mapq_status",
    ]
    boot = primary.get("block_bootstrap", {})
    row = [
        PRIMARY_TE,
        "PRIMARY",
        primary["n_pol2"],
        primary["n_hic"],
        primary["a_pol2_te_pos"],
        primary["c_hic_te_pos"],
        f"{primary['pol2_rate']:.6f}",
        f"{primary['hic_rate']:.6f}",
        f"{primary['fisher_or']:.6f}",
        f"{primary['fisher_p_two_sided']:.6e}",
        f"{primary['woolf_or']:.6f}",
        f"{primary['woolf_ci95_lo']:.6f}",
        f"{primary['woolf_ci95_hi']:.6f}",
        f"{boot.get('ci95_lo', float('nan')):.6f}",
        f"{boot.get('ci95_hi', float('nan')):.6f}",
        verdict["verdict"],
        result["mapq_mappability"]["status"],
    ]
    tsv_path.write_text("\t".join(headers) + "\n" + "\t".join(map(str, row)) + "\n", encoding="utf-8")

    json_path = RESULTS / "primary_result_OR_CI.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    perm_path = RESULTS / "permutation_null_summary.json"
    perm_path.write_text(
        json.dumps(
            {
                "script": result["script"],
                "te": PRIMARY_TE,
                "computed_at_utc": result["computed_at_utc"],
                **result["permutation_null"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    exp_path = RESULTS / "exploratory_secondary_TE.tsv"
    exp_lines = [
        "\t".join(
            [
                "te",
                "role",
                "n_pol2",
                "n_hic",
                "pol2_te_pos",
                "hic_te_pos",
                "pol2_rate",
                "hic_rate",
                "fisher_or",
                "woolf_ci95_lo",
                "woolf_ci95_hi",
                "note",
            ]
        )
    ]
    for r in result["exploratory_secondary"]:
        exp_lines.append(
            "\t".join(
                [
                    r["te"],
                    r["role"],
                    str(r["n_pol2"]),
                    str(r["n_hic"]),
                    str(r["a_pol2_te_pos"]),
                    str(r["c_hic_te_pos"]),
                    f"{r['pol2_rate']:.6f}",
                    f"{r['hic_rate']:.6f}",
                    f"{r['fisher_or']:.6f}",
                    f"{r['woolf_ci95_lo']:.6f}",
                    f"{r['woolf_ci95_hi']:.6f}",
                    r["note"].replace("\t", " "),
                ]
            )
        )
    exp_path.write_text("\n".join(exp_lines) + "\n", encoding="utf-8")

    md_path = RESULTS / "primary_result_OR_CI.md"
    md = f"""# Primary result — AluSz OR (T3 desk)

**Computed:** `{result['computed_at_utc']}`  
**Primary TE:** `{PRIMARY_TE}` (frozen; not post-hoc)  
**Desk verdict:** `{verdict['verdict']}`  
**MAPQ / mappability:** `{result['mapq_mappability']['status']}`

## Estimand

Fisher odds ratio for **AluSz** overlap in **fixed 1 kb midpoint windows** of
non-redundant merged anchors (≥1 kb) from Pol II ChIA-PET (`ENCFF511QFN`) vs
Hi-C (`ENCFF693XIL`), K562 / GRCh38.

Descriptive association in processed public call sets only — **not** causal.
Full-span overlap is reported only as width-confounded sensitivity.

## Anchor counts

| Arm | Raw unique | Merged ≥1 kb | 1 kb scoring windows |
|-----|------------|--------------|----------------------|
| Pol II ChIA-PET | {result['anchor_counts']['pol2_raw_unique']} | {result['anchor_counts']['pol2_merged_ge1kb']} | {result['anchor_counts']['pol2_scoring_windows_1kb']} |
| Hi-C | {result['anchor_counts']['hic_raw_unique']} | {result['anchor_counts']['hic_merged_ge1kb']} | {result['anchor_counts']['hic_scoring_windows_1kb']} |

## Primary AluSz statistics

| Metric | Value |
|--------|-------|
| Pol II AluSz+ / n | {primary['a_pol2_te_pos']} / {primary['n_pol2']} (rate {primary['pol2_rate']:.4f}) |
| Hi-C AluSz+ / n | {primary['c_hic_te_pos']} / {primary['n_hic']} (rate {primary['hic_rate']:.4f}) |
| Fisher OR | **{primary['fisher_or']:.4f}** |
| Fisher p (two-sided) | {primary['fisher_p_two_sided']:.4e} |
| Woolf OR 95% CI | {primary['woolf_ci95_lo']:.4f} – {primary['woolf_ci95_hi']:.4f} |
| Chrom block-bootstrap 95% CI | {boot.get('ci95_lo', float('nan')):.4f} – {boot.get('ci95_hi', float('nan')):.4f} (n_boot={boot.get('n_boot')}) |
| MCID support / fail | ≥{MCID_SUPPORT} / <{MCID_FAIL} |

**Verdict note:** {verdict['note']}

## Matched-null permutations

| Metric | Value |
|--------|-------|
| n_perm | {result['permutation_null']['n_perm']} |
| Matching | {result['permutation_null']['matching']} |
| Null OR mean / median | {result['permutation_null']['null_or_mean']:.4f} / {result['permutation_null']['null_or_median']:.4f} |
| Null OR 95% central | {result['permutation_null']['null_or_p025']:.4f} – {result['permutation_null']['null_or_p975']:.4f} |
| Empirical p (two-sided) | {result['permutation_null']['emp_p_two_sided']:.4g} |

## Full-span sensitivity (not primary)

| Metric | Value |
|--------|-------|
| Fisher OR (full merged span) | {primary.get('full_span_sensitivity', {}).get('fisher_or', float('nan')):.4f} |
| Note | {primary.get('full_span_sensitivity', {}).get('note', '')} |

## Limitations (honest)

1. `{result['mapq_mappability']['status']}` — {result['mapq_mappability']['note']}
2. GC matching not applied (no hg38 FASTA in worktree) — chromosome + width strata (widths equalized at 1 kb for primary).
3. Single cell type (K562); claim.md full REJECT needs MAPQ gate + replication.

## Exploratory secondary (NOT primary)

See `exploratory_secondary_TE.tsv` for SVA_F and AluJo. Do not promote to claim language.

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT wet-lab / oligo / C1 E–P authorization.
3. NOT holdout unseal.
4. NOT a multi-cell-type replicated claim.
"""
    md_path.write_text(md + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pol2", type=Path, default=DATA / "ENCFF511QFN.bedpe.gz")
    ap.add_argument("--hic", type=Path, default=DATA / "ENCFF693XIL.bedpe.gz")
    ap.add_argument("--rmsk", type=Path, default=DATA / "rmsk.txt.gz")
    ap.add_argument("--n-perm", type=int, default=N_PERM_DEFAULT)
    ap.add_argument("--n-boot", type=int, default=N_BOOT_DEFAULT)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--min-bp", type=int, default=MIN_ANCHOR_BP)
    args = ap.parse_args()

    for p, label in ((args.pol2, "Pol II bedpe"), (args.hic, "Hi-C bedpe"), (args.rmsk, "rmsk")):
        if not p.exists():
            print(f"Missing {label}: {p}", file=sys.stderr)
            return 1

    result = run_analysis(
        args.pol2,
        args.hic,
        args.rmsk,
        n_perm=args.n_perm,
        n_boot=args.n_boot,
        seed=args.seed,
        min_bp=args.min_bp,
    )
    write_outputs(result)
    primary = result["primary_result"]
    print(
        json.dumps(
            {
                "verdict": primary["desk_verdict"]["verdict"],
                "fisher_or": primary["fisher_or"],
                "woolf_ci95": [
                    primary["woolf_ci95_lo"],
                    primary["woolf_ci95_hi"],
                ],
                "n_pol2": primary["n_pol2"],
                "n_hic": primary["n_hic"],
                "n_perm": result["permutation_null"]["n_perm"],
                "mapq": result["mapq_mappability"]["status"],
            },
            indent=2,
        )
    )
    print(f"Wrote results under {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
