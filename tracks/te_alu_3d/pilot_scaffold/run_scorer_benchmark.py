"""Run scorer benchmark gate (scientific freeze / scorer_benchmark_spec).

Usage:
  python build_benchmark_controls.py
  python run_scorer_benchmark.py
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

from ctcf_pwm_scorer import ctcf_pwm_disruption, scorer_fingerprint
from qc_filters import load_config

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BENCH = DATA / "benchmark"
OUT = ROOT / ".." / "09_outputs" / "pilot_chr11" / "benchmark"


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _auroc(scores: list[float], labels: list[int]) -> float:
    """Mann-Whitney AUROC: P(score_pos > score_neg) + 0.5*ties."""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    gt = sum(1 for p in pos for n in neg if p > n)
    eq = sum(1 for p in pos for n in neg if p == n)
    return (gt + 0.5 * eq) / (len(pos) * len(neg))


def _perm_median_delta(
    pos: list[float], neg: list[float], n_perm: int, rng: random.Random
) -> tuple[float, float]:
    obs = statistics.median(pos) - statistics.median(neg)
    pool = pos + neg
    n_p = len(pos)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pool)
        sim = statistics.median(pool[:n_p]) - statistics.median(pool[n_p:])
        if sim >= obs:
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def run() -> dict[str, Any]:
    cfg = load_config()
    # Prefer planted benchmark fasta when present
    fasta = BENCH / "chr11_hbb_benchmark.fa"
    if not fasta.exists():
        fasta = ROOT / cfg.get("scoring", {}).get("fasta_window", "data/chr11_hbb_window.fa")
        if not fasta.is_absolute():
            fasta = ROOT / fasta
    peaks = DATA / "ctcf_HUDEP2_peaks.bed"

    # clear fasta cache if fingerprint path changed
    from ctcf_pwm_scorer import _load_fasta_window

    _load_fasta_window.cache_clear()

    pos_rows = _read_tsv(BENCH / "positive_controls.tsv")
    neg_rows = _read_tsv(BENCH / "negative_controls.tsv")
    rev_rows = [r for r in _read_tsv(BENCH / "sanity_reversal.tsv") if r.get("set_id") == "S2"]

    def score_row(r: dict[str, str]) -> float:
        meta = ctcf_pwm_disruption(
            r["chrom"],
            int(r["pos"]),
            r["ref"],
            r["alt"],
            fasta_path=fasta,
            peaks_path=peaks,
        )
        return float(meta["score"])

    pos_scores = [score_row(r) for r in pos_rows]
    neg_scores = [score_row(r) for r in neg_rows]
    labels = [1] * len(pos_scores) + [0] * len(neg_scores)
    all_scores = pos_scores + neg_scores
    auroc = _auroc(all_scores, labels)

    rng = random.Random(cfg["pilot"]["random_seed"])
    med_delta, perm_p = _perm_median_delta(pos_scores, neg_scores, n_perm=2000, rng=rng)

    # Direction: positive disruptor should score >= its reversal (ref/alt swap)
    pos_by_id = {r["variant_id"]: s for r, s in zip(pos_rows, pos_scores)}
    correct = 0
    checked = 0
    reversal_pairs: list[dict[str, Any]] = []
    for r in rev_rows:
        pid = r.get("paired_positive_id") or ""
        if pid not in pos_by_id:
            continue
        s_rev = score_row(r)
        s_pos = pos_by_id[pid]
        ok = s_pos >= s_rev  # disruption allele higher than restorative swap
        checked += 1
        correct += int(ok)
        reversal_pairs.append(
            {
                "positive_id": pid,
                "positive_score": s_pos,
                "reversal_score": s_rev,
                "correct": ok,
            }
        )
    frac_correct = correct / checked if checked else float("nan")

    expected = json.loads((BENCH / "expected_outcomes.yaml").read_text(encoding="utf-8"))
    gate = expected["scorer_benchmark_gate"]
    min_auroc = gate["positive_vs_negative"]["min_auROC"]
    frac_req = gate["direction_reversal"]["fraction_correct_sign"]
    perm_max = gate["positive_vs_negative"]["or_median_delta_and_perm"]["perm_p_max"]

    sep_pass = (not math.isnan(auroc) and auroc >= min_auroc) or (
        med_delta > 0 and perm_p < perm_max
    )
    dir_pass = (not math.isnan(frac_correct)) and frac_correct >= frac_req
    overall = "PASS" if (sep_pass and dir_pass) else "FAIL"

    report = {
        "status": overall,
        "scorer": "ctcf_pwm_delta_v1.1",
        "fingerprint": scorer_fingerprint(),
        "n_positive": len(pos_scores),
        "n_negative": len(neg_scores),
        "n_reversal_checked": checked,
        "median_positive": statistics.median(pos_scores) if pos_scores else None,
        "median_negative": statistics.median(neg_scores) if neg_scores else None,
        "median_P_minus_N": med_delta,
        "auROC": auroc,
        "perm_p_median_delta": perm_p,
        "direction_reversal_fraction_correct": frac_correct,
        "gates": {
            "separation_pass": sep_pass,
            "direction_pass": dir_pass,
            "min_auROC": min_auroc,
            "perm_p_max": perm_max,
            "fraction_correct_required": frac_req,
        },
        "fail_action": gate.get("fail_action"),
        "reversal_pairs_head": reversal_pairs[:5],
        "interpretation": (
            "Scorer may proceed to holdout prep"
            if overall == "PASS"
            else "STOP biological enrichment runs until scorer fixed or replaced"
        ),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "scorer_benchmark_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    (OUT / "pass_fail.txt").write_text(overall + "\n", encoding="utf-8")
    return report


def main() -> int:
    if not (BENCH / "positive_controls.tsv").exists():
        from build_benchmark_controls import build

        build()
    report = run()
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
