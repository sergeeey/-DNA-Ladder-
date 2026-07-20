---
experiment: exp_l1hs_ctcf_loop_anchors
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: REJECT
candidate_id: C-L1
candidate_alias: C-L1-l1hs-ctcf-loop-anchors
source: Standing order — TRUE C-L1 (NOT cross-cell transfer; that remains C-L1-crosscell-original)
decision_gate: FAIL_KILL
null_results: null_results/20260720-l1hs-ctcf-loop-anchor-enrichment.md
---

# Claim: L1HS 5′UTR enrichment at CTCF∩Hi-C loop anchors vs matched background CTCF

## Status

**REJECT** (`FAIL_KILL`) — Standard tier; desk **CLOSED**.  
K562 OR **0.143** (umap≥0.3 same); HCT116 OR **0.200**. Both &lt; 1.1.  
See `decision.md`. Autonomous wave **STOP** after wave summary.

## EstimandOps L0

**Question type:** Descriptive.

In K562 (primary) and HCT116 (replication if data OK), among **CTCF-bound Hi-C loop
anchors**, is overlap with **L1HS 5′UTR** (strand-aware first 2 kb of RepeatMasker
`repName=L1HS`) enriched at **OR ≥ 1.4** vs **1:1 matched background CTCF** midpoint
windows (CTCF peaks not overlapping Hi-C anchors), matched on chrom + length_bin +
umap_quartile **before** L1HS attach?

User phrasing “matched non-TE CTCF sites” is operationalized as **matched background
(non-anchor) CTCF** — not “zero-TE CTCF” (that would force control L1HS rate = 0 and
make Fisher OR ill-posed). Honest remapping noted here pre-results.

Explicitly **not** C-A1 AluSz ChIA vs Hi-C discordance. Explicitly **not** cross-cell
transfer (Deep Research original C-L1).

## Frozen claim

> OR(L1HS 5′UTR | CTCF∩Hi-C anchor) ≥ **1.4** vs matched background CTCF windows in K562.

**Falsify:** after mean umap ≥ 0.3 on both arms, OR **< 1.1** → **REJECT**.

Gray zone 1.1 ≤ OR < 1.4 → **INCONCLUSIVE** / fail-to-support.

## Primary estimand

| Element | Definition |
|---------|------------|
| Case | **CTCF peaks** overlapping ≥1 merged Hi-C loop anchor |
| Control | 1:1 matched **background CTCF peaks** (zero Hi-C-anchor overlap) |
| Matching | chrom + CTCF length quartile + umap quartile; seed `20260720`; before L1HS |
| Exposure | ≥1 bp overlap with L1HS **5′UTR proxy**: first 2000 bp of each L1HS (strand + → genoStart; strand − → genoEnd−2000) |
| Summary | Fisher OR + Woolf 95% CI |
| SUPPORT | OR ≥ 1.4 (K562 primary) |
| Kill | OR < 1.1 after umap ≥ 0.3 |

**Unit note (pre-results sparsity / matching gate):** Hi-C-anchor-as-unit (median ~10 kb)
cannot be length-matched to CTCF peaks (~0.4 kb); mid-1 kb windows yield ~0 L1HS hits.
Primary unit = **CTCF peak** on vs off anchor (same class both arms).

## Datasets

| Role | Accession |
|------|-----------|
| K562 Hi-C loops | `ENCFF693XIL` |
| K562 CTCF | `ENCFF769AUF` |
| HCT116 Hi-C | `ENCFF060QTI` |
| HCT116 CTCF | `ENCFF463FGL` |
| TE | UCSC hg38 rmsk `L1HS` |
| Mappability | Hoffman k100 Umap bigWig |

## Forbidden language

Causal L1→CTCF/loop; reopening C-A1/C-H1; wet/holdout/C1.
