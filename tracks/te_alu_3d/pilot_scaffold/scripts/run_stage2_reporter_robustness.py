#!/usr/bin/env python3
"""Stage-2 reporter window robustness — REF/ALT predicted effect vs length/GC/motifs.

Pre-registered BEFORE viewing:
  Kill Branch B as primary wet plan (keep exploratory) if:
    R1. sign(log2 ALT/REF predicted activity proxy) flips between 301bp and 1kb
        AND again between 1kb and 2kb without shared motif mechanism
    R2. |ΔGC| REF vs ALT > 0.02 in primary window (technical imbalance)
    R3. C1 base within 15 bp of either end of 301bp construct

Proxy metrics (desk): AG scores reused from Stage-1/satmut where available;
local motif delta via PWM; GC%; polyA/splice/cryptic flags via regex.

Does not order oligos.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
DATA = ROOT / "pilot_scaffold" / "data" / "cultivation" / "stage2_reporters"
META = OUT / "stage2_reporter_panel_v1.json"

POLYA = re.compile(r"A{6,}|T{6,}")
SPLICE_DONOR = re.compile(r"GT[AG]AGT")
SPLICE_ACCEPT = re.compile(r"[CT]{6,}[CT]AG")


def gc_frac(seq: str) -> float:
    s = seq.upper()
    return (s.count("G") + s.count("C")) / max(len(s), 1)


def load_fa(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "".join(lines[1:]).upper()


def main() -> int:
    meta = json.loads(META.read_text(encoding="utf-8"))
    # freeze statement pre-result
    freeze = {
        "primary_window": "minimal_301bp",
        "orientation": "genomic_sense",
        "backbone": "minP_luc_or_FP_TBD_at_GO",
        "normalization": "ALT/REF ratio with empty-backbone control",
        "primary_endpoint": "|log2(ALT/REF)|>=0.5 in >=2 tx",
        "secondary_windows": ["context_1kb", "context_2kb"],
    }
    kills_def = ["R1_sign_flip_across_lengths", "R2_deltaGC_gt_0.02", "R3_variant_near_edge"]

    rows = []
    for c in meta["constructs"]:
        cid = c["id"]
        rec = {"id": cid, "variant_id": c["variant_id"], "windows": {}}
        edge_risk = False
        gcs = {}
        for wname, w in c["windows"].items():
            ref = load_fa(DATA / w["ref_file"])
            alt = load_fa(DATA / w["alt_file"])
            idx = w["c1_index0"]
            near_edge = idx < 15 or idx > (len(ref) - 1 - 15)
            if wname == "minimal_301bp" and near_edge:
                edge_risk = True
            dgc = abs(gc_frac(alt) - gc_frac(ref))
            flags = {
                "polyA_ref": bool(POLYA.search(ref)),
                "polyA_alt": bool(POLYA.search(alt)),
                "splice_donor_gained": bool(SPLICE_DONOR.search(alt)) and not bool(SPLICE_DONOR.search(ref)),
                "splice_accept_gained": bool(SPLICE_ACCEPT.search(alt)) and not bool(SPLICE_ACCEPT.search(ref)),
            }
            # activity proxy: AG from construct metadata (same allele all windows)
            chip = c.get("ag", {}).get("chip_tf_mae")
            contact = c.get("ag", {}).get("contact_mae")
            # cannot get length-specific AG without re-score; use GC+edge as tech; AG for allele only
            rec["windows"][wname] = {
                "len": len(ref),
                "gc_ref": gc_frac(ref),
                "gc_alt": gc_frac(alt),
                "delta_gc": dgc,
                "variant_index0": idx,
                "near_edge_15bp": near_edge,
                "flags": flags,
                "ag_chip_tf_mae_allele": chip,
                "ag_contact_mae_allele": contact,
            }
            gcs[wname] = dgc
        # length-specific AG not available → R1 assessed as INCONCLUSIVE_DESK unless we flag missing
        rec["edge_risk_301"] = edge_risk
        rec["max_delta_gc"] = max(gcs.values()) if gcs else None
        rec["R1_status"] = "NOT_TESTED_NEED_WINDOW_AG"  # honest
        rows.append(rec)

    kills = []
    for rec in rows:
        if rec.get("id") == "C1" and rec.get("edge_risk_301"):
            kills.append("R3_variant_near_edge")
        if rec.get("id") == "C1" and (rec.get("max_delta_gc") or 0) > 0.02:
            kills.append("R2_deltaGC_gt_0.02")

    # C1 position in 301bp
    c1 = next(r for r in rows if r["id"] == "C1")
    overall = "REPORTER_DESK_OK_TECHNICAL"
    if "R3_variant_near_edge" in kills or "R2_deltaGC_gt_0.02" in kills:
        overall = "REPORTER_EXPLORATORY_ONLY"
    if any(r["R1_status"] == "NOT_TESTED_NEED_WINDOW_AG" for r in rows):
        note_r1 = "R1 not scored — need AG per window length before freeze of length invariance"
    else:
        note_r1 = "ok"

    out = {
        "status": "REPORTER_ROBUSTNESS_DESK",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "freeze_pre_registered": freeze,
        "kill_definitions": kills_def,
        "overall": overall,
        "kills": kills,
        "note_r1": note_r1,
        "constructs": rows,
    }
    OUT.joinpath("Stage2_reporter_robustness_v1.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    md = [
        "# Stage-2 reporter robustness desk v1",
        "",
        f"**Overall:** `{overall}`  ",
        f"**Kills:** {kills or 'none'}  ",
        f"**R1 note:** {note_r1}",
        "",
        "## Frozen before wet (design lock)",
        "",
        "```yaml",
        json.dumps(freeze, indent=2),
        "```",
        "",
        "## C1 technical",
        "",
        f"- edge risk 301bp: {c1['edge_risk_301']}",
        f"- max |ΔGC|: {c1['max_delta_gc']}",
        f"- idx in 301bp: {c1['windows']['minimal_301bp']['variant_index0']}",
        "",
        "Length-invariance of predicted ALT/REF requires dedicated AG window scores — pending.",
        "",
    ]
    OUT.joinpath("Stage2_reporter_robustness_v1.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"overall": overall, "kills": kills, "c1_idx": c1["windows"]["minimal_301bp"]["variant_index0"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
