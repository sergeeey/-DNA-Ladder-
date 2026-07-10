#!/usr/bin/env python3
"""exp_rloop_se_vs_typical_enhancer: compares R-loop (DNA:RNA hybrid) overlap
between H3K27ac enhancer peaks inside a super-enhancer ("SE-constituent") vs.
length-matched H3K27ac peaks outside any super-enhancer ("typical"), in K562.

R-loop data: RLBase-processed DRIP-seq (SRX1070682, Sanz/Chedin 2016, hg38),
downloaded from the public s3://rlbase-data/ bucket.

Reuses the exact classification and length-matching logic from
gnocchi_constraint_se_vs_typical_analysis.py; the only new piece is
overlap_fraction (region-vs-R-loop-peak bp overlap / region length), which
plays the same role weighted_mean_z played for Gnocchi Z-scores.
"""

import bisect
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    load_intervals,
    mann_whitney_u,
    overlaps_any,
    paired_permutation_test,
)
from llps_promoter_vs_se_analysis import merge_intervals  # noqa: E402

H3K27AC_FILE = ROOT / "data/input/h3k27ac_k562_grch38.json"
SE_FILE = ROOT / "data/input/k562_super_enhancers_grch38.json"
RLOOP_FILE = ROOT / "data/input/rloop_k562_SRX1070682_hg38.broadPeak"
RESULTS_FILE = ROOT / "experiments/exp_rloop_se_vs_typical_enhancer/results.json"

MATCH_SEED = 42
N_PERMUTATIONS = 10000
VALID_CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY"}


def load_rloop_peaks():
    by_chrom = defaultdict(list)
    with open(RLOOP_FILE) as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            chrom, start, end = cols[0], int(cols[1]), int(cols[2])
            if chrom not in VALID_CHROMS:
                continue
            by_chrom[chrom].append((start, end))
    # merge overlapping peaks first -- overlap_fraction sums per-peak overlap
    # without deduplication, so unmerged overlapping input peaks would double-count
    merged, _total_bp = merge_intervals(dict(by_chrom))
    return merged


def overlap_fraction(chrom, start, end, rloop_by_chrom):
    """Assumes rloop_by_chrom intervals are already non-overlapping per
    chromosome (load_rloop_peaks guarantees this via merge_intervals). The
    final clamp to region_len is a defensive backstop, not the primary
    correctness mechanism -- it prevents a >1.0 fraction if that precondition
    is ever violated by a future caller, but does not by itself produce a
    correct value for genuinely overlapping input (that requires merging)."""
    intervals = rloop_by_chrom.get(chrom)
    region_len = end - start
    if not intervals or region_len <= 0:
        return 0.0
    starts = [s for s, _ in intervals]
    i = bisect.bisect_right(starts, start) - 1
    i = max(i, 0)
    total_overlap = 0
    while i < len(intervals) and intervals[i][0] < end:
        s, e = intervals[i]
        ov_start = max(start, s)
        ov_end = min(end, e)
        if ov_end > ov_start:
            total_overlap += ov_end - ov_start
        i += 1
    return min(total_overlap, region_len) / region_len


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def greedy_match_full(se_list, typ_list, seed):
    import math

    typ_sorted = sorted(typ_list, key=lambda p: math.log10(p[1] - p[0]))
    typ_lengths = [math.log10(p[1] - p[0]) for p in typ_sorted]
    used = [False] * len(typ_sorted)
    rng = random.Random(seed)
    se_shuffled = list(se_list)
    rng.shuffle(se_shuffled)
    pairs = []
    for se in se_shuffled:
        target = math.log10(se[1] - se[0])
        i = bisect.bisect_left(typ_lengths, target)
        best_j, best_dist = None, None
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(typ_sorted) and not used[j]:
                d = abs(typ_lengths[j] - target)
                if best_dist is None or d < best_dist:
                    best_dist, best_j = d, j
        if best_j is None:
            for j in range(len(typ_sorted)):
                if not used[j]:
                    d = abs(typ_lengths[j] - target)
                    if best_dist is None or d < best_dist:
                        best_dist, best_j = d, j
        if best_j is not None:
            used[best_j] = True
            pairs.append((se, typ_sorted[best_j]))
    return pairs


def main():
    print("Loading R-loop peaks (SRX1070682, K562 DRIP-seq, hg38)...")
    rloop = load_rloop_peaks()
    n_rloop = sum(len(v) for v in rloop.values())
    print(f"  {n_rloop} R-loop peaks across {len(rloop)} chromosomes")

    print("Loading H3K27ac peaks and super-enhancers (K562)...")
    h3k27ac = load_intervals(H3K27AC_FILE, key="peaks")
    se_intervals = load_intervals(SE_FILE, key="super_enhancers")

    se_constituent = []
    typical = []
    for chrom, peaks in h3k27ac.items():
        for start, end in peaks:
            if overlaps_any(chrom, start, end, se_intervals):
                se_constituent.append((start, end, chrom))
            else:
                typical.append((start, end, chrom))

    print(f"  H3K27ac peaks: {sum(len(v) for v in h3k27ac.values())} total")
    print(f"  SE-constituent: {len(se_constituent)}, typical: {len(typical)}")

    pairs = greedy_match_full(se_constituent, typical, MATCH_SEED)
    print(f"  Length-matched pairs: {len(pairs)}")

    pairs_frac = []
    for (s_start, s_end, s_chrom), (t_start, t_end, t_chrom) in pairs:
        f_se = overlap_fraction(s_chrom, s_start, s_end, rloop)
        f_typ = overlap_fraction(t_chrom, t_start, t_end, rloop)
        pairs_frac.append((f_se, f_typ))

    frac_se_all = [a for a, b in pairs_frac]
    frac_typ_all = [b for a, b in pairs_frac]

    u, p_mwu, delta = mann_whitney_u(frac_se_all, frac_typ_all)
    observed_diff, p_perm = paired_permutation_test(pairs_frac, N_PERMUTATIONS, MATCH_SEED)

    n_se_with_overlap = sum(1 for f in frac_se_all if f > 0)
    n_typ_with_overlap = sum(1 for f in frac_typ_all if f > 0)

    result = {
        "data_source": "RLBase SRX1070682 (Sanz/Chedin 2016 K562 DRIP-seq, PMID 27373332), hg38",
        "n_se_constituent_total": len(se_constituent),
        "n_typical_total": len(typical),
        "n_matched_pairs": len(pairs),
        "n_se_with_any_rloop_overlap": n_se_with_overlap,
        "n_typical_with_any_rloop_overlap": n_typ_with_overlap,
        "pct_se_with_overlap": round(100 * n_se_with_overlap / len(pairs), 2) if pairs else None,
        "pct_typical_with_overlap": round(100 * n_typ_with_overlap / len(pairs), 2)
        if pairs
        else None,
        "median_overlap_fraction_se": median(frac_se_all),
        "median_overlap_fraction_typical": median(frac_typ_all),
        "mann_whitney_U": u,
        "p_value_mwu": p_mwu,
        "cliffs_delta": delta,
        "paired_permutation_observed_mean_diff": observed_diff,
        "p_value_permutation": p_perm,
        "n_permutations": N_PERMUTATIONS,
        "mcid": "abs(cliffs_delta) >= 0.2 AND p_value_permutation < 0.05",
        "match_seed": MATCH_SEED,
    }
    print("\n" + json.dumps(result, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
