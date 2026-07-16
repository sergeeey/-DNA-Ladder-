# P6 — PE/OT robustness desk v1

**Date:** 2026-07-16
**Status:** `P6_PE_OT_COMPLETE`
**Verdict:** **`PE_OT_CONDITIONAL_PASS`**
**Kills:** none
**Disclosures:** K3_SOFT_EXON_WATCH_CFD_ge_0.3, PD1_AND_PD2_BOTH_VIABLE, K4_NGRNA_ALT_HAS_mm_le_2_OR_WEAK, K5_GENOMEWIDE_PRIMER_BLAST_STILL_MANUAL
**Oligo order:** FORBIDDEN

## Claim

`P6_PE_OT_CLAIM_v1.md` (engine2 amended to UCSC OT-verify; remote BLAST abandoned)

## Engine 1 — CRISPOR hg38 (multi-guide)

| Guide | ID | MIT | CFD | OT# | mm≤2 | max exon CFD |
|-------|----|----:|----:|----:|-----:|-------------:|
| PD1 | `197forw` | 69 | 89 | 121 | 0 | 0.37 |
| PD2 | `196rev` | 84 | 92 | 96 | 0 | 0.23 |
| ngRNA_primary | `142rev` | 91 | 93 | 60 | 0 | 0.23 |
| ngRNA_alt | `128rev` | 90 | 94 | 162 | 1 | 0.17 |

### PD1 exon watch

| mm | locus | chrom | CFD |
|---:|-------|-------|----:|
| 3 | exon:RADIL | chr7 | 0.37 |
| 4 | exon:RPAP2 | chr1 | 0.29 |
| 4 | exon:TEX40/RP11-783K16.10 | chr11 | 0.18 |
| 4 | exon:PHF12 | chr17 | 0.06 |

## Engine 2 — UCSC verify of CRISPOR OT coordinates

Verified 4 sites; genomic DNA matches CRISPOR OT seq on **4/4**.

- `exon:RADIL` chr7:4805549 status=OK mm_vs_guide=4 ot_seq_match=True
- `exon:RPAP2` chr1:92388950 status=OK mm_vs_guide=5 ot_seq_match=True
- `exon:TEX40/RP11-783K16.10` chr11:64300836 status=OK mm_vs_guide=5 ot_seq_match=True
- `exon:PHF12` chr17:28951309 status=OK mm_vs_guide=5 ot_seq_match=True

## Primers

| ID | Locus | fwd in amp | rev in amp | polyA/T | Genome Primer-BLAST |
|----|-------|:----------:|:----------:|:-------:|---------------------|
| OT0 | C1_on_target | True | True | False | PENDING_MANUAL |
| OT1 | RADIL_exon | True | True | False | PENDING_MANUAL |
| OT2 | KDM2B_intron | True | True | True | PENDING_MANUAL |
| OT3 | RPAP2_exon | True | True | False | PENDING_MANUAL |
| OT4 | UPF3A_intron | True | True | False | PENDING_MANUAL |

## Recommended desk stack (still NO order)

- pegRNA: **PD1** (backup: PD2)
- ngRNA: **GTTCTAAGGTTAGGCCGAGG** (alt: WEAKER_mm_le_2)
- Watch: **RADIL** (and other exon CFD≥0.15)

## Plain language

PD1 не единственный выживший: PD2 тоже без mm≤2. Предпочтительный ngRNA чище альтернативы (у alt есть mm≤2). Сайты OT из CRISPOR перепроверяются по UCSC-последовательности. Праймеры садятся на заявленные ампликоны; полный Primer-BLAST по геному — ещё руками до заказа.

## What this does NOT mean

- Not wet OT NGS
- Not full Cas-OFFinder / NCBI Primer-BLAST completion
- Not oligo GO

JSON: `P6_PE_OT_robustness_v1.json`
