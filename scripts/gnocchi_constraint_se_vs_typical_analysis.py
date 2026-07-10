#!/usr/bin/env python3
"""exp_gnocchi_constraint_se_vs_typical_enhancer: compares germline mutational
constraint (Gnocchi Z-score, Chen/Francioli/Karczewski 2023, gnomAD v3.1.2,
GRCh38) between H3K27ac enhancer peaks that fall inside a super-enhancer
("SE-constituent") vs. length-matched H3K27ac peaks outside any super-enhancer
("typical"), per cell line (K562, HepG2).

Unit of analysis is the ENHANCER REGION, not the 1kb window -- each peak gets
one length-weighted-mean Z score across all overlapping 1kb windows, avoiding
the pseudoreplication of pooling correlated adjacent windows (methodological
point raised in the external critique this experiment responds to).

Significance is assessed via a paired-permutation test on the matched pairs
(primary) plus Mann-Whitney U / Cliff's delta on the pooled matched groups
(secondary, for comparability with prior experiments in this project).
"""

import bisect
import gzip
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GNOCCHI_FILE = ROOT / "data/input/gnocchi_constraint_z_genome_1kb_qc.txt.gz"
H3K27AC_FILES = {
    "K562": ROOT / "data/input/h3k27ac_k562_grch38.json",
    "HepG2": ROOT / "data/input/h3k27ac_hepg2_grch38.json",
}
SE_FILES = {
    "K562": ROOT / "data/input/k562_super_enhancers_grch38.json",
    "HepG2": ROOT / "data/input/hepg2_super_enhancers_grch38.json",
}
RESULTS_FILE = ROOT / "experiments/exp_gnocchi_constraint_se_vs_typical_enhancer/results.json"

MATCH_SEED = 42
N_PERMUTATIONS = 10000


def load_gnocchi_windows():
    """chrom -> (sorted starts list, ends list, z list) for QC-passed 1kb windows."""
    by_chrom = defaultdict(list)
    with gzip.open(GNOCCHI_FILE, "rt") as f:
        header = f.readline().strip().split("\t")
        idx = {name: i for i, name in enumerate(header)}
        for line in f:
            cols = line.rstrip("\n").split("\t")
            chrom = cols[idx["chrom"]]
            start = int(cols[idx["start"]])
            end = int(cols[idx["end"]])
            z = cols[idx["z"]]
            if z == "NA" or z == "":
                continue
            by_chrom[f"chr{chrom}" if not chrom.startswith("chr") else chrom].append(
                (start, end, float(z))
            )
    out = {}
    for chrom, windows in by_chrom.items():
        windows.sort()
        out[chrom] = (
            [w[0] for w in windows],
            [w[1] for w in windows],
            [w[2] for w in windows],
        )
    return out


def load_intervals(path, key="peaks"):
    with open(path) as f:
        data = json.load(f)
    by_chrom = defaultdict(list)
    for p in data[key]:
        by_chrom[p["chrom"]].append((p["start"], p["end"]))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return dict(by_chrom)


def overlaps_any(chrom, start, end, by_chrom):
    intervals = by_chrom.get(chrom)
    if not intervals:
        return False
    starts = [s for s, _ in intervals]
    i = bisect.bisect_right(starts, start) - 1
    i = max(i, 0)
    while i < len(intervals) and intervals[i][0] < end:
        s, e = intervals[i]
        if s < end and e > start:
            return True
        i += 1
    return False


def weighted_mean_z(chrom, start, end, gnocchi_by_chrom):
    if chrom not in gnocchi_by_chrom:
        return None
    starts, ends, zs = gnocchi_by_chrom[chrom]
    i = bisect.bisect_right(starts, start) - 1
    i = max(i, 0)
    total_weight = 0
    weighted_sum = 0.0
    while i < len(starts) and starts[i] < end:
        ov_start = max(start, starts[i])
        ov_end = min(end, ends[i])
        if ov_end > ov_start:
            w = ov_end - ov_start
            weighted_sum += w * zs[i]
            total_weight += w
        i += 1
    if total_weight == 0:
        return None
    return weighted_sum / total_weight


