# B0 desk status — 2026-07-24

**Status:** `READY_FOR_SIGNATURE` · **UNSIGNED_NO_GO**  
**Oligo / wet purchase:** FORBIDDEN until human signature

## What is already desk-complete

| Artifact | Path |
|----------|------|
| Ready pack | `GO_B0_READY_PACK_v1.md` |
| PO draft | `B0_PO_draft_v1.md` |
| Backbone nominate | `B0_backbone_desk_nominate_v1.md` (pGL4.23 E8411) |
| Day card | `B0_transfection_day_card_v1.md` |
| Oligo checklist | `BranchB_oligo_checklist_v1.md` |
| C1 301 bp REF/ALT | `pilot_scaffold/data/cultivation/c1_reporter_minimal_301bp_*.fa` |

## What agent cannot do

1. Forge `date_signed` / authorize Phase B0  
2. Place oligo or plasmid orders  
3. Unseal holdout or start A1 PE / A2 Capture  

## Unlock line (human only)

Paste into chat or `GO_note_draft_C1_B_first_v1.md`:

```yaml
go_version: GO_B0_v1
authorized_phases: [B0]
date_signed: YYYY-MM-DD
signer: <name>
```

Until then: desk cultivation remains PAUSED for wet; computational G10/G11 are
separate and do not unlock B0.
