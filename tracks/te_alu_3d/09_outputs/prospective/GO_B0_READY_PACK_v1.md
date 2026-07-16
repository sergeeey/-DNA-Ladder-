# GO B0 ready pack — awaiting human signature

**Date:** 2026-07-16  
**Status:** `READY_FOR_SIGNATURE` · still **NO-GO** until signature block filled  
**Recommended authorize:** **Phase B0 only** (activity reporter)  
**Not included:** A1 PE · A2 Capture · OT oligos · holdout unblind

This pack does **not** place an oligo order. It makes B0 one signature away.

---

## What B0 unlocks (after you sign)

| Allowed | Forbidden |
|---------|-----------|
| Order **B-min-REF** + **B-min-ALT** (301 bp) inserts | pegRNA / ngRNA / OT primers |
| Order chosen reporter backbone + empty-backbone control | Capture-C baits |
| Transfection plan under MCID below | Claiming loop disruption |
| Escalate to 1 kb / 2 kb only if B-min null/equivocal | Moving locked E/P · unsealing holdout |

---

## Frozen specs (do not edit at signature time)

```yaml
variant: chr11:62753923 A>G
constructs_first_po:
  - B-min-REF: pilot_scaffold/data/cultivation/c1_reporter_minimal_301bp_REF.fa
  - B-min-ALT: pilot_scaffold/data/cultivation/c1_reporter_minimal_301bp_ALT.fa
cells: HUDEP-2 preferred (K562 = demoted claim)
mcid: "|log2(ALT/REF)| >= 0.5 in >=2 independent transfections"
power_desk: P8_ADEQUATE at n_tx=6 (mid noise)
primary_endpoint: reporter activity only (M3 lean)
```

Desk kill-sprint: C1 not destroyed (P1–P10). Still **not** wet biology.

---

## Lab must freeze before PO (fill at signature or same day)

| Item | Desk nominate | Sign / confirm |
|------|---------------|----------------|
| Backbone vendor / plasmid ID | `Promega_pGL4.23_luc2_minP_E8411` | ________________ |
| Readout (luc / FP) | luc2 + Renilla norm | ________________ |
| Cloning method | gBlock ± Gibson | ________________ |
| Partner lab | — | ________________ |
| Budget cap (USD) | — | ________________ |

See `B0_backbone_desk_nominate_v1.md` · `B0_PO_draft_v1.md` · `B0_transfection_day_card_v1.md`.

---

## Signature block — copy into `GO_note_draft_C1_B_first_v1.md`

Reply in chat with one line (agent will apply it), **or** paste yourself:

```yaml
go_version: GO_B0_v1
authorized_phases: [B0]
signer_name: <REQUIRED>
signer_role: <REQUIRED>
date_signed: 2026-07-16   # or today
budget_cap_usd: <number or null>
partner_lab: <name or null>
backbone_id: <REQUIRED before PO>
notes: "B0 only; B-min REF/ALT + backbone; no PE/Capture/OT"
```

**Machine rule:** `date_signed: null` → NO-GO · oligos FORBIDDEN.

---

## Linked

- `GO_note_draft_C1_B_first_v1.md` — master authorization file  
- `BranchB_oligo_checklist_v1.md` — shopping list  
- `B0_backbone_desk_nominate_v1.md` · `B0_PO_draft_v1.md` · `B0_insert_verify_primers_desk_v1.md`  
- `B0_transfection_day_card_v1.md` · `B0_bmin_hash_spotcheck_v1.json`  
- `GO_A1_READY_PACK_v1.md` · `A2_CAPTURE_HELD_v1.md` · `HOLDOUT_REMAIN_SEALED_v1.md`  
- `P8_power_simulation_v1.md` · `P9_virtual_e2e_v1.md` · `P10_immutable_handoff_v1.md`  
