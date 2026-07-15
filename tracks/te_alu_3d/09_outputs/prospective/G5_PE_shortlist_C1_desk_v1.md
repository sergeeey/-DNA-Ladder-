# G5 PE shortlist — C1 A>G (desk only)

**Status:** `DESK_ONLY` · **NO guide ordering** · wet-lab STOPPED  
**Variant:** `chr11:62753923 A>G` (GRCh38) · AluSz  
**Method:** local heuristic SpCas9 PE2-style candidates (not PrimeDesign).

## Decision

| Item | Result |
|------|--------|
| Classic SpCas9 BE | FAIL (prior desk: pos 17–18) |
| Prime editing | **CONDITIONAL path** — candidates below |
| Wet-lab order | **FORBIDDEN** until panel/MCID freeze |

Found **24** PAM geometries with edit within 30 bp of cut; showing top 8.

## Top candidates

| rank | strand | PAM@ | spacer | edit→cut (bp) | PBS | RTT |
|-----:|:------:|-----:|--------|--------------:|-----|-----|
| 1 | + | 62753919 | `CGTCCGATAAGCCCTGCCCC` | 7 | `GCAGGGCTTATCG` | `CCCCGGAGGTCC` |
| 2 | - | 62753917 | `GGCTAAGGGGCGGGACTTCC` | 0 | `AGTCCCGCCCCTT` | `GGACCTC` |
| 3 | - | 62753916 | `GCTAAGGGGCGGGACTTCCG` | 1 | `AAGTCCCGCCCCT` | `GGACCTCC` |
| 4 | - | 62753918 | `TGGCTAAGGGGCGGGACTTC` | 1 | `GTCCCGCCCCTTA` | `GGGACCTC` |
| 5 | - | 62753915 | `CTAAGGGGCGGGACTTCCGG` | 2 | `GAAGTCCCGCCCC` | `GGACCTCC` |
| 6 | - | 62753911 | `GGGGCGGGACTTCCGGGGGC` | 6 | `CCCGGAAGTCCCG` | `GGACCTCCGGG` |
| 7 | - | 62753910 | `GGGCGGGACTTCCGGGGGCA` | 7 | `CCCCGGAAGTCCC` | `GGACCTCCGGGG` |
| 8 | - | 62753926 | `GCGGAGGGTGGCTAAGGGGC` | 9 | `CCTTAGCCACCCT` | `TAAGGGGCGGGACC` |

## Next validation (before any order)

1. Recompute in PrimeDesign / Easy-Prime / pegLIT  
2. PE3 nicking sgRNA opposite strand  
3. Cas-OFFinder / CRISPRitz off-targets for spacer  
4. Confirm no essential splice disruption outside intended A>G  

## Gate linkage

- Architecture G4b needs this edit verified in HUDEP-2 clones  
- Activity Branch B can use same PE path for expression readout  

JSON: `G5_PE_shortlist_C1_desk_v1.json`
