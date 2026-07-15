#!/usr/bin/env python3
"""exp_se_continuous_rank_dichotomization_check: within SE-constituent H3K27ac
peaks, does the SIZE of the enclosing super-enhancer (continuous) correlate
with Gnocchi constraint / R-loop overlap / G4 overlap -- testing whether the
5 binary-SE-vs-typical REJECTs this session were a dichotomization artifact
(MacCallum et al. 2002) rather than a genuine null.

Reuses every loader already written and tested this session
(gnocchi_constraint_se_vs_typical_analysis, rloop_se_vs_typical_analysis,
g4_se_vs_typical_analysis); the only new logic is find_enclosing_se and a
from-scratch Spearman correlation + permutation test.
"""

import bisect
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from g4_se_vs_typical_analysis import G4_FILES_HG19, load_and_liftover_g4  # noqa: E402
from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    load_gnocchi_windows,
    load_intervals,
    weighted_mean_z,
)
from liftover import load_chain_file  # noqa: E402
from rloop_se_vs_typical_analysis import load_rloop_peaks, overlap_fraction  # noqa: E402

H3K27AC_FILES = {
    "K562": ROOT / "data/input/h3k27ac_k562_grch38.json",
    "HepG2": ROOT / "data/input/h3k27ac_hepg2_grch38.json",
}
SE_FILES = {
    "K562": ROOT / "data/input/k562_super_enhancers_grch38.json",
    "HepG2": ROOT / "data/input/hepg2_super_enhancers_grch38.json",
}
CHAIN_FILE = ROOT / "data/input/hg19ToHg38.over.chain.gz"
RESULTS_FILE = ROOT / "experiments/exp_se_continuous_rank_dichotomization_check/results.json"

SEED = 42
N_PERMUTATIONS = 10000


def find_enclosing_se(chrom, start, end, se_by_chrom):
    """Returns (se_start, se_end) of the first SE interval overlapping
    [start,end), or None. Mirrors overlaps_any's bisect logic but returns the
    interval instead of a bool."""
    intervals = se_by_chrom.get(chrom)
    if not intervals:
        return None
    starts = [s for s, _ in intervals]
    i = bisect.bisect_right(starts, start) - 1
    i = max(i, 0)
    while i < len(intervals) and intervals[i][0] < end:
        s, e = intervals[i]
        if s < end and e > start:
            return (s, e)
        i += 1
    return None


