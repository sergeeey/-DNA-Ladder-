#!/usr/bin/env python3
"""exp_llps_promoter_vs_se_chip_evidence: does static ChIP-seq co-occupancy of
BRD4/MED1 favor promoters (within 2kb of a GENCODE TSS) or super-enhancers
(dbSUPER K562, lifted to GRCh38)? Pre-registered in claim.md BEFORE this
script ran: peak-density ratio (promoter-only-space vs SE-only-space),
MCID >=1.5 promoter-favoring / <=0.67 SE-favoring / between = no preference.
POLR2A is reported as a broad-binding sanity baseline, not a primary test.
"""

import bisect
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

PROMOTER_WINDOW_BP = 2000

TSS_FILE = ROOT / "data/input/gencode_tss_grch38.json"
SE_FILE = ROOT / "data/input/k562_super_enhancers_grch38.json"
RESULTS_FILE = ROOT / "experiments/exp_llps_promoter_vs_se_chip_evidence/results.json"

PEAK_FILES = {
    "BRD4": ROOT / "data/input/chip_brd4_grch38.json",
    "MED1": ROOT / "data/input/chip_med1_grch38.json",
    "POLR2A": ROOT / "data/input/chip_polr2a_grch38.json",
}


def build_promoter_intervals(tss_list):
    by_chrom = defaultdict(list)
    for g in tss_list:
        s, e = g["tss"] - PROMOTER_WINDOW_BP, g["tss"] + PROMOTER_WINDOW_BP
        by_chrom[g["chrom"]].append((max(0, s), e))
    return by_chrom


def build_se_intervals(se_list):
    by_chrom = defaultdict(list)
    for se in se_list:
        by_chrom[se["chrom"]].append((se["start"], se["end"]))
    return by_chrom


def merge_intervals(by_chrom):
    """Merge overlapping intervals per chromosome; returns {chrom: [(s,e),...]} sorted/merged
    and total bp covered."""
    merged = {}
    total_bp = 0
    for chrom, intervals in by_chrom.items():
        intervals = sorted(intervals)
        out = []
        for s, e in intervals:
            if out and s <= out[-1][1]:
                out[-1] = (out[-1][0], max(out[-1][1], e))
            else:
                out.append((s, e))
        merged[chrom] = out
        total_bp += sum(e - s for s, e in out)
    return merged, total_bp


def subtract_intervals(a_by_chrom, b_by_chrom):
    """Returns a_by_chrom MINUS any overlap with b_by_chrom (per chromosome),
    i.e. the 'a-only' region set. Both inputs must already be merged/sorted."""
    result = {}
    total_bp = 0
    for chrom, a_intervals in a_by_chrom.items():
        b_intervals = b_by_chrom.get(chrom, [])
        out = []
        for a_s, a_e in a_intervals:
            cur_s = a_s
            for b_s, b_e in b_intervals:
                if b_e <= cur_s:
                    continue
                if b_s >= a_e:
                    break
                if b_s > cur_s:
                    out.append((cur_s, min(b_s, a_e)))
                cur_s = max(cur_s, b_e)
                if cur_s >= a_e:
                    break
            if cur_s < a_e:
                out.append((cur_s, a_e))
        result[chrom] = out
        total_bp += sum(e - s for s, e in out)
    return result, total_bp


def point_in_intervals(chrom, pos, merged_by_chrom):
    intervals = merged_by_chrom.get(chrom)
    if not intervals:
        return False
    starts = [s for s, _ in intervals]
    i = bisect.bisect_right(starts, pos) - 1
    if i < 0:
        return False
    s, e = intervals[i]
    return s <= pos < e


def main():
    with open(TSS_FILE) as f:
        tss_data = json.load(f)
    with open(SE_FILE) as f:
        se_data = json.load(f)

    print(
        f"Loaded {tss_data['n_genes']} TSS, {se_data['n_grch38_lifted']} super-enhancers (GRCh38)"
    )

    promoter_raw = build_promoter_intervals(tss_data["tss"])
    se_raw = build_se_intervals(se_data["super_enhancers"])

    promoter_merged, promoter_bp_total = merge_intervals(promoter_raw)
    se_merged, se_bp_total = merge_intervals(se_raw)

    # "promoter-only" space = promoter regions minus any SE overlap, and vice versa --
    # avoids double-counting peaks that fall in a promoter embedded inside a super-enhancer.
    promoter_only, promoter_only_bp = subtract_intervals(promoter_merged, se_merged)
    se_only, se_only_bp = subtract_intervals(se_merged, promoter_merged)

    print(
        f"Promoter windows (+-{PROMOTER_WINDOW_BP}bp): {promoter_bp_total:,} bp merged, "
        f"{promoter_only_bp:,} bp promoter-only (excl. SE overlap)"
    )
    print(
        f"Super-enhancers: {se_bp_total:,} bp merged, {se_only_bp:,} bp SE-only (excl. promoter overlap)"
    )

    results = {
        "promoter_window_bp": PROMOTER_WINDOW_BP,
        "promoter_only_bp_total": promoter_only_bp,
        "se_only_bp_total": se_only_bp,
        "factors": {},
    }

    for factor, path in PEAK_FILES.items():
        with open(path) as f:
            peak_data = json.load(f)
        peaks = peak_data["peaks"]

        n_promoter = n_se = n_both = n_neither = 0
        for p in peaks:
            mid = (p["start"] + p["end"]) // 2
            in_prom = point_in_intervals(p["chrom"], mid, promoter_merged)
            in_se = point_in_intervals(p["chrom"], mid, se_merged)
            if in_prom and in_se:
                n_both += 1
            elif in_prom:
                n_promoter += 1
            elif in_se:
                n_se += 1
            else:
                n_neither += 1

        density_promoter = (
            n_promoter / (promoter_only_bp / 1000) if promoter_only_bp else float("nan")
        )
        density_se = n_se / (se_only_bp / 1000) if se_only_bp else float("nan")
        ratio = density_promoter / density_se if density_se else float("nan")

        print(
            f"\n{factor} ({peak_data['n_peaks']} peaks): "
            f"promoter-only={n_promoter}, SE-only={n_se}, both={n_both}, neither={n_neither}"
        )
        print(
            f"  density_promoter={density_promoter:.4f} peaks/kb, "
            f"density_se={density_se:.4f} peaks/kb, ratio={ratio:.3f}"
        )

        results["factors"][factor] = {
            "n_total_peaks": peak_data["n_peaks"],
            "n_promoter_only": n_promoter,
            "n_se_only": n_se,
            "n_both": n_both,
            "n_neither": n_neither,
            "density_promoter_per_kb": density_promoter,
            "density_se_per_kb": density_se,
            "promoter_se_density_ratio": ratio,
        }

    results["mcid"] = (
        "density_ratio >= 1.5 promoter-favoring; <= 0.67 SE-favoring; between = no clear preference"
    )

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
