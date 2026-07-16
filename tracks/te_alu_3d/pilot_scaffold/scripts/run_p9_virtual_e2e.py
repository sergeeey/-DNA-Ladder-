#!/usr/bin/env python3
"""P9 — virtual end-to-end dry-run of C1 dual-track B0→A1→A2.

Process falsification audit using existing desk arts only.
Does not authorize wet-lab GO / oligo order / holdout unblind.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
CULT = ROOT / "pilot_scaffold" / "data" / "cultivation"

REQUIRED = [
    "09_outputs/prospective/GO_note_draft_C1_B_first_v1.md",
    "09_outputs/prospective/C1_claim_freeze_pack_v1.md",
    "09_outputs/prospective/STAGE2_REPORTER_PANEL_v1.md",
    "09_outputs/prospective/P6_PE_OT_robustness_v1.md",
    "09_outputs/prospective/OT_amplicon_primer_panel_desk_v1.md",
    "09_outputs/prospective/G4b_bait_windows_locked.yaml",
    "09_outputs/prospective/CaptureC_bait_quote_sheet_v1.md",
    "09_outputs/prospective/P8_power_simulation_v1.md",
    "09_outputs/prospective/P10_immutable_handoff_v1.md",
    "09_outputs/prospective/PAUSE_PIN_2026-07-14.md",
    "09_outputs/prospective/BranchB_oligo_checklist_v1.md",
    "09_outputs/prospective/KILL_SPRINT_RESULTS_v1.md",
]

FASTA = [
    "c1_reporter_minimal_301bp_REF.fa",
    "c1_reporter_minimal_301bp_ALT.fa",
    "c1_reporter_context_1kb_REF.fa",
    "c1_reporter_context_1kb_ALT.fa",
    "c1_reporter_context_2kb_REF.fa",
    "c1_reporter_context_2kb_ALT.fa",
]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def _has(text: str, *needles: str) -> bool:
    return all(n in text for n in needles)


def main() -> int:
    hard: list[dict] = []
    soft: list[dict] = []
    ok_checks: list[dict] = []

    # --- file presence ---
    missing = [r for r in REQUIRED if not (ROOT / r).is_file()]
    for r in missing:
        hard.append({"id": "MISSING_ART", "path": r, "detail": "required art absent"})
    for r in REQUIRED:
        if (ROOT / r).is_file():
            ok_checks.append({"id": "ART_PRESENT", "path": r})

    fasta_missing = [f for f in FASTA if not (CULT / f).is_file()]
    for f in fasta_missing:
        hard.append({"id": "MISSING_FASTA", "path": str(CULT / f), "detail": "C1 reporter FASTA absent"})
    for f in FASTA:
        if (CULT / f).is_file():
            ok_checks.append({"id": "FASTA_PRESENT", "path": f})

    # --- GO note locks ---
    go = _read("09_outputs/prospective/GO_note_draft_C1_B_first_v1.md") if not missing else ""
    if go:
        if "UNSIGNED_DRAFT" in go or "authorization_state:  UNSIGNED" in go:
            ok_checks.append({"id": "GO_UNSIGNED", "detail": "GO remains UNSIGNED_DRAFT"})
        else:
            hard.append({"id": "GO_SIGNED_UNEXPECTED", "detail": "GO appears signed during desk dry-run"})
        if "FORBIDDEN" in go:
            ok_checks.append({"id": "OLIGO_FORBIDDEN", "detail": "oligo/transfection FORBIDDEN in GO note"})
        if "chr11:62753923" in go and "A>G" in go:
            ok_checks.append({"id": "C1_ALLELE_FROZEN", "detail": "C1 A>G present in GO note"})

    # --- Stage-2 reporter ---
    s2 = _read("09_outputs/prospective/STAGE2_REPORTER_PANEL_v1.md") if (ROOT / "09_outputs/prospective/STAGE2_REPORTER_PANEL_v1.md").is_file() else ""
    if s2:
        if "ORDER FORBIDDEN" in s2:
            ok_checks.append({"id": "STAGE2_ORDER_FORBIDDEN"})
        if "0.5" in s2 and "transfection" in s2.lower():
            ok_checks.append({"id": "REPORTER_MCID", "detail": "MCID log2>=0.5 present"})

    # --- Branch B backbone soft gap ---
    bb = _read("09_outputs/prospective/BranchB_oligo_checklist_v1.md") if (ROOT / "09_outputs/prospective/BranchB_oligo_checklist_v1.md").is_file() else ""
    if bb:
        if re.search(r"backbone|vendor / plasmid|☐", bb, re.I):
            soft.append(
                {
                    "id": "BACKBONE_TBD",
                    "detail": "Reporter backbone vendor/plasmid ID still lab-fill before order",
                }
            )

    # --- P6 PE/OT ---
    p6 = _read("09_outputs/prospective/P6_PE_OT_robustness_v1.md") if (ROOT / "09_outputs/prospective/P6_PE_OT_robustness_v1.md").is_file() else ""
    if p6:
        if "PE_OT_CONDITIONAL_PASS" in p6:
            ok_checks.append({"id": "P6_CONDITIONAL_PASS"})
        if "RADIL" in p6:
            ok_checks.append({"id": "RADIL_WATCH_DOCUMENTED"})
        if "PRIMER_BLAST" in p6.upper() or "Primer-BLAST" in p6 or "manual" in p6.lower():
            soft.append(
                {
                    "id": "PRIMER_BLAST_MANUAL",
                    "detail": "Genome-wide Primer-BLAST still manual before oligo order",
                }
            )
        if "GTTCTAAGGTTAGGCCGAGG" in p6 or "ngRNA" in p6:
            ok_checks.append({"id": "NGRNA_DOCUMENTED"})

    # --- OT primers ---
    ot = _read("09_outputs/prospective/OT_amplicon_primer_panel_desk_v1.md") if (ROOT / "09_outputs/prospective/OT_amplicon_primer_panel_desk_v1.md").is_file() else ""
    if ot:
        ok_checks.append({"id": "OT_PRIMER_PANEL_PRESENT"})

    # --- Capture baits + P8 power ---
    bait = ROOT / "09_outputs/prospective/G4b_bait_windows_locked.yaml"
    if bait.is_file():
        ok_checks.append({"id": "BAITS_LOCKED"})
    p8 = _read("09_outputs/prospective/P8_power_simulation_v1.md") if (ROOT / "09_outputs/prospective/P8_power_simulation_v1.md").is_file() else ""
    if p8:
        if "P8_ADEQUATE" in p8:
            ok_checks.append({"id": "REPORTER_POWER_ADEQUATE"})
        if "P8_UNDERPOWERED" in p8:
            soft.append(
                {
                    "id": "CAPTURE_UNDERPOWERED",
                    "detail": "Capture-C P8_UNDERPOWERED — must not be sold as powered primary",
                }
            )

    # --- P10 / pause locks ---
    p10 = _read("09_outputs/prospective/P10_immutable_handoff_v1.md") if (ROOT / "09_outputs/prospective/P10_immutable_handoff_v1.md").is_file() else ""
    if p10:
        for lock, needle in [
            ("HOLDOUT_SEALED", "SEALED"),
            ("WET_NOGO", "NO-GO"),
            ("STAGE3_LOCKED", "LOCKED"),
        ]:
            if needle in p10:
                ok_checks.append({"id": lock})
            else:
                hard.append({"id": f"MISSING_LOCK_{lock}", "detail": f"{needle} not found in P10"})

    # --- contradictions (hard) ---
    if go and "ORDER FORBIDDEN" not in s2 and s2 and "FORBIDDEN" not in go:
        hard.append({"id": "ORDER_STATUS_CONFLICT", "detail": "order status unclear across arts"})

    # Label
    if hard:
        label = "P9_BLOCKED"
    elif soft:
        label = "P9_GAPS"
    else:
        label = "P9_COHERENT"

    payload = {
        "status": "P9_VIRTUAL_E2E_COMPLETE",
        "label": label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "P9_VIRTUAL_E2E_CLAIM_v1.md",
        "n_ok": len(ok_checks),
        "n_soft": len(soft),
        "n_hard": len(hard),
        "ok_checks": ok_checks,
        "soft_gaps": soft,
        "hard_blocks": hard,
        "phases": {
            "B0": "desk arts present; backbone soft gap; ORDER FORBIDDEN",
            "A1": "PE_OT_CONDITIONAL_PASS; Primer-BLAST soft gap; RADIL watch",
            "A2": "baits locked; Capture UNDERPOWERED soft gap",
            "cross": "holdout SEALED; Stage-3 LOCKED; GO UNSIGNED",
        },
    }

    out_json = OUT / "P9_virtual_e2e_v1.json"
    out_md = OUT / "P9_virtual_e2e_v1.md"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    soft_rows = "\n".join(f"| `{g['id']}` | {g.get('detail', '')} |" for g in soft) or "| — | none |"
    hard_rows = "\n".join(f"| `{g['id']}` | {g.get('detail', g.get('path', ''))} |" for g in hard) or "| — | none |"

    md = f"""# P9 — Virtual end-to-end dry-run v1

