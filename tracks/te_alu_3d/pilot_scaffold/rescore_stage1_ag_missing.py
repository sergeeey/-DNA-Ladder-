#!/usr/bin/env python3
"""Score Stage-1 alleles missing AG overlay. Loads key from ../.env (gitignored)."""
from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

from load_project_env import load_project_env

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
OUT = PROJ / "09_outputs" / "prospective"
STAGE = OUT / "stage1_desk_screen_v1.json"
TSV = OUT / "stage1_desk_screen_v1.tsv"


def main() -> int:
    load_project_env()
    if not (__import__("os").environ.get("ALPHAGENOME_API_KEY") or __import__("os").environ.get("GOOGLE_API_KEY")):
        raise SystemExit("ALPHAGENOME_API_KEY not in .env or environment")

    from adapters.ag_contact_delta import VariantSpec, score_variant_deltas

    report = json.loads(STAGE.read_text(encoding="utf-8"))
    pool = report["pool"]
    need = [p for p in pool if p.get("ag_status") != "SCORED"]
    print(f"scoring {len(need)} alleles…")
    ok = fail = 0
    for i, p in enumerate(need, 1):
        vid = p["variant_id"]
        print(f"  [{i}/{len(need)}] {vid}", flush=True)
        spec = VariantSpec("chr11", int(p["pos"]), p["ref"], p["alt"])
        try:
            s = score_variant_deltas(spec)
            p["ag_status"] = "SCORED"
            p["ag_contact_mae"] = s.get("contact_mae_all")
            p["ag_chip_tf_mae"] = s.get("chip_tf_mae")
            p["ag_primary_score"] = s.get("primary_score")
            p["ag_error"] = None
            ok += 1
        except Exception as exc:
            p["ag_status"] = "FAIL"
            p["ag_error"] = f"{type(exc).__name__}: {exc}"
            fail += 1
            print("    FAIL", p["ag_error"])
        time.sleep(0.4)

    report["ag_api"] = "PRESENT_rescore_pass"
    report["ag_rescore"] = {"n_attempted": len(need), "n_ok": ok, "n_fail": fail}
    report["pool"] = pool
    STAGE.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    fields = list(csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t").fieldnames or [])
    if "ag_error" not in fields:
        fields.append("ag_error")
    with TSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        for p in pool:
            w.writerow(p)

    print(json.dumps({"ok": ok, "fail": fail}, indent=2))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
