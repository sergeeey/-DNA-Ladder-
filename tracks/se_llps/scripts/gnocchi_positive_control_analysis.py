#!/usr/bin/env python3
"""Positive control for the Gnocchi pipeline (scripts/gnocchi_constraint_se_vs_typical_analysis.py):
does the pipeline detect a KNOWN, large, well-documented effect -- protein-coding CDS exons
under much stronger germline constraint than random intergenic regions -- using the exact
same weighted_mean_z / matching / permutation-test code as the SE-vs-typical-enhancer
experiment that returned REJECT?

If this control also returns null/tiny-effect, the REJECT is suspect (broken pipeline).
If this control shows the expected large, correctly-signed, significant effect, the
REJECT is trustworthy (the pipeline can detect real signal; SE-vs-typical genuinely has none).

Comparator: sampled CDS exons (GENCODE v47 basic, GRCh38) vs length-matched random regions
sampled at least 100kb away from any GENCODE TSS (crude intergenic/neutral proxy, using
data already on disk -- data/input/gencode_tss_grch38.json).
"""

import gzip
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    load_gnocchi_windows,
    mann_whitney_u,
    paired_permutation_test,
    weighted_mean_z,
)

GTF_FILE = ROOT / "data/input/gencode_v47_basic_grch38.gtf.gz"
TSS_FILE = ROOT / "data/input/gencode_tss_grch38.json"
CHROM_SIZES_FILE = ROOT / "data/input/hg38_chrom_sizes.json"
RESULTS_FILE = (
    ROOT / "experiments/exp_gnocchi_constraint_se_vs_typical_enhancer/positive_control_results.json"
)

SAMPLE_SIZE = 3000
MIN_DIST_FROM_TSS = 100_000
SEED = 42
N_PERMUTATIONS = 10000


def load_cds_exons():
    exons = []
    with gzip.open(GTF_FILE, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if cols[2] != "CDS":
                continue
            chrom, start, end = cols[0], int(cols[3]) - 1, int(cols[4])  # GTF is 1-based inclusive
            if "_" in chrom or chrom in ("chrM",):
                continue
            exons.append((chrom, start, end))
    # dedupe (many transcripts share exons)
    exons = sorted(set(exons))
    return exons


def load_tss_points():
    with open(TSS_FILE) as f:
        data = json.load(f)
    by_chrom = {}
    for t in data["tss"]:
        by_chrom.setdefault(t["chrom"], []).append(t["tss"])
    for c in by_chrom:
        by_chrom[c].sort()
    return by_chrom


def load_chrom_sizes():
    with open(CHROM_SIZES_FILE) as f:
        data = json.load(f)
    return data["sizes"]


def far_from_any_tss(chrom, pos, tss_by_chrom, min_dist):
    import bisect

    points = tss_by_chrom.get(chrom)
    if not points:
        return True
    i = bisect.bisect_left(points, pos)
    for j in (i - 1, i):
        if 0 <= j < len(points) and abs(points[j] - pos) < min_dist:
            return False
    return True


def sample_intergenic_regions(n, length_pool, tss_by_chrom, chrom_sizes, seed):
    rng = random.Random(seed)
    chroms = [c for c in chrom_sizes if "_" not in c and c not in ("chrM", "chrY")]
    out = []
    attempts = 0
    max_attempts = n * 200
    while len(out) < n and attempts < max_attempts:
        attempts += 1
        length = length_pool[len(out) % len(length_pool)]
        chrom = rng.choice(chroms)
        size = chrom_sizes[chrom]
        if size <= length + 2 * MIN_DIST_FROM_TSS:
            continue
        start = rng.randint(MIN_DIST_FROM_TSS, size - length - MIN_DIST_FROM_TSS)
        end = start + length
        if far_from_any_tss(chrom, start, tss_by_chrom, MIN_DIST_FROM_TSS) and far_from_any_tss(
            chrom, end, tss_by_chrom, MIN_DIST_FROM_TSS
        ):
            out.append((chrom, start, end))
    return out


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def main():
    print("Loading CDS exons from GENCODE v47 basic GTF...")
    exons = load_cds_exons()
    print(f"  {len(exons)} unique CDS exon intervals")

    rng = random.Random(SEED)
    exon_sample = rng.sample(exons, min(SAMPLE_SIZE, len(exons)))
    print(f"  Sampled {len(exon_sample)} CDS exons (seed={SEED})")

    print("Loading TSS points (for intergenic exclusion zone) and chrom sizes...")
    tss_by_chrom = load_tss_points()
    chrom_sizes = load_chrom_sizes()

    length_pool = [e - s for _, s, e in exon_sample]
    print(
        f"Sampling {len(exon_sample)} length-matched 'intergenic' regions (>= {MIN_DIST_FROM_TSS}bp from any TSS)..."
    )
    intergenic_sample = sample_intergenic_regions(
        len(exon_sample), length_pool, tss_by_chrom, chrom_sizes, SEED
    )
    print(f"  Sampled {len(intergenic_sample)} intergenic regions")

    print("Loading Gnocchi 1kb constraint windows...")
    gnocchi = load_gnocchi_windows()

    pairs_z = []
    n = min(len(exon_sample), len(intergenic_sample))
    for i in range(n):
        e_chrom, e_start, e_end = exon_sample[i]
        i_chrom, i_start, i_end = intergenic_sample[i]
        z_exon = weighted_mean_z(e_chrom, e_start, e_end, gnocchi)
        z_inter = weighted_mean_z(i_chrom, i_start, i_end, gnocchi)
        if z_exon is None or z_inter is None:
            continue
        pairs_z.append((z_exon, z_inter))

    print(f"Pairs with valid Gnocchi coverage: {len(pairs_z)} / {n}")

    z_exon_all = [a for a, b in pairs_z]
    z_inter_all = [b for a, b in pairs_z]

    u, p_mwu, delta = mann_whitney_u(z_exon_all, z_inter_all)
    observed_diff, p_perm = paired_permutation_test(pairs_z, N_PERMUTATIONS, SEED)

    result = {
        "purpose": "positive control -- does the pipeline detect the known coding-vs-intergenic constraint effect?",
        "n_pairs": len(pairs_z),
        "median_z_cds_exon": median(z_exon_all),
        "median_z_intergenic": median(z_inter_all),
        "mann_whitney_U": u,
        "p_value_mwu": p_mwu,
        "cliffs_delta": delta,
        "paired_permutation_observed_mean_diff": observed_diff,
        "p_value_permutation": p_perm,
        "n_permutations": N_PERMUTATIONS,
        "mcid_reference": "same MCID as main experiment: abs(cliffs_delta) >= 0.2 AND p < 0.05",
        "expected_direction": "CDS exons should show HIGHER Z (more constrained) than intergenic",
    }
    print("\n" + json.dumps(result, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
