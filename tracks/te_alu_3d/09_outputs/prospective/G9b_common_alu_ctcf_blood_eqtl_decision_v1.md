# G9b — Common Alu/SVA × CTCF blood eQTL — DECISION v1

**Date:** 2026-07-23  
**Claim:** `G9b_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`  
**Freeze sha256:** `4432586208c3cf51713a66587ec0b9bc5e688bac7fcd2702c4db13c2f2d087da`  
**Primary dataset:** `QTD000356` (GTEx blood ge)  
**Verdict:** **INCONCLUSIVE** (`effect_uncertain`)

## Design deltas vs G9

- AF band [0.01, 0.50]
- HTTP 400 → MISS
- New freeze (G9 artifacts unchanged)

## Primary counts

- cases tested: 46 (hit=1, miss=45, error=0)
- controls tested: 46 (hit=9, miss=37, error=0)
- p_case=0.0217  p_ctrl=0.1957  risk_diff=-0.1739  fisher_p=0.0152

API error_rate = 0 (HTTP-400-as-MISS fix worked). Power floor met (n=46≥30).

Enrichment is **wrong-direction** descriptively (controls have more blood eQTL hits),
but Fisher p=0.015 > pre-registered α=0.01 → not REJECT; |diff|≥0.05 → not
negligible REJECT → **INCONCLUSIVE**. Replication not run.

## What this does NOT mean

1. Not causal Alu → CTCF → expression.
2. Not erythroid / HUDEP-2 specific (whole blood only).
3. Not a rewrite of G9 (G9 stays INCONCLUSIVE).
4. Not wet-lab GO / holdout unlock.
5. Not permission to relax α post-hoc to call REJECT.
