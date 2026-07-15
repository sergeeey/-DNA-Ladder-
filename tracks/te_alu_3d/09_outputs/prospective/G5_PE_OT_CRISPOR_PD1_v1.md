# G5 PE genome-wide off-target — PD1 (CRISPOR hg38)

**Date:** 2026-07-15  
**Tool:** [CRISPOR](https://crispor.gi.ucsc.edu/crispor.py?batchId=aurVfmrzWeRL946FQvDv) batch `aurVfmrzWeRL946FQvDv`  
**Guide:** PD1 `CGTCCGATAAGCCCTGCCCC` + PAM `CGG` (PrimeDesign #1)  
**On-target locus:** intron:ZBTB3 (chr11)

## Scores

| Metric | Value | Desk reading |
|--------|------:|--------------|
| MIT specificity | **69** | Medium–high (≥50 often usable) |
| CFD specificity | **89** | High |
| Off-target sites (≤4 mm) | **121** | See histogram |
| Doench'16 / MM / RS3 | 58 / 50 / 109 | Adequate cleavage predictors |
| Graf status | GrafOK | |

## Mismatch histogram (CRISPOR offtargets)

| mm0 | mm1 | mm2 | mm3 | mm4 |
|----:|----:|----:|----:|----:|
| 0 | 0 | 0 | **6** | **115** |

No 0–2 mismatch off-targets (good). Risk concentrated at mm3–4.

## Exon-overlapping off-targets (priority watchlist)

| mm | Locus | CFD (OT) | Chrom |
|---:|-------|---------:|-------|
| 3 | **exon:RADIL** | 0.37 | chr7 |
| 4 | exon:RPAP2 | 0.29 | chr1 |
| 4 | exon:TEX40 / RP11-783K16.10 | 0.18 | chr11 |
| 4 | exon:PHF12 | 0.06 | chr17 |
| 4 | exon:PRKG1 | 0.04 | chr10 |

Highest CFD genomic OT overall: intron:KDM2B (mm4, CFD≈0.40).

## PE3 ngRNA (same CRISPOR batch)

PrimeDesign-nominated ngRNAs found in the same 401 bp window:

| ngRNA spacer | MIT | CFD | OT count | Note |
|--------------|----:|----:|---------:|------|
| `CCGAGGTGGGCGGAGCTAAT` (PD top) | **90** | **94** | 162 | Prefer among PD list |
| `GTTCTAAGGTTAGGCCGAGG` | **91** | **93** | **60** | **Best specificity in window** |
| `TTCTAAGGTTAGGCCGAGGT` | 85 | 94 | 72 | Strong alt |
| `GCCGAGGTGGGCGGAGCTAA` | 30 | 72 | 14999 | **DROP** |
| `TAAGGTTAGGCCGAGGTGGG` | 29 | 54 | 470 | **DROP** |

**Recommendation:** pair PD1 with ngRNA `GTTCTAAGGTTAGGCCGAGG` (MIT91/CFD93, PE3 dist **−46** bp) as primary; `CCGAGGTGGGCGGAGCTAAT` (MIT90, dist **−60**) as alternate.

## Verdict

```text
GENOME_WIDE_OT: CONDITIONAL_PASS
```

- Specificity scores support **desk advancement** of PD1.  
- **Not** a green light for oligo order without:  
  1. Confirm PE3 nick distance for chosen ngRNA vs PD1 cut  
  2. Planned amplicon-NGS OT panel (≥ RADIL, KDM2B, RPAP2, UPF3A) if ever wet  
  3. Explicit wet-lab GO note  

Alu context remains a general PE risk; histogram shows no ultra-close (mm≤2) genome hits for this spacer.

## Files

- `crispor_c1/guides.tsv`, `offtargets.tsv`, `PD1_crispor_summary.json`  
- Linked: `G5_PE_validation_external_C1_v1.md`, `G5_PE_shortlist_C1_desk_v1.md`
