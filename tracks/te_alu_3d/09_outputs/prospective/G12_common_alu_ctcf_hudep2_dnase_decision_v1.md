# G12 — Common Alu∩CTCF × HUDEP-2 DNase — DECISION v1

**Date:** 2026-07-24  
**Claim:** `G12_common_alu_ctcf_hudep2_dnase_CLAIM_v1.md`  
**Freeze sha256:** `42505a328866309206929c0654b784a3a61ec6f1a507a684e00c5118afac2983`  
**Primary peaks:** `ENCFF626FHU` (`ENCSR978CYN`)  
**Peaks sha256:** `868c8bf1443d7e23f6faee176b259dd515235d594776da9b63d6850f6ede7801`  
**Verdict:** **PASS** (enrichment_case_gt_ctrl) — replicated on `ENCFF895OQX`

## Primary counts (`ENCFF626FHU`)

| Arm | hit | miss | rate |
|-----|----:|-----:|-----:|
| CASE_CTCF_ALU | 50 | 150 | 0.250 |
| CTRL_ALU_NONCTCF | 1 | 199 | 0.005 |

risk_diff = +0.245; Fisher p ≈ 1.6×10⁻¹⁵ (α=0.01, min_abs_diff=0.05 cleared).

## Replication (`ENCSR013QDF` / `ENCFF895OQX`)

| Arm | hit | miss | rate |
|-----|----:|-----:|-----:|
| CASE | 40 | 160 | 0.200 |
| CTRL | 0 | 200 | 0.000 |

risk_diff = +0.200; Fisher p ≈ 2.1×10⁻¹³ → **PASS**.

## Interpretation bound (honest)

Case SNVs sit inside **HUDEP-2 CTCF ChIP peaks** by construction. CTCF-bound sites are
typically DNase-accessible. This PASS therefore largely reflects **CTCF ∩ open-chromatin
colocalization** on the Alu geography — it does **not** establish an Alu-specific
accessibility mechanism beyond CTCF occupancy, and does **not** revive blood/LCL eQTL or
Hi-C contact claims.

Allowed language: accessibility-candidate enrichment of Alu∩CTCF vs Alu-nonCTCF under
HUDEP-2 DNase. Forbidden: expression, contact, regulatory, causal.

## What this does NOT mean

1. Not eQTL / expression enrichment (G9–G11 remain REJECT).  
2. Not Hi-C contact or architecture (Stage-3 / G10 remain closed).  
3. Not causal Alu→CTCF→accessibility.  
4. Not wet-lab GO / holdout unlock.  
5. Not proof that Alu sequence (vs CTCF binding alone) drives DHS.

## Next (allowed)

- ~~G12b CLAIM: within CTCF peaks, Alu vs non-Alu DHS rate~~ → **DONE INCONCLUSIVE**
  (`G12b_ctcf_alu_vs_nonalu_dnase_decision_v1.md`; null filed)
- Human B0 signature  
- EGA erythroblast eQTL unlock  
