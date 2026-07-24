# G9c — Multi-chrom common Alu/SVA × CTCF blood eQTL — DECISION v1

**Date:** 2026-07-23  
**Claim:** `G9c_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`  
**Freeze sha256:** `42505a328866309206929c0654b784a3a61ec6f1a507a684e00c5118afac2983`  
**Chromosomes:** chr1, chr2, chr6, chr11  
**Primary dataset:** `QTD000356`  
**Verdict:** **REJECT** (`negligible_diff`)

## Primary counts

- cases: hit=11 miss=189 error=0 tested=200 (p_case=0.055)
- controls: hit=4 miss=196 error=0 tested=200 (p_ctrl=0.020)
- risk_diff=+0.035  fisher_p=0.112

Direction matches enrichment hypothesis (case > ctrl), but absolute difference
`< 0.05` with Fisher p `> 0.01` → pre-registered **REJECT** (negligible).
Replication not run.

## What this does NOT mean

1. Not causal Alu→CTCF→expression.
2. Not erythroid-specific.
3. Does not rewrite G9/G9b.
4. Not wet-lab GO / holdout unlock.
5. Not permission to lower the 0.05 risk-diff floor post-hoc.