def mann_whitney_u(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return float("nan"), float("nan"), float("nan")
    combined = [(d, 0) for d in group1] + [(d, 1) for d in group2]
    combined.sort(key=lambda x: x[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    cliffs_delta = (2 * u1 / (n1 * n2)) - 1
    if sigma == 0:
        return u1, float("nan"), cliffs_delta
    z = (u1 - mu) / sigma
    p = math.erfc(abs(z) / math.sqrt(2))
    return u1, p, cliffs_delta


def paired_permutation_test(pairs_z, n_perm, seed):
    """pairs_z: list of (z_se, z_typical). Test statistic = mean(z_se - z_typical).
    Null: randomly swap which member of each pair is 'SE' vs 'typical'."""
    diffs = [a - b for a, b in pairs_z]
    observed = sum(diffs) / len(diffs)
    rng = random.Random(seed)
    count_extreme = 0
    for _ in range(n_perm):
        perm_sum = 0.0
        for a, b in pairs_z:
            if rng.random() < 0.5:
                perm_sum += a - b
            else:
                perm_sum += b - a
        perm_mean = perm_sum / len(pairs_z)
        if abs(perm_mean) >= abs(observed):
            count_extreme += 1
    p = (count_extreme + 1) / (n_perm + 1)
    return observed, p


def benjamini_hochberg(p_values):
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * n
    prev = 1.0
    for rank, (idx, p) in enumerate(reversed(indexed), start=1):
        bh_rank = n - rank + 1
        val = min(prev, p * n / bh_rank)
        adjusted[idx] = val
        prev = val
    return adjusted


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def main():
    print("Loading Gnocchi 1kb constraint windows (1,984,900 rows expected)...")
    gnocchi = load_gnocchi_windows()
    n_windows = sum(len(v[0]) for v in gnocchi.values())
    print(f"  Loaded {n_windows} QC-passed windows across {len(gnocchi)} chromosomes")

    all_results = {}
    p_values_permutation = []
    p_values_mwu = []
    cell_order = []

    for cell in ("K562", "HepG2"):
        print(f"\n=== {cell} ===")
        h3k27ac = load_intervals(H3K27AC_FILES[cell], key="peaks")
        se_intervals = load_intervals(SE_FILES[cell], key="super_enhancers")

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

        se_full = se_constituent
        typ_full = typical

        # do matching on (start,end,chrom) tuples directly by reusing length only
        def greedy_match_full(se_list, typ_list, seed):
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

        pairs = greedy_match_full(se_full, typ_full, MATCH_SEED)
        print(f"  Length-matched pairs: {len(pairs)}")

        pairs_z = []
        n_missing = 0
        for (s_start, s_end, s_chrom), (t_start, t_end, t_chrom) in pairs:
            z_se = weighted_mean_z(s_chrom, s_start, s_end, gnocchi)
            z_typ = weighted_mean_z(t_chrom, t_start, t_end, gnocchi)
            if z_se is None or z_typ is None:
                n_missing += 1
                continue
            pairs_z.append((z_se, z_typ))

        print(
            f"  Pairs with valid Gnocchi coverage: {len(pairs_z)} ({n_missing} dropped, no QC-passed window overlap)"
        )

        z_se_all = [a for a, b in pairs_z]
        z_typ_all = [b for a, b in pairs_z]

        u, p_mwu, delta = mann_whitney_u(z_se_all, z_typ_all)
        observed_diff, p_perm = paired_permutation_test(pairs_z, N_PERMUTATIONS, MATCH_SEED)

        se_lengths = [e - s for s, e, c in se_full]
        typ_matched_lengths = [t[1] - t[0] for _, t in pairs]

        print(f"  n_pairs={len(pairs_z)}")
        print(f"  median_z_SE={median(z_se_all)}, median_z_typical={median(z_typ_all)}")
        print(f"  Mann-Whitney U={u}, p={p_mwu}, Cliff's delta={delta}")
        print(
            f"  Paired permutation: observed mean(z_SE - z_typical)={observed_diff}, p={p_perm} ({N_PERMUTATIONS} perms)"
        )

        all_results[cell] = {
            "n_se_constituent_total": len(se_constituent),
            "n_typical_total": len(typical),
            "n_matched_pairs": len(pairs),
            "n_pairs_with_gnocchi_coverage": len(pairs_z),
            "n_pairs_dropped_no_coverage": n_missing,
            "median_z_se": median(z_se_all),
            "median_z_typical": median(z_typ_all),
            "mann_whitney_U": u,
            "p_value_mwu": p_mwu,
            "cliffs_delta": delta,
            "paired_permutation_observed_mean_diff": observed_diff,
            "p_value_permutation": p_perm,
            "n_permutations": N_PERMUTATIONS,
            "median_length_se_constituent_bp": median(se_lengths),
            "median_length_typical_matched_bp": median(typ_matched_lengths),
        }
        p_values_permutation.append(p_perm)
        p_values_mwu.append(p_mwu)
        cell_order.append(cell)

    p_adj_perm = benjamini_hochberg(p_values_permutation)
    p_adj_mwu = benjamini_hochberg(p_values_mwu)
    for i, cell in enumerate(cell_order):
        all_results[cell]["p_value_permutation_bh"] = p_adj_perm[i]
        all_results[cell]["p_value_mwu_bh"] = p_adj_mwu[i]

    all_results["mcid"] = "abs(cliffs_delta) >= 0.2 AND p_value_permutation_bh < 0.05"
    all_results["match_seed"] = MATCH_SEED
    all_results["data_source"] = (
        "Gnocchi (Chen/Francioli/Karczewski 2023, Nature, DOI 10.1038/s41586-023-06045-0), gnomAD v3.1.2, GRCh38"
    )

    print("\n" + json.dumps(all_results, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
