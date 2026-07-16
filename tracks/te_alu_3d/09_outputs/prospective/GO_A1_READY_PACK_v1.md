# GO A1 ready pack — UNSIGNED (PE path)

**Date:** 2026-07-16  
**Status:** `READY_FOR_SIGNATURE_LATER` · **NO-GO** · do **not** authorize with B0 by default  
**Prerequisite recommendation:** complete B0 reporter path first (NDE B-first)

---

## What A1 would unlock (only after separate signature)

| Allowed | Forbidden |
|---------|-----------|
| Order PD1 pegRNA + primary ngRNA | Claiming loop disruption |
| Order OT0/1/2c/3b/4 amplicon primers | Capture baits (A2) |
| PE edit in HUDEP-2 + on-target NGS | Unsealing holdout · moving E/P |
| OT watchlist amplicon-NGS | Treating Capture as powered primary |

---

## Frozen PE specs (reference)

```yaml
edit: chr11:62753923 A>G
peg_spacer: CGTCCGATAAGCCCTGCCCC
PAM: CGG
ngRNA_primary: GTTCTAAGGTTAGGCCGAGG
ngRNA_alt: CCGAGGTGGGCGGAGCTAAT
desk_status: PE_OT_CONDITIONAL_PASS
watch: RADIL_mm3
ot_panel_active: [OT0, OT1, OT2c, OT3b, OT4]
primer_desk: PRIMER_DESK_PASS + PRIMER_BLAT_DESK_PASS
```

Arts: `G5_PE_OT_CRISPOR_PD1_v1.md`, `OT_amplicon_primer_panel_desk_v1.md`, `P6_PE_OT_robustness_v1.md`.

---

## Soft gaps still open for A1

- Manual NCBI Primer-BLAST confirmation (UCSC isPCR+BLAT already PASS)  
- PBS/RTT oligo sheet freeze at order time from PrimeDesign PD1 row  
- Lab PE enzyme / transfection SOP  

---

## Signature template (do not fill until B0 path decided)

```yaml
go_version: GO_A1_v1
authorized_phases: [A1]          # or [B0, A1] only if explicit joint GO
signer_name: null
signer_role: null
date_signed: null
budget_cap_usd: null
partner_lab: null
notes: "PE + OT panel; no Capture; holdout sealed"
```

**Machine rule:** null `date_signed` → PE oligos FORBIDDEN.

---

## Linked

- `GO_note_draft_C1_B_first_v1.md`  
- `GO_B0_READY_PACK_v1.md`  
- `CaptureC_bait_quote_sheet_v1.md` (A2 pricing only)  
