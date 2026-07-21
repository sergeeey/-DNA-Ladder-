#!/usr/bin/env python3
"""C-E1 T0 probe: local assets for TE vs non-TE rare-SNV PWM desk (non-HBB)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
TRACK = EXP.parents[1]
PILOT = TRACK / "pilot_scaffold"
OUT = EXP / "data" / "t0_accession_probe.json"


def exists(p: Path) -> dict:
    return {"path": str(p), "exists": p.exists(), "size": (p.stat().st_size if p.exists() else 0)}


def main() -> int:
    scorer = PILOT / "ctcf_pwm_scorer.py"
    hbb_gnomad = PILOT / "data" / "gnomad_hbb_window.tsv"
    holdout_manifest = TRACK / "07_methods" / "holdout_manifest.yaml"
    umap_candidates = list(
        (TRACK / "experiments" / "exp_te_loop_assay_discordance_chia_vs_hic" / "data" / "input").glob(
            "k100*.bw"
        )
    ) + list((EXP / "data" / "input").glob("k100*"))
    stage1 = TRACK / "09_outputs" / "prospective" / "stage1_desk_screen_v1.tsv"

    report = {
        "candidate_id": "C-E1",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "scorer": exists(scorer),
        "hbb_gnomad_dev_only": exists(hbb_gnomad),
        "holdout_manifest": exists(holdout_manifest),
        "holdout_status": "SEALED",
        "stage1_te_panel": exists(stage1),
        "umap_local_hits": [exists(p) for p in umap_candidates],
        "genomewide_non_hbb_rare_snv_panel_on_disk": False,
        "verdict": "T0_PASS_FREEZE",
        "blockers": [
            "No genome-wide non-HBB gnomAD rare-SNV TE∪non-TE panel on disk",
            "Umap k100 bigWig not in this experiment data/input",
            "Holdout remains SEALED — cannot use HO windows for enrichment",
            "HBB gnomAD present but excluded from primary (development set)",
        ],
        "next": "Fetch non-HBB rare SNV panel + umap; then match-before-PWM primary",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"], "blockers": report["blockers"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
