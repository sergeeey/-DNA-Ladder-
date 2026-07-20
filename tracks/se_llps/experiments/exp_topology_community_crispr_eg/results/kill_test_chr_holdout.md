# Kill-test — chromosome holdout (C-B1)

**Run (UTC):** 2026-07-20T12:33:39.953059+00:00
**Verdict:** `FAIL_KILL`

## Estimand (redesigned after rE2G audit)

ΔAUC of baseline+topology vs baseline=log10_distance+activity_els+se_membership; NOT novelty for any 3D contact (rE2G already has contact/loops).

- **Label:** `Regulated==TRUE` (ensemble CRISPR benchmark)
- **Train:** all chroms except ['chr20', 'chr21', 'chr22'] (n=10065, pos=467)
- **Test:** ['chr20', 'chr21', 'chr22'] (n=265, pos=20)

## Primary metric

| Model | ROC-AUC | AUPRC |
|-------|---------|-------|
| Baseline (log10_dist + ELS + SE) | 0.8806 | 0.685533065655084 |
| Baseline + topology | 0.8733 | 0.6816263257262154 |
| **ΔAUC** | **-0.0073** | — |

- Kill if ΔAUC < 0.02 → FAIL_KILL / REJECT
- SUPPORT if ΔAUC ≥ 0.05 → PASS_KILL
- else INCONCLUSIVE

## Controls

- Distance alone AUC: **0.8796** — Distance-alone AUC=0.8796 (>0.55 positive-control gate PASS).
- SE-only AUC (sensitivity): 0.5378
- Leave-one-chr mean ΔAUC: 0.0003
- Shuffle-label null mean ΔAUC: 0.0093 (std 0.0753, n_valid=20)

## Feature prevalence

{
  "activity_els_frac": 0.60648596321394,
  "se_membership_frac": 0.16573088092933205,
  "mean_enh_loop_degree": 0.2960309777347531,
  "mean_prom_loop_degree": 0.3150048402710552,
  "frac_shared_community_gt0": 0.012681510164569216
}

## What this does NOT mean

1. Not a claim that 3D contact/loops are novel for E–G prediction (rE2G).
2. Not causal CRE-community → regulation.
3. Beating this baseline is not beating full ENCODE-rE2G.
4. Does not reopen closed SE enrichment nulls or TE C-A1.

