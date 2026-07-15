#!/usr/bin/env python3
"""exp_g4_se_vs_typical_enhancer: compares G-quadruplex (BG4 ChIP-seq) overlap
between H3K27ac enhancer peaks inside a super-enhancer ("SE-constituent") vs.
length-matched H3K27ac peaks outside any super-enhancer ("typical"), in K562
AND HepG2.

G4 data: GSE145090 (Spiegel/Cuesta/Adhikari et al. 2021, Genome Biology,
PMC8063395), official GEO-deposited processed BED files, hg19 -- lifted to
GRCh38 via this project's own liftover.py before analysis.

Reuses overlap_fraction/merge_intervals-based logic from
rloop_se_vs_typical_analysis.py (same pattern, same defensive clamp against
double-counting from overlapping input peaks).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    load_intervals,
    mann_whitney_u,
    overlaps_any,
    paired_permutation_test,
)
from liftover import load_chain_file, lift_interval  # noqa: E402
from llps_promoter_vs_se_analysis import merge_intervals  # noqa: E402
from rloop_se_vs_typical_analysis import greedy_match_full, median, overlap_fraction  # noqa: E402

G4_FILES_HG19 = {
    "K562": ROOT / "data/input/g4_k562_GSE145090_5of8.bed.gz",
    "HepG2": ROOT / "data/input/g4_hepg2_GSE145090_6of9.bed.gz",
}
H3K27AC_FILES = {
    "K562": ROOT / "data/input/h3k27ac_k562_grch38.json",
    "HepG2": ROOT / "data/input/h3k27ac_hepg2_grch38.json",
}
SE_FILES = {
    "K562": ROOT / "data/input/k562_super_enhancers_grch38.json",
    "HepG2": ROOT / "data/input/hepg2_super_enhancers_grch38.json",
}
CHAIN_FILE = ROOT / "data/input/hg19ToHg38.over.chain.gz"
CHAIN_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz"
RESULTS_FILE = ROOT / "experiments/exp_g4_se_vs_typical_enhancer/results.json"

MATCH_SEED = 42
N_PERMUTATIONS = 10000


def load_and_liftover_g4(path, chains):
    import gzip

    by_chrom = {}
    n_total = 0
    n_failed = 0
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            chrom, start, end = cols[0], int(cols[1]), int(cols[2])
            n_total += 1
            lifted = lift_interval(chains, chrom, start, end)
            if lifted is None:
                n_failed += 1
                continue
            lchrom, lstart, lend = lifted
            by_chrom.setdefault(lchrom, []).append((lstart, lend))
    merged, _ = merge_intervals(by_chrom)
    return merged, n_total, n_failed


def main():
    if not CHAIN_FILE.exists():
        print(f"Fetching UCSC hg19->GRCh38 chain file: {CHAIN_URL}")
        import urllib.request

        req = urllib.request.Request(CHAIN_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            chain_bytes = resp.read()
        CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHAIN_FILE, "wb") as f:
            f.write(chain_bytes)
    else:
        with open(CHAIN_FILE, "rb") as f:
            chain_bytes = f.read()
    chains = load_chain_file(chain_bytes)
    print(f"  Loaded liftover chains for {len(chains)} chromosomes")

    all_results = {}
    p_values_perm = []
    cell_order = []

    for cell in ("K562", "HepG2"):
        print(f"\n=== {cell} ===")
        g4_grch38, n_total, n_failed = load_and_liftover_g4(G4_FILES_HG19[cell], chains)
        n_lifted = sum(len(v) for v in g4_grch38.values())
        print(f"  G4 peaks: {n_total} hg19 -> {n_lifted} GRCh38 ({n_failed} failed to lift)")

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
        print(f"  SE-constituent: {len(se_constituent)}, typical: {len(typical)}")

        pairs = greedy_match_full(se_constituent, typical, MATCH_SEED)
        print(f"  Length-matched pairs: {len(pairs)}")

        pairs_frac = []
        for (s_start, s_end, s_chrom), (t_start, t_end, t_chrom) in pairs:
            f_se = overlap_fraction(s_chrom, s_start, s_end, g4_grch38)
            f_typ = overlap_fraction(t_chrom, t_start, t_end, g4_grch38)
            pairs_frac.append((f_se, f_typ))

        frac_se_all = [a for a, b in pairs_frac]
        frac_typ_all = [b for a, b in pairs_frac]

        u, p_mwu, delta = mann_whitney_u(frac_se_all, frac_typ_all)
        observed_diff, p_perm = paired_permutation_test(pairs_frac, N_PERMUTATIONS, MATCH_SEED)

        n_se_with_overlap = sum(1 for f in frac_se_all if f > 0)
        n_typ_with_overlap = sum(1 for f in frac_typ_all if f > 0)

        print(f"  median_frac_SE={median(frac_se_all)}, median_frac_typical={median(frac_typ_all)}")
        print(f"  Mann-Whitney p={p_mwu}, Cliff's delta={delta}")
        print(f"  Paired permutation: observed diff={observed_diff}, p={p_perm}")

        all_results[cell] = {
            "n_g4_peaks_hg19": n_total,
            "n_g4_peaks_grch38_lifted": n_lifted,
            "n_g4_failed_liftover": n_failed,
            "n_se_constituent_total": len(se_constituent),
            "n_typical_total": len(typical),
            "n_matched_pairs": len(pairs),
            "n_se_with_any_g4_overlap": n_se_with_overlap,
            "n_typical_with_any_g4_overlap": n_typ_with_overlap,
            "pct_se_with_overlap": round(100 * n_se_with_overlap / len(pairs), 2)
            if pairs
            else None,
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
        }
        p_values_perm.append(p_perm)
        cell_order.append(cell)

    all_results["data_source"] = (
        "GSE145090 (Spiegel/Cuesta/Adhikari et al 2021, Genome Biology, PMC8063395), "
        "hg19 lifted to GRCh38"
    )
    all_results["mcid"] = "abs(cliffs_delta) >= 0.2 AND p_value_permutation < 0.05"
    all_results["match_seed"] = MATCH_SEED

    print("\n" + json.dumps(all_results, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
