#!/usr/bin/env python3
"""exp_llps_promoter_vs_se_chip_evidence -- matched-control sensitivity check
(requested after external methodological review): does the SE-favoring
BRD4/MED1 density result survive when the comparator is "typical enhancer"
(H3K27ac-marked, NOT part of a super-enhancer) instead of "rest of genome"?

Rest-of-genome includes large amounts of inactive/heterochromatic DNA where
BRD4/MED1 trivially have near-zero signal -- a matched H3K27ac-active
control is a much stronger test. Reuses merge_intervals/subtract_intervals/
point_in_intervals verbatim from llps_promoter_vs_se_analysis.py.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))

import llps_promoter_vs_se_analysis as base  # noqa: E402

RESULTS_FILE = (
    ROOT / "experiments/exp_llps_promoter_vs_se_chip_evidence/results_matched_control.json"
)

CELL_LINES = {
    "K562": {
        "se_file": ROOT / "data/input/k562_super_enhancers_grch38.json",
        "h3k27ac_file": ROOT / "data/input/h3k27ac_k562_grch38.json",
        "peak_files": {
            "BRD4": ROOT / "data/input/chip_brd4_grch38.json",
            "MED1": ROOT / "data/input/chip_med1_grch38.json",
        },
    },
    "HepG2": {
        "se_file": ROOT / "data/input/hepg2_super_enhancers_grch38.json",
        "h3k27ac_file": ROOT / "data/input/h3k27ac_hepg2_grch38.json",
        "peak_files": {
            "BRD4": ROOT / "data/input/chip_brd4_hepg2_grch38.json",
            "MED1": ROOT / "data/input/chip_med1_hepg2_grch38.json",
        },
    },
}


def build_h3k27ac_intervals(peaks):
    from collections import defaultdict

    by_chrom = defaultdict(list)
    for p in peaks:
        by_chrom[p["chrom"]].append((p["start"], p["end"]))
    return dict(by_chrom)


def run_cell_line(cell, config):
    with open(config["se_file"]) as f:
        se_data = json.load(f)
    with open(config["h3k27ac_file"]) as f:
        h3k27ac_data = json.load(f)

    se_raw = base.build_se_intervals(se_data["super_enhancers"])
    h3k27ac_raw = build_h3k27ac_intervals(h3k27ac_data["peaks"])

    se_merged, se_bp = base.merge_intervals(se_raw)
    h3k27ac_merged, h3k27ac_bp = base.merge_intervals(h3k27ac_raw)

    # "typical enhancer" = H3K27ac-marked space MINUS super-enhancer space
    te_only, te_bp = base.subtract_intervals(h3k27ac_merged, se_merged)

    print(f"\n=== {cell} ===")
    print(f"  SE regions: {se_bp:,} bp merged")
    print(f"  H3K27ac regions: {h3k27ac_bp:,} bp merged")
    print(f"  Typical-enhancer-only (H3K27ac minus SE): {te_bp:,} bp")

    results = {
        "se_bp": se_bp,
        "h3k27ac_bp": h3k27ac_bp,
        "typical_enhancer_bp": te_bp,
        "factors": {},
    }

    for factor, path in config["peak_files"].items():
        with open(path) as f:
            peak_data = json.load(f)
        peaks = peak_data["peaks"]
        n_se = n_te = n_neither = 0
        for p in peaks:
            mid = (p["start"] + p["end"]) // 2
            in_se = base.point_in_intervals(p["chrom"], mid, se_merged)
            in_te = base.point_in_intervals(p["chrom"], mid, te_only)
            if in_se:
                n_se += 1
            elif in_te:
                n_te += 1
            else:
                n_neither += 1

        density_se = n_se / (se_bp / 1000) if se_bp else float("nan")
        density_te = n_te / (te_bp / 1000) if te_bp else float("nan")
        ratio_se_vs_te = density_se / density_te if density_te else float("nan")

        print(
            f"  {factor} ({peak_data['n_peaks']} peaks): "
            f"SE={n_se}, typical-enhancer={n_te}, neither={n_neither}"
        )
        print(
            f"    density_SE={density_se:.4f}/kb, density_typical_enhancer={density_te:.4f}/kb, "
            f"ratio(SE/typical)={ratio_se_vs_te:.3f}"
        )

        results["factors"][factor] = {
            "n_total_peaks": peak_data["n_peaks"],
            "n_se": n_se,
            "n_typical_enhancer": n_te,
            "n_neither": n_neither,
            "density_se_per_kb": density_se,
            "density_typical_enhancer_per_kb": density_te,
            "se_vs_typical_enhancer_ratio": ratio_se_vs_te,
        }

    return results


def main():
    all_results = {}
    for cell, config in CELL_LINES.items():
        all_results[cell] = run_cell_line(cell, config)

    all_results["interpretation_note"] = (
        "ratio > 1.0 means SE peak density exceeds typical-H3K27ac-enhancer density "
        "(SE-favoring survives a matched active-chromatin control, not just vs whole genome); "
        "ratio near or below 1.0 means the original SE-favoring result may have been driven "
        "mainly by comparing to inactive genome, not by SE being special vs other active enhancers."
    )

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
