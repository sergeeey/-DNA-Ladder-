# Null result — Mappability-matched TE vs non-TE rare-SNV PWM Δ (non-HBB)?

**ID:** 20260721-te-vs-nonte-rare-snv-pwm  
**Date:** 2026-07-21  
**Track:** te_alu_3d  
**Experiment:** `tracks/te_alu_3d/experiments/exp_te_vs_nonte_rare_snv_pwm/`  
**Candidate:** C-E1  
**Verdict:** REJECT (`FAIL_KILL`)

## Claim (frozen)

Cliff's δ (TE − non-TE) on |ctcf_pwm_delta_v1.1| ≥ 0.20 among rare SNVs
(AF≤0.001) outside HBB + sealed HO, after chrom + Hoffman umap k100 quartile
matching; kill if |δ| < 0.05.

## Result

Primary δ **0.033** (boot CI [0.005, 0.061]); n=2961 matched pairs on chr11
CTCF-neighborhood desk panel. |δ| < 0.05 → FAIL_KILL / REJECT.

## What this does NOT mean

1. Does **not** imply TE-borne rare SNVs never disrupt CTCF motifs under a
   different (non-exploratory) scorer.  
2. Does **not** reopen Track A HBB dual-estimand enrichment.  
3. Does **not** authorize wet / holdout unblind / C1 E/P.  
4. Does **not** claim genome-wide bulk gnomAD was required — desk used chr11
   CTCF±250 bp GraphQL slices (project no-bulk rule).
