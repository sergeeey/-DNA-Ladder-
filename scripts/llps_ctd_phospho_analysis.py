#!/usr/bin/env python3
"""exp_llps_ctd_phospho_vs_coactivators: extends
exp_llps_promoter_vs_se_chip_evidence's promoter/SE density-ratio method to a
4th factor, Pol II-Ser5P, WITHOUT touching that experiment's own results.json
(writes to this experiment's own results file instead). Reuses every function
and all cached region data from llps_promoter_vs_se_analysis.py verbatim.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))

import llps_promoter_vs_se_analysis as base  # noqa: E402

RESULTS_FILE = ROOT / "experiments/exp_llps_ctd_phospho_vs_coactivators/results.json"

PEAK_FILES = dict(base.PEAK_FILES)
PEAK_FILES["POLR2A-Ser5P"] = ROOT / "data/input/chip_polr2a_ps5_grch38.json"


def run(promoter_window_bp, results_file):
    base.PROMOTER_WINDOW_BP = promoter_window_bp
    with open(base.TSS_FILE) as f:
        tss_data = json.load(f)
    with open(base.SE_FILE) as f:
        se_data = json.load(f)

    promoter_raw = base.build_promoter_intervals(tss_data["tss"])
    se_raw = base.build_se_intervals(se_data["super_enhancers"])
    promoter_merged, _ = base.merge_intervals(promoter_raw)
    se_merged, _ = base.merge_intervals(se_raw)
    promoter_only, promoter_only_bp = base.subtract_intervals(promoter_merged, se_merged)
    se_only, se_only_bp = base.subtract_intervals(se_merged, promoter_merged)

    results = {
        "promoter_window_bp": promoter_window_bp,
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
            in_prom = base.point_in_intervals(p["chrom"], mid, promoter_merged)
            in_se = base.point_in_intervals(p["chrom"], mid, se_merged)
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
            f"[{promoter_window_bp}bp window] {factor} ({peak_data['n_peaks']} peaks): "
            f"ratio={ratio:.3f} (promoter/kb={density_promoter:.4f}, se/kb={density_se:.4f})"
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
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {results_file}\n")
    return results


def main():
    run(2000, RESULTS_FILE)
    sensitivity_file = (
        ROOT / "experiments/exp_llps_ctd_phospho_vs_coactivators/results_sensitivity_5kb.json"
    )
    run(5000, sensitivity_file)


if __name__ == "__main__":
    main()
