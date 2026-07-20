---
experiment: exp_microc_vs_hic_alu_anchors
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: BLOCKED_DATA
candidate_id: C-I1
candidate_alias: C-I1-microc-vs-hic-alu-anchors
source: Standing order post C-H1 SUPPORT — TRUE C-I1 = Micro-C vs Hi-C (Deep Research original C-H1)
decision_gate: BLOCKED_DATA
---

# Claim: Micro-C vs Hi-C Alu-anchor recovery differential

## Status

**BLOCKED_DATA** — Standard tier; desk **CLOSED** at T0.  
No released processed Micro-C loop bedpe (ENCODE assay absent; 4DN = pairs/hic/mcool only).  
OR not computed. See `decision.md`. Next fruit: **C-L1**.

## EstimandOps L0

**Question type:** Descriptive.

In ≥1 preferred cell type (prefer **HFFc6 / H1 / GM12878 / K562** with released processed
loops), among processed loop call sets from **Micro-C** and matched **Hi-C**, does Alu
(primary **AluSz**) membership at anchors differ with **OR ≥ 1.5** (Micro-C vs Hi-C)?

Explicitly **not causal**. Explicitly **not** C-A1 Pol II ChIA-PET discordance.
Explicitly **not** C-H1 TE-derived pELS Gnocchi (SUPPORT 2026-07-20).

## Frozen claim (pre-results)

> Micro-C recovers AluSz-anchor loops at **OR ≥ 1.5** vs matched Hi-C anchors in ≥1 cell
> type with processed GRCh38 loop bedpe.

**Falsification:** after umap ≥ 0.3, OR **< 1.1** → **REJECT**.

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | Loop anchors from frozen processed bedpe (GRCh38) |
| Exposure | AluSz overlap on fixed midpoint windows (≥1 kb pad; C-A1 convention) |
| Contrast | Micro-C anchors vs matched Hi-C anchors (same cell type) |
| Summary | Fisher OR + Woolf 95% CI |
| MCID (SUPPORT) | OR ≥ 1.5 in ≥1 cell type |
| Kill | OR < 1.1 after umap ≥ 0.3 |

## Datasets — T0 probe targets

| Role | Source |
|------|--------|
| Micro-C processed loop bedpe | ENCODE / 4DN (GRCh38) |
| Matched Hi-C loops | Same cell; prefer prior freezes (`ENCFF693XIL` K562 / `ENCFF781ASD` GM12878) if cell matches |
| TE / umap | UCSC rmsk; Hoffman Umap k100 |

If no processed Micro-C loop bedpe → terminal **`BLOCKED_DATA`** (still merge prereg);
fallback next fruit **C-L1**.

## ID note

Deep Research listed this estimand as **C-H1**. Standing order filled C-H1 with TE-pELS
Gnocchi; this Micro-C desk is **C-I1**. Registry AluJo NC title for C-I1 remains a
C-A1-internal control (not this folder).

## Forbidden claim language

- Causal Micro-C superiority / TE → loop mechanism
- Calling loops from pairs/mcool without new freeze
- Reopening C-A1 / C-H1 Gnocchi / SE nulls / wet / holdout / C1
