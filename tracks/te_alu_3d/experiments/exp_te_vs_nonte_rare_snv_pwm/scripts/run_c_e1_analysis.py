#!/usr/bin/env python3
"""C-E1 primary: umap-quartile match TE vs non-TE, then |PWM Δ|, Cliff's δ.

Order locked by claim/controls: match BEFORE PWM attach.
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyBigWig

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT.parents[1] / "pilot_scaffold"))

from c_e1_lib import (  # noqa: E402
    KILL_ABS_DELTA,
    RNG_SEED,
    SUPPORT_ABS_DELTA,
    UMAP_FLANK,
    cliffs_delta,
    group_by_key,
    match_1to1,
    quantile_bins,
    verdict_delta,
)
from ctcf_pwm_scorer import ctcf_pwm_disruption  # noqa: E402

INP = ROOT / "data" / "input"
RES = ROOT / "results"
PANEL = INP / "rare_snv_panel_chr11_nonhbb.jsonl"
UMAP = INP / "k100.Umap.MultiTrackMappability.bw"
CTCF_PEAKS = INP / "ctcf_HUDEP2_peaks.bed"
# Prefer symlink target if present
PILOT_CTCF = ROOT.parents[1] / "pilot_scaffold" / "data" / "ctcf_HUDEP2_peaks.bed"


def load_panel(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def mean_umap_at(bw, chrom: str, pos1: int) -> float:
    chroms = bw.chroms() or {}
    if chrom not in chroms:
        return 0.0
    clen = chroms[chrom]
    s = max(0, pos1 - 1 - UMAP_FLANK)
    e = min(clen, pos1 + UMAP_FLANK)
    if e <= s:
        return 0.0
    try:
        m = bw.stats(chrom, s, e, type="mean")[0]
    except RuntimeError:
        m = None
    return float(m) if m is not None else 0.0


class SeqTileCache:
    """Fetch UCSC hg38 sequence in 2 kb tiles; reuse across nearby SNVs."""

    def __init__(self, tile: int = 2000):
        self.tile = tile
        self._cache: dict[tuple[str, int], tuple[int, str]] = {}

    def _fetch(self, chrom: str, start0: int, end0: int) -> str:
        url = (
            "https://api.genome.ucsc.edu/getData/sequence"
            f"?genome=hg38;chrom={chrom};start={start0};end={end0}"
        )
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    data = json.load(r)
                seq = data.get("dna") or data.get("sequence")
                if not seq:
                    raise RuntimeError(f"no DNA {chrom}:{start0}-{end0}")
                return seq.upper()
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError("unreachable")

    def window(self, chrom: str, pos1: int, half: int = 40) -> tuple[int, int, str]:
        start0 = max(0, pos1 - 1 - half)
        end0 = pos1 - 1 + half
        tile0 = (start0 // self.tile) * self.tile
        key = (chrom, tile0)
        if key not in self._cache:
            # fetch two tiles to cover boundary straddles
            seq = self._fetch(chrom, tile0, tile0 + 2 * self.tile)
            self._cache[key] = (tile0, seq)
            time.sleep(0.02)
        base, seq = self._cache[key]
        rel_s = start0 - base
        rel_e = end0 - base
        if rel_s < 0 or rel_e > len(seq):
            # hard miss — direct fetch
            direct = self._fetch(chrom, start0, end0)
            return start0, end0, direct
        return start0, end0, seq[rel_s:rel_e]


def score_pwm(
    chrom: str,
    pos: int,
    ref: str,
    alt: str,
    peaks_path: Path,
    cache: SeqTileCache,
) -> dict:
    start0, end0, seq = cache.window(chrom, pos, half=40)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".fa", delete=False, encoding="utf-8"
    ) as fh:
        fh.write(f">{chrom}:{start0 + 1}-{end0}\n{seq}\n")
        fa = Path(fh.name)
    try:
        return ctcf_pwm_disruption(
            chrom, pos, ref, alt, fasta_path=fa, peaks_path=peaks_path
        )
    finally:
        fa.unlink(missing_ok=True)


def bootstrap_delta_ci(
    te: list[float], non: list[float], n_boot: int = 2000, seed: int = RNG_SEED
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n1, n2 = len(te), len(non)
    if n1 < 2 or n2 < 2:
        return float("nan"), float("nan")
    te_a = np.asarray(te, dtype=float)
    non_a = np.asarray(non, dtype=float)
    boots = []
    for _ in range(n_boot):
        s1 = te_a[rng.integers(0, n1, size=n1)]
        s2 = non_a[rng.integers(0, n2, size=n2)]
        boots.append(cliffs_delta(s1, s2))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(lo), float(hi)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    if not PANEL.exists():
        print("MISSING panel — run fetch_c_e1_panel.py first", flush=True)
        return 2
    if not UMAP.exists():
        print("BLOCKED_DATA: umap missing", flush=True)
        return 2

    peaks_path = CTCF_PEAKS if CTCF_PEAKS.exists() else PILOT_CTCF
    rows = load_panel(PANEL)
    print(f"panel n={len(rows)}", flush=True)

    bw = pyBigWig.open(str(UMAP))
    for r in rows:
        r["umap"] = mean_umap_at(bw, r["chrom"], r["pos"])
    bw.close()

    te_rows = [r for r in rows if r["te_overlap"]]
    non_rows = [r for r in rows if not r["te_overlap"]]
    print(f"TE={len(te_rows)} nonTE={len(non_rows)}", flush=True)

    all_u = np.array([r["umap"] for r in rows], dtype=float)
    bins = quantile_bins(all_u, 4)
    for r, b in zip(rows, bins):
        r["umap_q"] = int(b)

    # MATCH LOCK before PWM
    te_ids = [r["variant_id"] for r in te_rows]
    te_keys = [(r["chrom"], r["umap_q"]) for r in te_rows]
    non_ids = [r["variant_id"] for r in non_rows]
    non_keys = [(r["chrom"], r["umap_q"]) for r in non_rows]
    pool = group_by_key(non_ids, non_keys)
    exposed = list(zip(te_ids, te_keys))
    pairs = match_1to1(exposed, pool, seed=RNG_SEED)

    by_id = {r["variant_id"]: r for r in rows}
    matched: list[tuple[dict, dict]] = []
    for te_id, non_id in pairs.items():
        if non_id is None:
            continue
        matched.append((by_id[te_id], by_id[non_id]))

    match_lock = {
        "seed": RNG_SEED,
        "covariates": ["chrom", "umap_q4"],
        "n_te": len(te_rows),
        "n_non_te_pool": len(non_rows),
        "n_matched_pairs": len(matched),
        "n_unmatched_te": sum(1 for v in pairs.values() if v is None),
        "umap_flank_bp": UMAP_FLANK,
        "locked_before_pwm": True,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
    }
    (RES / "matching_lock.json").write_text(
        json.dumps(match_lock, indent=2) + "\n", encoding="utf-8"
    )
    print(f"matched pairs={len(matched)}", flush=True)

    te_scores: list[float] = []
    non_scores: list[float] = []
    scored_rows: list[dict] = []
    cache = SeqTileCache(tile=2000)
    for i, (te, non) in enumerate(matched):
        if i and i % 100 == 0:
            print(f"  scored {i}/{len(matched)} tiles={len(cache._cache)}", flush=True)
        try:
            st = score_pwm(
                te["chrom"], te["pos"], te["ref"], te["alt"], peaks_path, cache
            )
            sn = score_pwm(
                non["chrom"], non["pos"], non["ref"], non["alt"], peaks_path, cache
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  skip pair {te['variant_id']}: {exc}", flush=True)
            time.sleep(0.5)
            continue
        d_te = abs(float(st.get("delta_logodds") or 0.0))
        d_non = abs(float(sn.get("delta_logodds") or 0.0))
        te_scores.append(d_te)
        non_scores.append(d_non)
        scored_rows.append(
            {
                "te_id": te["variant_id"],
                "non_id": non["variant_id"],
                "umap_q": te["umap_q"],
                "te_umap": te["umap"],
                "non_umap": non["umap"],
                "te_abs_pwm_delta": d_te,
                "non_abs_pwm_delta": d_non,
                "te_name": te.get("te_name"),
            }
        )

    delta = cliffs_delta(te_scores, non_scores)
    lo, hi = bootstrap_delta_ci(te_scores, non_scores)
    verd = verdict_delta(delta)

    primary = {
        "candidate_id": "C-E1",
        "estimand": "Cliffs_delta_TE_minus_nonTE_on_abs_ctcf_pwm_delta_v1.1",
        "scorer": "ctcf_pwm_delta_v1.1",
        "n_scored_pairs": len(te_scores),
        "mean_abs_pwm_te": float(np.mean(te_scores)) if te_scores else None,
        "mean_abs_pwm_non": float(np.mean(non_scores)) if non_scores else None,
        "median_abs_pwm_te": float(np.median(te_scores)) if te_scores else None,
        "median_abs_pwm_non": float(np.median(non_scores)) if non_scores else None,
        "cliffs_delta": delta,
        "cliffs_delta_boot_ci95": [lo, hi],
        "mcid_support": SUPPORT_ABS_DELTA,
        "mcid_kill": KILL_ABS_DELTA,
        "verdict": verd,
        "scope": "chr11 CTCF-neighborhood rare SNVs; HBB+HO excluded; umap-q matched",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
    }
    (RES / "primary_result_cliffs_delta.json").write_text(
        json.dumps(primary, indent=2) + "\n", encoding="utf-8"
    )
    (RES / "matched_scored_pairs.jsonl").write_text(
        "\n".join(json.dumps(x, separators=(",", ":")) for x in scored_rows) + ("\n" if scored_rows else ""),
        encoding="utf-8",
    )
    print(json.dumps(primary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