def ranks_of(vals):
    """Average-rank transform (ties share the mean rank), same convention as
    mann_whitney_u."""
    indexed = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and vals[indexed[j]] == vals[indexed[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            r[indexed[k]] = avg_rank
        i = j
    return r


def pearson_on_ranks(rx, ry):
    n = len(rx)
    mean_rx, mean_ry = sum(rx) / n, sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    var_x = sum((v - mean_rx) ** 2 for v in rx)
    var_y = sum((v - mean_ry) ** 2 for v in ry)
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / math.sqrt(var_x * var_y)


def spearman(xs, ys):
    """Spearman rho = Pearson correlation of the rank-transformed vectors."""
    return pearson_on_ranks(ranks_of(xs), ranks_of(ys))


def permutation_test_correlation(xs, ys, n_perm, seed):
    """Ranks, means, and variances are computed ONCE (they are invariant
    under permutation -- shuffling only reorders values, not the multiset).
    Each permutation then costs a single O(n) dot product instead of
    recomputing means/variances/ranks from scratch (O(n log n) or worse) --
    the naive version would be ~10-20x slower at this n (K562: ~6000
    SE-constituent peaks x 10,000 permutations x up to 3 endpoints)."""
    rx = ranks_of(xs)
    ry = ranks_of(ys)
    n = len(rx)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    rx_c = [v - mean_rx for v in rx]
    ry_c = [v - mean_ry for v in ry]
    var_x = sum(v * v for v in rx_c)
    var_y = sum(v * v for v in ry_c)
    denom = math.sqrt(var_x * var_y) if var_x > 0 and var_y > 0 else 0.0

    def corr(ry_c_vec):
        if denom == 0.0:
            return 0.0
        return sum(rx_c[i] * ry_c_vec[i] for i in range(n)) / denom

    observed = corr(ry_c)
    rng = random.Random(seed)
    ry_c_shuffled = list(ry_c)
    count_extreme = 0
    for _ in range(n_perm):
        rng.shuffle(ry_c_shuffled)
        r = corr(ry_c_shuffled)
        if abs(r) >= abs(observed):
            count_extreme += 1
    p = (count_extreme + 1) / (n_perm + 1)
    return observed, p


def main():
    print("Loading Gnocchi constraint windows...")
    gnocchi = load_gnocchi_windows()

    print("Loading R-loop peaks (K562 only)...")
    rloop_k562 = load_rloop_peaks()

    print("Loading liftover chains for G4...")
    with open(CHAIN_FILE, "rb") as f:
        chains = load_chain_file(f.read())
    g4_by_cell = {}
    for cell in ("K562", "HepG2"):
        g4_grch38, _, _ = load_and_liftover_g4(G4_FILES_HG19[cell], chains)
        g4_by_cell[cell] = g4_grch38

    all_results = {}
    for cell in ("K562", "HepG2"):
        print(f"\n=== {cell} ===")
        h3k27ac = load_intervals(H3K27AC_FILES[cell], key="peaks")
        se_intervals = load_intervals(SE_FILES[cell], key="super_enhancers")

        se_length = []
        gnocchi_z = []
        rloop_frac = []
        g4_frac = []

        for chrom, peaks in h3k27ac.items():
            for start, end in peaks:
                se = find_enclosing_se(chrom, start, end, se_intervals)
                if se is None:
                    continue
                s_start, s_end = se
                se_length.append(s_end - s_start)
                gnocchi_z.append(weighted_mean_z(chrom, start, end, gnocchi))
                if cell == "K562":
                    rloop_frac.append(overlap_fraction(chrom, start, end, rloop_k562))
                g4_frac.append(overlap_fraction(chrom, start, end, g4_by_cell[cell]))

        print(f"  SE-constituent peaks: {len(se_length)}")

        cell_results = {"n_se_constituent": len(se_length)}

        # Gnocchi: drop pairs with missing (None) values
        pairs = [(a, b) for a, b in zip(se_length, gnocchi_z) if b is not None]
        if pairs:
            xs, ys = zip(*pairs)
            rho, p = permutation_test_correlation(list(xs), list(ys), N_PERMUTATIONS, SEED)
            print(f"  SE-size vs Gnocchi-Z: n={len(pairs)}, rho={rho:.4f}, p={p:.4f}")
            cell_results["gnocchi"] = {
                "n": len(pairs),
                "spearman_rho": rho,
                "p_value_permutation": p,
            }

        if cell == "K562":
            rho, p = permutation_test_correlation(se_length, rloop_frac, N_PERMUTATIONS, SEED)
            print(f"  SE-size vs R-loop-overlap: n={len(se_length)}, rho={rho:.4f}, p={p:.4f}")
            cell_results["rloop"] = {
                "n": len(se_length),
                "spearman_rho": rho,
                "p_value_permutation": p,
            }

        rho, p = permutation_test_correlation(se_length, g4_frac, N_PERMUTATIONS, SEED)
        print(f"  SE-size vs G4-overlap: n={len(se_length)}, rho={rho:.4f}, p={p:.4f}")
        cell_results["g4"] = {"n": len(se_length), "spearman_rho": rho, "p_value_permutation": p}

        all_results[cell] = cell_results

    all_results["mcid"] = "abs(spearman_rho) >= 0.2 AND p_value_permutation < 0.05"
    all_results["n_permutations"] = N_PERMUTATIONS

    print("\n" + json.dumps(all_results, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
