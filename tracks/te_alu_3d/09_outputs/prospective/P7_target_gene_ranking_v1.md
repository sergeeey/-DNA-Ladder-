# P7 — Target gene ranking v1

**Date:** 2026-07-16
**Status:** `P7_TARGET_GENE_COMPLETE`
**Claim:** `P7_TARGET_GENE_CLAIM_v1.md`
**Label:** **`P7_RANKED_EXPLORATORY`**
**P redefinition:** **FORBIDDEN** (TSS inside locked P: **0**)

## Inputs

| Source | Status |
|--------|--------|
| Ensembl genes in query | 69 raw → 68 unique |
| HUDEP-2 CTCF (local BED) | 21 intervals in/near window |
| K562 ATAC proxy | 88 intervals (not HUDEP-2) |
| HUDEP-2 RNA-seq | **UNAVAILABLE** |

## Ranked candidates (top)

| Rank | Gene | Score | Biotype | dist TSS-C1 | body∩P | TSS∈P |
|-----:|------|------:|---------|------------:|:------:|:-----:|
| 1 | **HNRNPUL2-BSCL2** | 6 | protein_coding | 26539 | Y | n |
| 2 | **BSCL2** | 5 | protein_coding | 44062 | Y | n |
| 3 | **TAF6L** | 4 | protein_coding | 17384 | n | n |
| 4 | **ENSG00000267811** | 4 | lncRNA | 17683 | n | n |
| 5 | **ENSG00000269176** | 4 | lncRNA | 32862 | n | n |
| 6 | **TMEM179B** | 4 | protein_coding | 33452 | n | n |
| 7 | **MIR6748** | 4 | miRNA | 35892 | n | n |
| 8 | **TMEM223** | 4 | protein_coding | 38099 | n | n |
| 9 | **ZBTB3** | 3 | protein_coding | 4912 | n | n |
| 10 | **POLR2G** | 3 | protein_coding | 7530 | n | n |
| 11 | **TTC9C** | 3 | protein_coding | 26236 | n | n |
| 12 | **HNRNPUL2** | 3 | protein_coding | 26286 | n | n |

## Prior desk nominations (cross-check)

| Gene | This ranking |
|------|----------------|
| LRRN4CL | score 3 · rank ~17 |
| BSCL2 | score 5 · rank ~2 |
| ZBTB3 | score 3 · rank ~9 |
| POLR2G | score 3 · rank ~10 |
| HNRNPUL2-BSCL2 | score 6 · rank ~1 |

## Soft / hard reading

- Exploratory only — **not** an assigned wet-lab expression target.
- Locked P has **no** protein-coding TSS inside → do **not** move P.
- Missing HUDEP-2 RNA keeps uncertainty high even if geometry ranks one gene first.

## Plain language

Кого мерить после edit — пока **не один ген**, а ранжированный список с дырой по HUDEP-2 RNA.
Отсутствие TSS в locked P — находка, не повод двигать якорь.

## What this does NOT mean

- Not «C1 regulates X»
- Not permission to redefine E/P
- Not HUDEP-2 expression proof

Full dump: `P7_target_gene_ranking_v1.json`
