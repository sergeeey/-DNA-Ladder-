# Branch B — oligo / construct checklist v1

**Date:** 2026-07-15  
**Status:** `DESK_CHECKLIST` · **ORDER FORBIDDEN** until `GO_note_draft_C1_B_first_v1.md` Phase B0 signed  
**Purpose:** ready-to-copy shopping list for activity reporter (M3), with NDE escalation ladder

---

## Escalation ladder (do not skip)

```text
B-min (301 bp)  →  if null / equivocal  →  B-1kb  →  if null  →  B-2kb
Biological B− claim only after full ladder (NDE B1).
```

---

## Sequence inserts (on disk — do not re-extract without amendment)

| SKU id | Allele | Window GRCh38 | Len | FASTA |
|--------|--------|---------------|----:|-------|
| **B-min-REF** | A | chr11:62753773-62754073 | 301 | `pilot_scaffold/data/cultivation/c1_reporter_minimal_301bp_REF.fa` |
| **B-min-ALT** | G | same | 301 | `.../c1_reporter_minimal_301bp_ALT.fa` |
| B-1kb-REF | A | chr11:62753423-62754423 | 1001 | `.../c1_reporter_context_1kb_REF.fa` |
| B-1kb-ALT | G | same | 1001 | `.../c1_reporter_context_1kb_ALT.fa` |
| B-2kb-REF | A | chr11:62752923-62754923 | 2001 | `.../c1_reporter_context_2kb_REF.fa` |
| B-2kb-ALT | G | same | 2001 | `.../c1_reporter_context_2kb_ALT.fa` |

C1 index within inserts: 150 / 500 / 1000 (0-based) per `BranchB_reporter_sequences_meta.json`.

**First PO (if B0 GO):** order **only B-min-REF + B-min-ALT** (+ backbone / cloning primers). Hold 1 kb / 2 kb as optional line items.

---

## Cloning / backbone (lab fills before order)

| Item | Desk default | Freeze at GO |
|------|--------------|--------------|
| Reporter backbone | **nominate:** Promega E8411 pGL4.23[luc2/minP] (`B0_backbone_desk_nominate_v1.md`) | ☐ paste `backbone_id` in GO |
| Insert orientation | sense as genomic + | ☐ confirm |
| Cloning method | IDT gBlock ± Gibson after MCS map | ☐ _______ |
| Antibiotic | lab standard | ☐ _______ |
| Empty backbone control | required | ☐ |
| Scramble insert | optional | ☐ |
| C2 A>T allelic competitor | optional later | ☐ not in B0 default |

---

## PCR / sequencing oligos

| Purpose | Status | Notes |
|---------|--------|-------|
| Insert verify F/R | **DESK DONE** | `B0-IV-F/R` in `B0_insert_verify_primers_desk_v1.md` (insert-internal) |
| Sanger of C1 base in plasmid | **DESK DONE** | `B0-SG-F/R` — covers index 150 A/G |
| Junction insert–backbone | **BLOCKED** | needs frozen backbone MCS map |
| qPCR / RNA (if FP not used) | optional | not required for luciferase MCID |

PO draft line items: `B0_PO_draft_v1.md`. Hash spotcheck: `B0_bmin_hash_spotcheck_v1.json`.

---

## Transfection plan (when GO)

```yaml
cell: HUDEP-2_preferred  # K562_ok_first_pass_demoted_claim
replicates: >=2 independent_transfections
readout: luc_or_FP_ratio_ALT_over_REF_normalized_to_transfection_control
mcid: "|log2(ALT/REF)| >= 0.5"
fail: no_reproducible_direction
```

---

## PE oligos — **out of scope for B0**

pegRNA / ngRNA live under Phase A1 of GO-note. Do not mix into Branch B PO.

Frozen A1 spacers (reference only):

```text
PD1 spacer:  CGTCCGATAAGCCCTGCCCC + PAM CGG
ngRNA:       GTTCTAAGGTTAGGCCGAGG  (primary)
```

---

## Pre-order gate

- [ ] `GO_note` Phase B0 signed (`date_signed` set)  
- [ ] Backbone ID frozen  
- [ ] B-min FASTA hashes / lengths spot-checked  
- [ ] PO SKUs match this checklist version  
- [ ] No Capture-C / PE items on same PO unless A1 also signed  

**If any box unchecked → do not submit PO.**

---

## Linked

- `BranchB_reporter_design_v1.md`  
- `GO_note_draft_C1_B_first_v1.md`  
- `NDE_C1_exhaustion_A_plus_B_v1.md`  
