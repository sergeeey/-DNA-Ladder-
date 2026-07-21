---
experiment: exp_te_loop_caller_concordance
date: 2026-07-21
ladder_tier: Standard
question_type: Descriptive
status: BLOCKED_DATA
candidate_id: C-F1
candidate_alias: C-F1-mustache-hiccups-te-concordance
source: Standing order post PAUSE_HUMAN («го») — TRUE C-F1 = Mustache vs HiCCUPS TE-anchor concordance
decision_gate: BLOCKED_DATA
---

# Claim: Mustache vs HiCCUPS TE-anchor loop concordance (K562)

## Status

**BLOCKED_DATA** — Standard tier; desk **CLOSED** at T0.  
No released K562 GRCh38 **Mustache** processed loop bedpe on ENCODE.  
HiCCUPS primary remains `ENCFF693XIL`. ΔJaccard **not computed**. See `decision.md`.

Deep Research registry title for C-F1 was Pol II ChIA-exclusive TE density; standing
order fills this desk slot with **Mustache↔HiCCUPS TE-anchor concordance**.

## EstimandOps L0

**Question type:** Descriptive.

In K562, among processed Hi-C loop calls from **Mustache** and **HiCCUPS** on the same
(or matched) library, is Jaccard concordance of loop sets **reduced by ≥ 0.1** for
AluSz/SVA-anchor loops vs matched non-TE-anchor loops?

Explicitly **not causal**. Explicitly **not** wet / pathogenicity. Explicitly **not**
C-A1 Pol II ChIA discordance (already CLOSED).

## Novelty (Gate 0)

- C-A1 T6 caller-swap used **DELTA** (`ENCFF657QKE`) because Mustache was unavailable;
  that does **not** answer Mustache↔HiCCUPS Jaccard on TE anchors.
- This estimand is caller–caller concordance stratified by TE-anchor status, not
  assay discordance OR.

## Frozen claim (pre-results)

> ΔJaccard = Jaccard(non-TE-anchor loops) − Jaccard(AluSz/SVA-anchor loops)
> (Mustache ∩ HiCCUPS / ∪) ≥ **0.1**

**Falsification:** ΔJaccard **< 0.05** → **REJECT**.  
Gray 0.05 ≤ ΔJ < 0.1 → **INCONCLUSIVE**.

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | K562 GRCh38 processed loop bedpe (Mustache + HiCCUPS) |
| HiCCUPS | `ENCFF693XIL` (ENCSR545YBD; preferred_default merged_loops_30) |
| Mustache | ENCODE processed Mustache bedpe (T0 discover) |
| TE anchors | AluSz and/or SVA family overlap on 1 kb midpoint windows (C-A1 convention) |
| Comparator | Matched non-TE anchors (length/GC/umap as available) |
| Summary | Jaccard per stratum; primary **ΔJaccard** (non-TE − TE) |
| SUPPORT | ΔJ ≥ 0.1 |
| Kill | ΔJ < 0.05 |

Optional sanity: CTCF-anchor concordance should remain high (report-only).

## Datasets — T0

| Role | Source |
|------|--------|
| HiCCUPS loops | `ENCFF693XIL` |
| Mustache loops | ENCODE K562 GRCh38 bedpe tagged Mustache |
| TE | UCSC hg38 rmsk |

If Mustache missing → terminal **`BLOCKED_DATA`** (still merge prereg); do **not**
substitute DELTA as Mustache.

## Forbidden claim language

- Causal TE → caller discordance
- Equating DELTA swap to Mustache
- Wet / holdout / C1 E/P / pathogenicity
