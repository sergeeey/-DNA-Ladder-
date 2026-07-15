# G5 PE external validation — C1 (Step 1)

**Date:** 2026-07-15  
**Status:** `EXTERNAL_VALIDATED_PARTIAL` · order still **FORBIDDEN**  
**Tools:** PrimeDesign CLI (Pinellolab) + neighborhood off-target scan

## PrimeDesign concordance

| Rank | Spacer | Strand | PAM | Edit dist | Rec. PBS/RTT | First ext nt | vs heuristic |
|-----:|--------|:------:|-----|----------:|--------------|:------------:|--------------|
| 1 | `CGTCCGATAAGCCCTGCCCC` | + | CGG | 8 | 13 / 16 | G | **MATCH** top heuristic |
| 2 | `TGGCTAAGGGGCGGGACTTC` | − | CGG | 1 | 13 / 16 | A | MATCH PD shortlist #4-ish |
| 3 | `GCGGAGGGTGGCTAAGGGGC` | − | GGG | 9 | 13 / 14 | C | FILTER: first C (worse) |

Full CSV: `primedesign_c1/20260715_09.49.42_PrimeDesign.csv` (233 rows).

Recommended PE3 ngRNA examples for PD1 (from PrimeDesign):

| ngRNA spacer | PAM | Distance to peg |
|--------------|-----|----------------:|
| `CCGAGGTGGGCGGAGCTAAT` | GGG | −60 |
| `TAAGGTTAGGCCGAGGTGGG` | CGG | −50 |

## Off-target desk

Target sits in Alu/SINE neighborhood (Ensembl repeats at site). 2 Mb chr11 scan around C1:

- **PD1** (`CGTCCGATAAGCCCTGCCCC`): mm0=1, mm1=0, mm2=0, mm3=0 → risk **LOWER_NEAR_LOCUS**
- **PD2** (`TGGCTAAGGGGCGGGACTTC`): mm0=1, mm1=0, mm2=0, mm3=0 → risk **LOWER_NEAR_LOCUS**
- **PD3** (`GCGGAGGGTGGCTAAGGGGC`): mm0=1, mm1=0, mm2=0, mm3=0 → risk **LOWER_NEAR_LOCUS**

### Interpretation

- Alu context → elevated multi-locus risk expected genome-wide.
- Neighborhood scan is **not** sufficient for wet-lab order.
- **Before order:** Cas-OFFinder / CRISPRitz / CRISPOR genome-wide for PD1 (+ ngRNA).
- Prefer PD1 (PAM_intact, first ext = G, matches independent PrimeDesign).

## Gate decision (Step 1)

| Item | Verdict |
|------|---------|
| PrimeDesign external redesign | **PASS** (PD1 confirmed) |
| Genome-wide off-target (CRISPOR hg38) | **CONDITIONAL_PASS** — MIT 69 / CFD 89; 0×mm0–2; watch **exon:RADIL** (mm3) |
| Near-locus OT scan | COMPLETE |
| Wet-lab GO / oligo order | still **NO** (need ngRNA OT + GO note) |

Details: `G5_PE_OT_CRISPOR_PD1_v1.md`  
JSON: `G5_PE_offtarget_desk_C1_v1.json` + `crispor_c1/PD1_crispor_summary.json`
