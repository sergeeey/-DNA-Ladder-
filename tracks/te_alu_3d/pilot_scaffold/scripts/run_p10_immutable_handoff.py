#!/usr/bin/env python3
"""P10 — immutable handoff snapshot with SHA-256 file hashes.

Locks kill-sprint desk arts + MCIDs + Stage-3 assignments.
Does not set wet-lab GO. Does not touch holdout.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
PS = ROOT / "pilot_scaffold"

# Relative to track root (te_alu_3d)
ARTS = [
    "09_outputs/prospective/KILL_SPRINT_RESULTS_v1.md",
    "09_outputs/prospective/PAUSE_PIN_2026-07-14.md",
    "09_outputs/prospective/SCALE_PROTOCOL_prospective_panel_v1.md",
    "09_outputs/prospective/prospective_panel_registry_v1.yaml",
    "09_outputs/prospective/STAGE1_RESULTS_2026-07-15.md",
    "09_outputs/prospective/stage1_desk_screen_v1.json",
    "09_outputs/prospective/STAGE2_REPORTER_PANEL_v1.md",
    "09_outputs/prospective/C1_claim_freeze_pack_v1.md",
    "09_outputs/prospective/C1_saturation_mutagenesis_v2.md",
    "09_outputs/prospective/C1_saturation_mutagenesis_v2.json",
    "09_outputs/prospective/P3_matched_null_CLAIM_v1.md",
    "09_outputs/prospective/P3_matched_null_panel_v2.md",
    "09_outputs/prospective/P3_matched_null_panel_v2.json",
    "09_outputs/prospective/P3_EXPAND_REPORT_v1.md",
    "09_outputs/prospective/p3_expanded_universe_v1.json",
    "09_outputs/prospective/P5_R1_CLAIM_v1.md",
    "09_outputs/prospective/P5_R1_window_length_ag_v1.md",
    "09_outputs/prospective/P5_R1_window_length_ag_v1.json",
    "09_outputs/prospective/P6_PE_OT_CLAIM_v1.md",
    "09_outputs/prospective/P6_PE_OT_robustness_v1.md",
    "09_outputs/prospective/P6_PE_OT_robustness_v1.json",
    "09_outputs/prospective/P8_POWER_CLAIM_v1.md",
    "09_outputs/prospective/P8_power_simulation_v1.md",
    "09_outputs/prospective/P8_power_simulation_v1.json",
    "09_outputs/prospective/P9_VIRTUAL_E2E_CLAIM_v1.md",
    "09_outputs/prospective/P9_virtual_e2e_v1.md",
    "09_outputs/prospective/P9_virtual_e2e_v1.json",
    "09_outputs/prospective/G4a_multisample_kill_test_v1.md",
    "09_outputs/prospective/GO_note_draft_C1_B_first_v1.md",
    "pilot_scaffold/scripts/run_p3_matched_null_panel.py",
    "pilot_scaffold/scripts/run_p5_r1_window_length_ag.py",
    "pilot_scaffold/scripts/run_p6_pe_ot_primer_desk.py",
    "pilot_scaffold/scripts/run_p8_power_simulation.py",
    "pilot_scaffold/scripts/run_p9_virtual_e2e.py",
    "pilot_scaffold/scripts/run_c1_satmut_ag_expand_v2.py",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    files = []
    missing = []
    for rel in ARTS:
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        files.append(
            {
                "path": rel.replace("\\", "/"),
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size,
            }
        )

    # aggregate hash over sorted "path=hash" lines
    catalog = "\n".join(f"{f['path']}={f['sha256']}" for f in sorted(files, key=lambda x: x["path"]))
    manifest_hash = hashlib.sha256(catalog.encode("utf-8")).hexdigest()

    doc = {
        "manifest_id": "te_alu_3d_kill_sprint_handoff_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "immutable": True,
        "content_hash": manifest_hash,
        "unblind_or_outcome_viewed": False,
        "holdout": "SEALED",
        "wet_lab_go": "NO-GO",
        "oligo_order": "FORBIDDEN",
        "stage3_advancement": "LOCKED",
        "mcid": {
            "reporter": "|log2(ALT/REF)| >= 0.5 in >=2 independent transfections",
            "capture_c": "|DeltaContact| >= 25% WT OR |DeltaOE| >= 0.5",
        },
        "stage3_slots_locked": {
            "architecture_strong_1": "chr11:75445532:G:A",
            "architecture_strong_2": "chr11:518575:C:A",
            "convergence_1": "chr11:72434037:C:T",
            "disagreement_1": "chr11:57568168:C:T",
            "negative_1": "chr11:108009167:T:C",
            "C1_template_excluded": "chr11:62753923:A:G",
        },
        "pe_desk_stack": {
            "pegRNA": "PD1 CGTCCGATAAGCCCTGCCCC",
            "backup_pegRNA": "PD2 TGGCTAAGGGGCGGGACTTC",
            "ngRNA": "GTTCTAAGGTTAGGCCGAGG",
            "ot_watch": "RADIL (and CRISPOR exon list)",
        },
        "kill_sprint_verdicts": {
            "P1_G4a": "PASS_DESK_ROBUST",
            "P2_satmut": "ALLELE_LEAN_RETAINED",
            "P3_matched_null": "RETAIN_HP_C1_C2_C3_panel_not_weakened",
            "P5_R1": "R1_PASS",
            "P6_PE_OT": "PE_OT_CONDITIONAL_PASS",
            "P8_power": "reporter P8_ADEQUATE (n_tx=6); Capture-C P8_UNDERPOWERED",
            "P9_virtual_e2e": "P9_GAPS",
            "P10_immutable": "locked",
        },
        "rules_after_lock": [
            "Do not change MCID, E/P, Stage-3 slots, or primary endpoints after wet data",
            "Lab results fill empty templates only",
            "Any rule change requires new manifest_id + new content_hash",
        ],
        "files": files,
        "missing_files": missing,
        "empty_result_templates": {
            "reporter": {
                "fields": ["variant_id", "tx_id", "log2_ALT_REF", "pass_mcid_bool"],
                "decision_rule": "PASS if >=2 txs |log2|>=0.5 same sign",
            },
            "capture_c": {
                "fields": ["clone_or_batch_id", "delta_contact_frac_wt", "delta_oe", "edit_fraction"],
                "decision_rule": "PASS if |dContact|>=0.25 or |dOE|>=0.5 reproducible",
            },
        },
    }

    out_json = OUT / "P10_immutable_handoff_v1.json"
    out_json.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    # YAML-ish markdown for humans
    lines = [
        "# P10 — Immutable handoff snapshot v1",
        "",
        f"**Created:** {doc['created_at']}",
        f"**immutable:** `true`",
        f"**content_hash:** `{manifest_hash}`",
        "",
        "## Locks",
        "",
        "- holdout: **SEALED**",
        "- wet-lab GO: **NO-GO**",
        "- oligo order: **FORBIDDEN**",
        "- Stage-3 advancement: **LOCKED** (C1 excluded)",
        "",
        "## MCIDs",
        "",
        f"- Reporter: `{doc['mcid']['reporter']}`",
        f"- Capture-C: `{doc['mcid']['capture_c']}`",
        "",
        "## Stage-3 slots (frozen)",
        "",
    ]
    for k, v in doc["stage3_slots_locked"].items():
        lines.append(f"- `{k}`: `{v}`")

    lines += [
        "",
        "## Kill-sprint verdicts at lock",
        "",
    ]
    for k, v in doc["kill_sprint_verdicts"].items():
        lines.append(f"- **{k}:** `{v}`")

    lines += [
        "",
        f"## Hashed files ({len(files)})",
        "",
        "| path | sha256 | bytes |",
        "|------|--------|------:|",
    ]
    for f in files:
        lines.append(f"| `{f['path']}` | `{f['sha256'][:16]}…` | {f['bytes']} |")

    if missing:
        lines += ["", "## Missing at lock", ""]
        for m in missing:
            lines.append(f"- `{m}`")

    lines += [
        "",
        "## Rules after lock",
        "",
    ]
    for r in doc["rules_after_lock"]:
        lines.append(f"- {r}")

    lines += [
        "",
        "## Empty result templates",
        "",
        "See JSON `empty_result_templates` — lab fills rows; does not edit decision rules.",
        "",
        f"Machine: `{out_json.name}`",
        "",
    ]
    (OUT / "P10_immutable_handoff_v1.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "content_hash": manifest_hash,
                "n_files": len(files),
                "missing": missing,
                "wrote": str(out_json),
            },
            indent=2,
        )
    )
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
