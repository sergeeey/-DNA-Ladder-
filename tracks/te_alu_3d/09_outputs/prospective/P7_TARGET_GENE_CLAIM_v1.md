# P7 — Target gene ranking (exploratory desk)

**Status:** PRE-REGISTERED (before ranking results)
**Date locked:** 2026-07-16
**L0:** Descriptive / exploratory nomination — not causal claim that C1 regulates gene X
**Not wet-lab. Not holdout. Does not move locked E/P. Does not authorize expression assays.**

## Purpose

Produce a **ranked candidate target list** for C1 with evidence-for / evidence-against / uncertainty — not a single “correct gene”.

Hard constraint from kill-sprint:

> Absence of TSS inside locked P must **not** be bypassed by redefining P after viewing data.

## Locked geometry (frozen)

| Anchor | GRCh38 |
|--------|--------|
| C1 | `chr11:62753923 A>G` |
| E | `chr11:62390000-62395000` |
| P | `chr11:62690000-62695000` |

## Ranking inputs (desk)

| Input | Use | If missing |
|-------|-----|------------|
| GENCODE/Ensembl genes + TSS near E–P–C1 | distance, body overlap, TSS-in-P | hard fail |
| HUDEP-2 CTCF peaks (local) | CTCF near TSS / anchors | soft demote |
| K562 ATAC (proxy only) | chromatin near TSS | soft; label as non-HUDEP |
| HUDEP-2 RNA-seq | expression prior | **UNAVAILABLE** → uncertainty ↑ |
| Loop direction / OE to gene TSS | contact prior | soft; use distance-to-P as proxy only |

## Scoring (pre-registered, additive)

| Signal | Points |
|--------|-------:|
| Gene body overlaps locked P | +3 |
| TSS inside locked P | +5 (expect 0; if >0 → document, still no P move) |
| TSS within 10 kb of P midpoint | +2 |
| TSS within 50 kb of C1 | +2 |
| TSS within 100 kb of C1 | +1 |
| CTCF peak within 5 kb of TSS (HUDEP-2) | +1 |
| ATAC peak within 2 kb of TSS (K562 proxy) | +1 |
| Gene body overlaps locked E | +1 |

**Penalties**

| Signal | Points |
|--------|-------:|
| TSS > 500 kb from C1 and no P-body overlap | −3 |
| Only evidence is K562 ATAC (no P/C1 geometry) | −1 |

## Labels

| ID | Rule |
|----|------|
| **P7_NO_CLEAR_TARGET** | Top score < 4 **or** ≥3 genes within 1 point of top |
| **P7_RANKED_EXPLORATORY** | Clear rank order but HUDEP-2 RNA still missing |
| **P7_BLOCKED** | Cannot fetch gene annotation / geometry broken |

A single gene may be listed as **provisional_top** only with label `P7_RANKED_EXPLORATORY` and explicit “not assigned for wet RNA claims”.

## Forbidden

- Moving E or P
- Claiming “C1 regulates GENE”
- Using ClinVar/consequence as ranking feature
- Treating K562 ATAC as HUDEP-2 expression

## Arts

Script: `pilot_scaffold/scripts/run_p7_target_gene_ranking.py`
Out: `P7_target_gene_ranking_v1.md` / `.json`
