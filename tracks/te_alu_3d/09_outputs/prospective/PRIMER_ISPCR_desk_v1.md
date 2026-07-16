# Primer in-silico PCR desk v1

**Date:** 2026-07-16
**Status:** `PRIMER_ISPCR_DESK_COMPLETE`
**Claim:** `PRIMER_ISPCR_CLAIM_v1.md`
**Label:** **`PRIMER_DESK_GAPS`**
**Engine:** UCSC hgPcr hg38
**Oligo order:** FORBIDDEN
**NCBI Primer-BLAST:** still recommended as human confirm before A1 order

## Results

| ID | Locus | Label | n products | Products | Flag |
|----|-------|-------|----------:|----------|------|
| OT0 | C1_on_target | **ISPCR_PASS** | 1 | chr11:62753823-62754058(236bp) | edit_verify |
| OT1 | RADIL_exon | **ISPCR_PASS** | 1 | chr7:4805443-4805729(287bp) | priority_watch |
| OT2 | KDM2B_intron_DEPRECATED | **ISPCR_SKIP_DEPRECATED** | None | — | DEPRECATED_Alu_like_ISPCR_NONE |
| OT2b | KDM2B_intron | **ISPCR_WARN** | 1 | chr12:121534219-121534516(298bp) | redesign_v1_polyA_in_body |
| OT3 | RPAP2_exon | **ISPCR_PASS** | 1 | chr1:92388850-92389070(221bp) | — |
| OT4 | UPF3A_intron | **ISPCR_PASS** | 1 | chr13:114290081-114290322(242bp) | — |

## Reading

- **ISPCR_PASS** — single product at expected locus
- **ISPCR_WARN** — single product with soft mismatch and/or polyA flag (OT2)
- **ISPCR_MULTI / NONE** — redesign before order
- UCSC isPCR ≠ full NCBI Primer-BLAST sensitivity

## Manual confirm slots (optional)

| ID | NCBI Primer-BLAST done? | Notes |
|----|:-----------------------:|-------|
| OT0 | ☐ | |
| OT1 | ☐ | RADIL |
| OT2 | ☐ | polyA — redesign if PCR poor |
| OT3 | ☐ | |
| OT4 | ☐ | |

## Plain language

Проверили, не даёт ли пара праймеров кучу продуктов по hg38. Это desk-фильтр до A1, не разрешение заказывать олиго.

## What this does NOT mean

- Not A1 GO
- Not wet PCR validation
- Not replacement for NCBI Primer-BLAST if lab SOP requires it

Full dump: `PRIMER_ISPCR_desk_v1.json`
