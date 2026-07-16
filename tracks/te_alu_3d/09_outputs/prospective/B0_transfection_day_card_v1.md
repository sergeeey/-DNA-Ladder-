# B0 transfection day card v1

**Date:** 2026-07-16  
**Status:** `DESK_PROTOCOL_CARD` · wet only after B0 GO + sequenced plasmids  
**Cells:** HUDEP-2 preferred (K562 = demoted claim)

---

## Pre-flight (day −1)

- [ ] Plasmids Sanger-confirmed: REF=`A` / ALT=`G` at insert index 150  
- [ ] Empty-backbone control prep’d  
- [ ] Dual-luc (or FP) reagents in date  
- [ ] n_tx plan ≥ **6** (P8 mid-noise) across ≥ **2** independent transfection days  
- [ ] Blinded sample labels for readout tech (optional but preferred)

---

## Day 0 — transfect

```yaml
arms:
  - empty_backbone
  - B_min_REF
  - B_min_ALT
normalize: co_transfection_control_or_total_protein_per_lab_SOP
replicate_rule: ">=2 independent_transfection_days"
```

Do **not** add PE reagents on B0 days.

---

## Readout + MCID

```text
primary: log2(ALT/REF) after empty-backbone / transfection normalization
MCID: |log2(ALT/REF)| >= 0.5 in >=2 independent transfection days
fail: no reproducible direction, or |effect| < MCID
```

Escalation if null/equivocal: **B-1kb** then **B-2kb** before biological B− (`BranchB_oligo_checklist_v1.md`).

---

## What B0 does / does not mean

| Does | Does not |
|------|----------|
| Speaks to autonomous M3 activity lean | Prove loop disruption |
| Can escalate or kill reporter path | Authorize PE / Capture |
| | Touch holdout / move E/P |

---

## Linked

- `P8_power_simulation_v1.md`  
- `GO_note_draft_C1_B_first_v1.md`  
- `B0_PO_draft_v1.md`  
