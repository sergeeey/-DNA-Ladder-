"""G2 prep: motif/distance baselines vs AlphaGenome for R4 shortlist C1–C3.

Uses local Ensembl fasta under data/cultivation/ (not holdout).
Does not score sealed holdout. Does not freeze G9.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from baseline_scorers import distance_only_score, motif_only_score
from ctcf_pwm_scorer import SCORER_VERSION, ctcf_pwm_disruption, scorer_fingerprint
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed
from qc_filters import VariantRecord

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT.parent / "09_outputs" / "prospective"
PEAKS = DATA / "ctcf_HUDEP2_peaks.bed"
AG_REPORT = OUT / "ag_cultivation_r4_report.json"

CANDS = [
    {
        "id": "C1",
        "chrom": "chr11",
        "pos": 62753923,
        "ref": "A",
        "alt": "G",
        "fasta": DATA / "cultivation" / "chr11_C1C2_62753000_62755000.fa",
    },
    {
        "id": "C2",
        "chrom": "chr11",
        "pos": 62753923,
        "ref": "A",
        "alt": "T",
        "fasta": DATA / "cultivation" / "chr11_C1C2_62753000_62755000.fa",
    },
    {
        "id": "C3",
        "chrom": "chr11",
        "pos": 72434037,
        "ref": "C",
        "alt": "T",
        "fasta": DATA / "cultivation" / "chr11_C3_72433000_72435000.fa",
    },
]


def main() -> int:
    assert holdout_is_sealed()
    assert_not_scoring_holdout(DATA / "cultivation" / "ok.tsv")

    ag_doc = json.loads(AG_REPORT.read_text(encoding="utf-8"))
    ag_by = {x["variant_id"]: x for x in ag_doc.get("all_scores") or []}

    rows: list[dict] = []
    for c in CANDS:
        vid = f"{c['chrom']}:{c['pos']}:{c['ref']}:{c['alt']}"
        assert c["fasta"].exists(), c["fasta"]
        raw = ctcf_pwm_disruption(
            c["chrom"], c["pos"], c["ref"], c["alt"], fasta_path=c["fasta"], peaks_path=PEAKS
        )
        v = VariantRecord(
            chrom=c["chrom"],
            pos=c["pos"],
            ref=c["ref"],
            alt=c["alt"],
            variant_id=vid,
        )
        motif = motif_only_score(v, fasta_path=c["fasta"], peaks_path=PEAKS)
        dist = distance_only_score(v, peaks_path=PEAKS)
        ag = ag_by.get(vid) or {}
        rows.append(
            {
                "candidate_id": c["id"],
                "variant_id": vid,
                "pwm_version": SCORER_VERSION,
                "pwm_fingerprint": scorer_fingerprint(),
                "delta_logodds": raw.get("delta_logodds"),
                "pwm_disruption_score": raw.get("score"),
                "in_peak": raw.get("in_peak"),
                "dist_peak": raw.get("dist_peak"),
                "allele_mismatch": raw.get("allele_mismatch", False),
                "motif_only_score": motif.get("score"),
                "motif_only_ok": motif.get("ok"),
                "distance_only_score": dist.get("score"),
                "ag_contact_mae": ag.get("contact_mae_all") or ag.get("primary_score"),
                "ag_chip_tf_mae": ag.get("chip_tf_mae"),
                "fasta": str(c["fasta"].relative_to(ROOT)),
            }
        )

    # Rank correlations / disagreements (tiny n — descriptive only)
    def ranks(key: str) -> dict[str, int]:
        ordered = sorted(rows, key=lambda r: float(r.get(key) or 0.0), reverse=True)
        return {r["candidate_id"]: i + 1 for i, r in enumerate(ordered)}

    r_ag = ranks("ag_contact_mae")
    r_motif = ranks("motif_only_score")
    r_tf = ranks("ag_chip_tf_mae")
    agreement = []
    for r in rows:
        cid = r["candidate_id"]
        agreement.append(
            {
                "candidate_id": cid,
                "rank_ag_contact": r_ag[cid],
                "rank_ag_chip_tf": r_tf[cid],
                "rank_motif": r_motif[cid],
                "ag_vs_motif": "AGREE"
                if r_ag[cid] == r_motif[cid]
                else "DISAGREE",
            }
        )

    # G2 decision heuristic for cultivation (not confirmatory PASS)
    # Prefer C where AG ranks high AND motif is not null/near-zero if claiming M1.
    g2_note = (
        "Descriptive only (n=3). Arm A = AG∩motif directionally up; "
        "Arm B = AG high + motif low → architecture-leaning vs motif-only."
    )

    report = {
        "status": "G2_PREP_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "holdout_sealed": True,
        "scored_holdout": False,
        "scorer_pwm": SCORER_VERSION,
        "scorer_fp": scorer_fingerprint(),
        "rows": rows,
        "rank_agreement": agreement,
        "g2_note": g2_note,
        "verdict": {
            "C1": "Arm_B_lean" if r_ag["C1"] == 1 and r_motif["C1"] > 1 else "mixed",
            "C2": "secondary_allele",
            "C3": "mixed",
        },
        "next": [
            "Keep C1 preferred if Arm B (AG>motif) confirmed after TF channel audit",
            "Do not G9 freeze — need G5 editability + HUDEP-2 G4",
            "Holdout still sealed",
        ],
    }

    # Fix verdicts with actual ranks
    report["verdict"] = {
        "C1": (
            "ARM_B_AG_GT_MOTIF"
            if r_ag["C1"] < r_motif["C1"]
            else ("ARM_A_CONVERGE" if r_ag["C1"] == r_motif["C1"] else "ARM_B_MOTIF_GT_AG")
        ),
        "C2": (
            "ARM_B_AG_GT_MOTIF"
            if r_ag["C2"] < r_motif["C2"]
            else ("ARM_A_CONVERGE" if r_ag["C2"] == r_motif["C2"] else "ARM_B_MOTIF_GT_AG")
        ),
        "C3": (
            "ARM_B_AG_GT_MOTIF"
            if r_ag["C3"] < r_motif["C3"]
            else ("ARM_A_CONVERGE" if r_ag["C3"] == r_motif["C3"] else "ARM_B_MOTIF_GT_AG")
        ),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "g2_r4_shortlist_report.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    out_tsv = OUT / "g2_r4_shortlist_scores.tsv"
    fields = list(rows[0].keys()) if rows else []
    with out_tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    lines = [
        "# G2 prep — R4 shortlist C1–C3 (motif vs AlphaGenome)",
        "",
        f"**Date:** {report['timestamp'][:10]}  ",
        f"**PWM:** `{SCORER_VERSION}` fp `{scorer_fingerprint()}`  ",
        "**Holdout:** SEALED / not scored  ",
        "**Status:** G2_PREP_COMPLETE — descriptive ranks only (n=3)",
        "",
        "| ID | Variant | Motif-only | Δlogodds | Dist-only | AG contact MAE | AG CHIP_TF MAE | Arm lean |",
        "|----|---------|-----------:|---------:|----------:|---------------:|---------------:|----------|",
    ]
    for r, a in zip(rows, agreement):
        lines.append(
            f"| {r['candidate_id']} | `{r['variant_id']}` | "
            f"{float(r['motif_only_score'] or 0):.3f} | "
            f"{float(r['delta_logodds'] or 0):.3f} | "
            f"{float(r['distance_only_score'] or 0):.3f} | "
            f"{float(r['ag_contact_mae'] or 0):.4f} | "
            f"{float(r['ag_chip_tf_mae'] or 0):.3f} | "
            f"{report['verdict'][r['candidate_id']]} |"
        )
    lines += [
        "",
        "## Rank table",
        "",
        "| ID | Rank AG contact | Rank AG CHIP_TF | Rank motif | AG vs motif |",
        "|----|----------------:|----------------:|-----------:|-------------|",
    ]
    for a in agreement:
        lines.append(
            f"| {a['candidate_id']} | {a['rank_ag_contact']} | {a['rank_ag_chip_tf']} | "
            f"{a['rank_motif']} | {a['ag_vs_motif']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Higher AG contact rank with lower motif rank → **Arm B** (architecture-leaning, need strong WT contact).",
        "- Same ranks → **Arm A** convergence (still not wet-lab GO).",
        "- Motif alone remains exploratory PWM — cannot authorize confirmatory primary.",
        "",
        "## Non-claims",
        "- No G9 freeze / no wet-lab / no holdout unblind / no 3D disruption",
        "",
        f"Artifacts: `{out_json.name}`, `{out_tsv.name}`",
        "",
    ]
    (OUT / "g2_r4_shortlist.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"], "rows": rows, "out": str(out_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
