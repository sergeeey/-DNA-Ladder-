# B0 backbone — desk nomination v1

**Date:** 2026-07-16  
**Status:** `DESK_NOMINATE` · **not** lab-frozen · **ORDER FORBIDDEN** until GO `backbone_id` set  
**Closes soft gap:** P9 `BACKBONE_TBD` → `BACKBONE_DESK_NOMINATED` (lab still confirms at signature)

---

## Primary desk default (recommended for B0)

| Field | Value |
|-------|-------|
| **backbone_id (paste at GO)** | `Promega_pGL4.23_luc2_minP_E8411` |
| Vendor | Promega |
| Catalog | **E8411** — pGL4.23[*luc2*/minP] Vector |
| Why | Standard minP + luc2 enhancer-assay backbone; empty-backbone control = same vector no insert |
| Readout | Firefly luc2; normalize to co-transfected Renilla (e.g. pRL-TK) or lab dual-luc kit |
| Cloning | MCS upstream of minP — lab maps Gibson overhangs / restriction sites **after** plasmid map on bench |

## Alternate (if lab prefers NanoLuc)

| Field | Value |
|-------|-------|
| **backbone_id** | `Promega_pNL3.1_Nluc_minP_N1031` |
| Catalog | **N1031** — pNL3.1[Nluc/minP] |
| Why | Lower background / smaller enzyme; same minP logic |

## Explicit non-choices (do not auto-order)

- Full strong promoters (CMV/EF1α) — would swamp enhancer-lean readout  
- Unnamed Addgene forks without map on file  
- Custom lab plasmids without written GenBank accession in GO notes  

---

## Freeze rule

```text
Desk may nominate.
Lab (or signer) sets backbone_id in GO signature block.
PO must quote the exact catalog ID from this file or an amended note.
Junction verify primers (insert↔backbone) are designed AFTER backbone_id freeze.
```

---

## Linked

- `GO_B0_READY_PACK_v1.md`  
- `BranchB_oligo_checklist_v1.md`  
- `B0_PO_draft_v1.md`  
- `B0_insert_verify_primers_desk_v1.md`  
