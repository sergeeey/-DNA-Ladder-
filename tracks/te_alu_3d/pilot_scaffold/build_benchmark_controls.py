"""Build synthetic pos/neg/sanity benchmark controls.

Plants CTCF consensus motifs into a benchmark-only fasta so gates are well-defined.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ctcf_pwm_scorer import PWM_LEN, _CTCF_PWM, _load_fasta_window, _load_peaks, _revcomp

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BENCH = DATA / "benchmark"

CONSENSUS = "".join(max(col, key=col.get) for col in _CTCF_PWM)
WORST = "".join(min(col, key=col.get) for col in _CTCF_PWM)


def _write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def build() -> dict:
    src_fa = DATA / "chr11_hbb_window.fa"
    peaks_path = DATA / "ctcf_HUDEP2_peaks.bed"
    chrom, fa_start, fa_end, seq = _load_fasta_window(str(src_fa))
    seq_list = list(seq)
    peaks = [(a, b) for a, b in _load_peaks(peaks_path) if not (b < fa_start or a > fa_end)]

    # Plant sites: prefer inside peaks; else evenly in window
    plant_abs: list[int] = []
    for a, b in peaks:
        mid = (a + b) // 2
        if fa_start + 50 <= mid <= fa_end - PWM_LEN - 50:
            plant_abs.append(mid - PWM_LEN // 2)
    if len(plant_abs) < 20:
        for i in range(20):
            plant_abs.append(fa_start + 2000 + i * 4000)
    plant_abs = sorted(set(plant_abs))[:40]

    fields = ["set_id", "variant_id", "chrom", "pos", "ref", "alt", "expected", "note"]
    positives: list[dict] = []
    negatives: list[dict] = []
    reversals: list[dict] = []

    for i, abs_start in enumerate(plant_abs):
        rel = abs_start - fa_start
        if rel < 0 or rel + PWM_LEN > len(seq_list):
            continue
        # plant consensus
        for j, base in enumerate(CONSENSUS):
            seq_list[rel + j] = base

        # P1: mutate position 5 (high-info) consensus → worst
        offset = 5
        ref = CONSENSUS[offset]
        alt = WORST[offset]
        if alt == ref:
            alt = "A" if ref != "A" else "C"
        pos = abs_start + offset
        vid = f"P1_{i}_chr11:{pos}:{ref}:{alt}"
        positives.append(
            {
                "set_id": "P1",
                "variant_id": vid,
                "chrom": "chr11",
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "expected": "high",
                "note": f"planted_consensus_destroy offset={offset}",
            }
        )
        reversals.append(
            {
                "set_id": "S2",
                "variant_id": f"S2_{i}_chr11:{pos}:{alt}:{ref}",
                "chrom": "chr11",
                "pos": pos,
                "ref": alt,
                "alt": ref,
                "expected": "low_or_negative_delta",
                "note": f"reversal_of_{vid}",
                "paired_positive_id": vid,
            }
        )

        # N1: same peak/region but 40bp upstream of planted motif
        nrel = rel - 40
        if nrel >= 0:
            nref = seq_list[nrel]
            nalt = {"A": "C", "C": "A", "G": "T", "T": "G"}.get(nref, "A")
            npos = fa_start + nrel
            negatives.append(
                {
                    "set_id": "N1",
                    "variant_id": f"N1_{i}_chr11:{npos}:{nref}:{nalt}",
                    "chrom": "chr11",
                    "pos": npos,
                    "ref": nref,
                    "alt": nalt,
                    "expected": "low",
                    "note": "near_planted_motif_outside_core",
                }
            )

    # N2 far from plants and peaks
    n2 = 0
    for rel in range(100, len(seq_list) - 100, 700):
        if n2 >= 40:
            break
        pos = fa_start + rel
        if any(abs(pos - (p + 5)) < 5000 for p in plant_abs):
            continue
        if any(a - 5000 <= pos <= b + 5000 for a, b in peaks):
            continue
        ref = seq_list[rel]
        if ref not in "ACGT":
            continue
        alt = {"A": "G", "G": "A", "C": "T", "T": "C"}[ref]
        negatives.append(
            {
                "set_id": "N2",
                "variant_id": f"N2_{n2}_chr11:{pos}:{ref}:{alt}",
                "chrom": "chr11",
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "expected": "low",
                "note": "far_from_plant_and_peak",
            }
        )
        n2 += 1

    # S1 orientation: plant revcomp consensus and destroy same offset
    for i, abs_start in enumerate(plant_abs[:10]):
        rel = abs_start - fa_start + 80
        if rel < 0 or rel + PWM_LEN > len(seq_list):
            continue
        rc = _revcomp(CONSENSUS)
        for j, base in enumerate(rc):
            seq_list[rel + j] = base
        offset = 5
        # destroy on genomic forward string at offset
        ref = seq_list[rel + offset]
        alt = WORST[PWM_LEN - 1 - offset]  # rough
        if alt == ref:
            alt = "T" if ref != "T" else "A"
        pos = fa_start + rel + offset
        reversals.append(
            {
                "set_id": "S1",
                "variant_id": f"S1_{i}_chr11:{pos}:{ref}:{alt}",
                "chrom": "chr11",
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "expected": "consistent_magnitude",
                "note": "revcomp_planted_motif_destroy",
            }
        )

    bench_fa = BENCH / "chr11_hbb_benchmark.fa"
    BENCH.mkdir(parents=True, exist_ok=True)
    bench_fa.write_text(
        f">chr11:{fa_start}-{fa_end}\n{''.join(seq_list)}\n", encoding="utf-8"
    )

    _write_tsv(BENCH / "positive_controls.tsv", positives, fields)
    _write_tsv(BENCH / "negative_controls.tsv", negatives, fields)
    _write_tsv(
        BENCH / "sanity_reversal.tsv",
        reversals,
        fields + ["paired_positive_id"],
    )

    expected = {
        "scorer_benchmark_gate": {
            "positive_vs_negative": {
                "min_auROC": 0.75,
                "or_median_delta_and_perm": {
                    "median_P_minus_median_N_gt": 0.0,
                    "perm_p_max": 0.01,
                },
            },
            "direction_reversal": {"fraction_correct_sign": 0.9},
            "peak_summit_monotonicity": "exploratory_report_only",
            "fail_action": "STOP_biological_enrichment_runs",
        },
        "n_positive": len(positives),
        "n_negative": len(negatives),
        "n_reversal": len([r for r in reversals if r["set_id"] == "S2"]),
        "fasta": str(bench_fa),
        "peaks": str(peaks_path),
        "window": f"{chrom}:{fa_start}-{fa_end}",
        "note": "benchmark fasta contains planted CTCF consensus motifs",
    }
    (BENCH / "expected_outcomes.yaml").write_text(
        json.dumps(expected, indent=2), encoding="utf-8"
    )
    return expected


def main() -> int:
    print(json.dumps(build(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
