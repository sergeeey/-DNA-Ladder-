---
experiment: exp_topology_community_crispr_eg
date: 2026-07-20
ladder_tier: Standard
question_type: Predictive
status: REJECT
candidate_id: C-B1
candidate_alias: C-B1-topology-crispr-eg
source: standing_order_post_C-A1_close + Deep Research next-fruit slot
accession_freeze: ACCESSION_FREEZE_v1.md
rE2G_audit: ENCODE_R2G_FEATURE_AUDIT_v1.md
t0_status: PASS_FREEZE
kill_test: FAIL_KILL
delta_auc: -0.0073
---

# Claim: CRE-community topology adds predictive ΔAUC over distance+activity+SE for CRISPR E–G (K562)

## Status

**REJECT** (`FAIL_KILL`) — chromosome-holdout ΔAUC = **−0.0073** (< 0.02 kill).  
See `decision.md` and `results/kill_test_chr_holdout.json`.

**ID note:** Deep Research registry `C-B1` originally scored AluY@CTCF+RAD21+AG (TE track).
After C-A1 `INCONCLUSIVE_CROSS_CELL` close, standing order promotes **this** Predictive
estimand into the C-B1 desk slot. The TE AluY/AG candidate remains **PARKED** as
`C-B1-TE-AluY-AG`.

## EstimandOps L0

**Question type:** Predictive.

Among frozen CRISPR-validated enhancer–gene (E–G) pairs in K562, do **CRE-community
topology** features improve discrimination of CRISPR-positive vs negative pairs by
**ΔAUC ≥ 0.05** relative to baseline **`log10_distance + activity_els + se_membership`**
(same universe, chromosome holdout)?

Explicitly **not causal**. Explicitly **not** novelty for “any 3D contact feature”
(rE2G already uses contact/loops — audit `SURVIVES_WITH_REDESIGN`).

## Redesign note (locked before fit)

Original prereg used SE-only baseline. Per rE2G audit + standing kill-test protocol,
baseline was **amended before any ΔAUC fit** to:

| Feature | Definition |
|---------|------------|
| `log10_distance` | log10(\|enhancer midpoint − TSS\| + 1) |
| `activity_els` | binary overlap of enhancer with K562 cCRE **pELS or dELS** (`ENCFF210CAN`) |
| `se_membership` | binary overlap with dbSUPER K562 SE (`k562_super_enhancers_grch38.json`) |

Topology (incremental):

| Feature | Definition |
|---------|------------|
| `enh_loop_degree` | # unique Hi-C loops (`ENCFF693XIL`) incident on anchors overlapping enhancer |
| `prom_loop_degree` | same for TSS ± 2 kb |
| `shared_community_size` | connected-component size if E and P share a loop-graph component; else 0 |
| `min_loop_span_rank_inv` | 1 / rank of shortest direct E–P spanning loop on chrom (worst if none) |

## Frozen claim (pre-results)

> On the frozen K562 CRISPR E–G benchmark (chr20–22 holdout), baseline+topology achieves
> **ΔAUC ≥ 0.05** over baseline (ROC-AUC primary).

**Kill:** ΔAUC < 0.02 → REJECT.  
**Support:** ΔAUC ≥ 0.05.  
**Gray:** 0.02 ≤ ΔAUC < 0.05 → INCONCLUSIVE.

## Result (post-holdout)

ΔAUC = **−0.0073** → **FAIL_KILL / REJECT**. Distance-alone AUC = 0.8796 (positive control PASS).

## Label

Column **`Regulated`** (`TRUE` = positive) in
`EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz`.

## Novelty check

See prior table in experiment history: distinct from closed SE enrichment nulls and C-A1;
not novel as “first 3D E–G predictor.” Honest gap was higher-order community topology over
a distance+activity+SE baseline — now tested and rejected at desk MCID.

## Forbidden claim language

- Causal community → regulation
- “3D/loops novel for CRISPR E–G” (false vs rE2G)
- Reopening closed SE nulls; wet / holdout unblind / C1 / TE AluY+AG under this folder
