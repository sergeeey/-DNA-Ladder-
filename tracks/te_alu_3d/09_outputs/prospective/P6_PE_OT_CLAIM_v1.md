# P6 — PE/OT robustness + Primer-BLAST desk

**Status:** PRE-REGISTERED (before results)  
**Date locked:** 2026-07-16  
**L0:** Predictive desk — genome-wide OT concordance + primer uniqueness for PD1 path.  
**Not wet-lab. Not oligo order. Not holdout.**

## Inputs (frozen)

| Item | Value |
|------|-------|
| pegRNA PD1 | `CGTCCGATAAGCCCTGCCCC` + PAM `CGG` (CRISPOR `197forw`) |
| Alt peg PD2 | `TGGCTAAGGGGCGGGACTTC` + PAM `CGG` (CRISPOR `196rev`) |
| Primary ngRNA | `GTTCTAAGGTTAGGCCGAGG` (CRISPOR `142rev`, MIT91) |
| Alt ngRNA | `CCGAGGTGGGCGGAGCTAAT` (CRISPOR `128rev`) |
| Engine 1 | CRISPOR hg38 batch `aurVfmrzWeRL946FQvDv` (existing) |
| Engine 2 | UCSC sequence verify of CRISPOR OT coordinates (independent fetch; **not** Cas-OFFinder — no local hg38 dump). Remote NCBI BLAST attempted then abandoned (hung). |
| Primers | Amp-local UCSC check for 5 pairs; **genome-wide Primer-BLAST remains manual gate** |

## Pre-registered kills / labels

| ID | Rule |
|----|------|
| **K1_HARD** | Engine1 PD1 has any OT with mm ≤ 2 |
| **K2_HARD** | Verified UCSC DNA at a CRISPOR OT site has ≤2 mismatches to guideSeq **and** lies outside C1 ±1 kb |
| **K3_SOFT** | Engine1 PD1 exon OT with CFD ≥ 0.3 (watchlist must include it) |
| **K4_FRAGILE** | Only one of {PD1, PD2} has mm≤2 = 0 and MIT ≥ 50 |
| **K5_PRIMER_FAIL** | Amp-local check: fwd/rev not found on stated amplicon |
| **K5_MANUAL** | Genome-wide Primer-BLAST still required before oligo order (disclosure, not auto-kill) |
| **PASS_CONDITIONAL** | No K1/K2/K4/K5; K3/K5_MANUAL allowed as disclosures |

## Branch consequence

| Verdict | Meaning |
|---------|---------|
| `PE_OT_HARD_FAIL` | K1 or K2 → do not advance PD1 as primary edit design |
| `PE_OT_FRAGILE` | K4 without hard fails → need backup peg/ngRNA before wet |
| `PRIMERS_NOT_READY` | K5 → redesign before amplicon-NGS panel |
| `PE_OT_CONDITIONAL_PASS` | Survives hard kills; watches documented; order still FORBIDDEN |

## Explicit non-goals

- Not Cas-OFFinder full hg38 (no local genome dump in-repo)
- Not wet PCR validation
- Not oligo PO / Phase A1 GO

## Script / arts

`pilot_scaffold/scripts/run_p6_pe_ot_primer_desk.py`  
Out: `P6_PE_OT_robustness_v1.md` / `.json`
