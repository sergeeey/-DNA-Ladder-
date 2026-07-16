# B0 purchase-order DRAFT v1

**Date:** 2026-07-16  
**Status:** `PO_DRAFT` · **DO NOT SUBMIT** until `GO_note` Phase B0 has `date_signed`  
**Purpose:** copy-paste line items for lab purchasing after signature

---

## Gate (all required)

- [ ] `GO_note_draft_C1_B_first_v1.md` → `authorized_phases: [B0]` + `date_signed` set  
- [ ] `backbone_id` matches `B0_backbone_desk_nominate_v1.md` (or written amendment)  
- [ ] No pegRNA / ngRNA / OT / Capture SKUs on this PO  
- [ ] B-min hashes match `B0_bmin_hash_spotcheck_v1.json`  

---

## Line items (first PO)

| # | SKU / description | Qty | Source file / cat |
|--:|-------------------|----:|-------------------|
| 1 | **B-min-REF** gBlock / dsDNA 301 bp REF(A) | 1 | `c1_reporter_minimal_301bp_REF.fa` |
| 2 | **B-min-ALT** gBlock / dsDNA 301 bp ALT(G) | 1 | `c1_reporter_minimal_301bp_ALT.fa` |
| 3 | Reporter backbone | 1 | **default:** Promega E8411 pGL4.23[luc2/minP] |
| 4 | Empty-backbone control | 1 | same backbone, no insert |
| 5 | Dual-luc / Renilla control (if firefly) | 1 | lab kit (e.g. pRL-TK) |
| 6 | **B0-IV-F** oligo | 1 | `CTTGCCACTCCAAAACAATCGC` |
| 7 | **B0-IV-R** oligo | 1 | `GCGTGAGGGAGATGCTTAGG` |
| 8 | **B0-SG-F** oligo | 1 | `AAGCTCTCCCATTAGCTCCGCC` |
| 9 | **B0-SG-R** oligo | 1 | `TACTTCGTGGAGCCGTTGGACG` |

**Hold (do not add to first PO):** B-1kb / B-2kb inserts · PE oligos · OT primers · Capture baits.

**Optional later:** Gibson overhang tails on gBlocks once MCS map confirmed.

---

## Suggested vendor notes

```text
Synthesize REF and ALT as separate gBlocks; do not mix alleles.
Include Sanger of both plasmids at C1 (index 150) before transfection.
PO reference: DNA_Ladder_te_alu_3d_B0_v1
```

---

## Linked

- `BranchB_oligo_checklist_v1.md`  
- `GO_B0_READY_PACK_v1.md`  
- `B0_transfection_day_card_v1.md`  
