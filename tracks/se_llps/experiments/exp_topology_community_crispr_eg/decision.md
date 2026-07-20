# Decision — exp_topology_community_crispr_eg (C-B1)

**Date:** 2026-07-20  
**Status:** `FAIL_KILL` → **REJECT**

## Verdict

Chromosome-holdout kill-test **failed**. CRE-community topology features do **not** add
incremental ROC-AUC over the redesigned baseline
(`log10_distance + activity_els + se_membership`).

| Metric | Value |
|--------|-------|
| AUC baseline | 0.8806 |
| AUC baseline + topology | 0.8733 |
| **ΔAUC (primary)** | **−0.0073** |
| Kill threshold | < 0.02 → FAIL_KILL |
| Support threshold | ≥ 0.05 |
| Distance-alone AUC (positive control) | 0.8796 (**PASS** > 0.55) |
| Leave-one-chr mean ΔAUC | +0.0003 |
| Shuffle-label null mean ΔAUC | +0.0093 (std 0.075) |

**Decision rule applied:** ΔAUC < 0.02 → **FAIL_KILL** / claim **REJECT**.

Artifacts: `results/kill_test_chr_holdout.json`, `results/kill_test_chr_holdout.md`.  
Null filing: `null_results/20260720-topology-community-crispr-eg-delta-auc.md`.

## Gate checklist

| Gate | Status |
|------|--------|
| L0 Predictive classification | DONE |
| claim / controls / notes prereg | DONE |
| Novelty vs closed SE nulls + C-A1 | DONE |
| ENCODE-rE2G adversarial feature audit | **SURVIVES_WITH_REDESIGN** |
| T0 accession freeze | **PASS_FREEZE** |
| Baseline redesign (dist+ELS+SE) locked before fit | DONE |
| Chromosome-holdout ΔAUC kill-test | **DONE → FAIL_KILL** |

## Label (exact)

Positive class = EngreitzLab ensemble column **`Regulated == TRUE`**
(`EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz`, SHA-256 `d0806eb8…e417`).
Not a post-hoc `|EffectSize|≥0.1` rethreshold.

## What this decision does NOT mean

- Does **not** claim 3D contact/loops are useless for E–G prediction (rE2G already uses them).
- Does **not** authorize causal community → regulation language.
- Does **not** reopen closed SE enrichment nulls or TE C-A1.
- Does **not** license wet-lab / holdout unblind / C1 E/P edits.

## Next

Desk claim closed REJECT. Do not start C-B1-TE-AluY-AG under this folder.
