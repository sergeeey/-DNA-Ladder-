#!/usr/bin/env python3
"""T0 probe: K562 RAD21 vs CTCF ChIA-PET processed loops (C-G1)."""

from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent.parent / "data" / "t0_accession_probe.json"
USER_AGENT = "DNA-Ladder-C-G1-T0/1.0"

RAD21_EXPS = ["ENCSR338WUS", "ENCSR000FDB"]
CTCF_EXP = "ENCSR597AKG"
CTCF_PREFERRED_LOOP = "ENCFF118PBQ"


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def get_json(url: str, timeout: int = 120) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as resp:
        return json.load(resp)


def inventory_experiment(acc: str) -> dict[str, Any]:
    e = get_json(f"https://www.encodeproject.org/experiments/{acc}/?format=json")
    files = []
    for ref in e.get("files") or []:
        facc = ref.split("/")[2] if isinstance(ref, str) else ref.get("accession")
        if not facc:
            continue
        f = get_json(f"https://www.encodeproject.org/files/{facc}/?format=json")
        files.append(
            {
                "accession": facc,
                "file_format": f.get("file_format"),
                "output_type": f.get("output_type"),
                "assembly": f.get("assembly"),
                "status": f.get("status"),
                "preferred_default": f.get("preferred_default"),
                "href": f.get("href"),
            }
        )
    loops_grch38 = [
        x
        for x in files
        if x.get("file_format") == "bedpe"
        and x.get("assembly") == "GRCh38"
        and "loop" in (x.get("output_type") or "").lower()
        and x.get("status") == "released"
    ]
    return {
        "experiment": acc,
        "assay_title": e.get("assay_title"),
        "target": (e.get("target") or {}).get("label")
        if isinstance(e.get("target"), dict)
        else e.get("target"),
        "status": e.get("status"),
        "n_files": len(files),
        "files": files,
        "grch38_released_loop_bedpe": loops_grch38,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rad21 = [inventory_experiment(a) for a in RAD21_EXPS]
    ctcf = inventory_experiment(CTCF_EXP)
    rad21_loops = [x for inv in rad21 for x in inv["grch38_released_loop_bedpe"]]
    ctcf_loops = ctcf["grch38_released_loop_bedpe"]
    ctcf_ok = any(x["accession"] == CTCF_PREFERRED_LOOP for x in ctcf_loops) or bool(
        ctcf_loops
    )
    verdict = "PASS_FREEZE_CANDIDATE" if (rad21_loops and ctcf_ok) else "BLOCKED_DATA"
    report = {
        "experiment": "exp_rad21_vs_ctcf_chia_te_odds",
        "candidate_id": "C-G1",
        "probed_at_utc": datetime.now(timezone.utc).isoformat(),
        "rad21_experiments": rad21,
        "ctcf_experiment": ctcf,
        "rad21_grch38_loop_bedpe": rad21_loops,
        "ctcf_grch38_loop_bedpe": ctcf_loops,
        "ctcf_preferred_target": CTCF_PREFERRED_LOOP,
        "verdict": verdict,
        "note": (
            "RAD21 K562 ChIA-PET lacks released GRCh38 loop bedpe "
            "(ENCSR338WUS=fastq only; ENCSR000FDB=hg19 archived TSV/bed). "
            "CTCF ENCSR597AKG has ENCFF118PBQ. OR not run."
            if verdict == "BLOCKED_DATA"
            else "Both RAD21 and CTCF GRCh38 loop bedpe present — freeze before OR."
        ),
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "verdict": verdict,
                "n_rad21_loops": len(rad21_loops),
                "n_ctcf_loops": len(ctcf_loops),
                "out": str(OUT),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