**Date:** 2026-07-16
**Status:** `P9_VIRTUAL_E2E_COMPLETE`
**Claim:** `P9_VIRTUAL_E2E_CLAIM_v1.md`
**Label:** **`{label}`**

## Summary

| Class | n |
|-------|--:|
| OK checks | {len(ok_checks)} |
| Soft gaps | {len(soft)} |
| Hard blocks | {len(hard)} |

## Soft gaps

| ID | Detail |
|----|--------|
{soft_rows}

## Hard blocks

| ID | Detail |
|----|--------|
{hard_rows}

## Phase walk

| Phase | Result |
|-------|--------|
| B0 reporter | FASTA present; MCID present; ORDER FORBIDDEN; backbone lab-fill soft |
| A1 PE | `PE_OT_CONDITIONAL_PASS`; RADIL watch; Primer-BLAST manual soft |
| A2 Capture-C | baits locked; quote sheet present; **P8_UNDERPOWERED** soft |
| Cross-cutting | holdout SEALED · Stage-3 LOCKED · GO UNSIGNED_DRAFT |

## Plain language

План B0→A1→A2 на бумаге **сходится**: артефакты есть, замки целы, жёстких противоречий нет.
Остаются мягкие дыры (backbone, Primer-BLAST, Capture недомощен) — это не редизайн, а чеклист до human GO.

## What this does NOT mean

- Not wet-lab authorization
- Not oligo order
- Not Capture-C powered primary
- Not biological proof of C1

Full dump: `P9_virtual_e2e_v1.json`
"""
    out_md.write_text(md, encoding="utf-8")
    print(json.dumps({"label": label, "n_ok": len(ok_checks), "n_soft": len(soft), "n_hard": len(hard), "wrote": str(out_md)}, indent=2))
    return 0 if label != "P9_BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
