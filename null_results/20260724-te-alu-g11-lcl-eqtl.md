# Decision: TE/Alu common Alu∩CTCF × GTEx LCL eQTL (G11)

**Date:** 2026-07-24  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — REJECT (negligible LCL-eQTL enrichment)

## Result

Same frozen G9c panel (n=200/200; AF 0.01–0.50; HTTP 400→MISS) queried against
**GTEx LCL** cis-eQTL map `QTD000221` (non-blood; claim locked before peek):

| Arm | hit-rate |
|-----|---------:|
| Alu∩HUDEP-2 CTCF | 1/200 = 0.005 |
| Alu outside CTCF±250bp | 2/200 = 0.010 |

risk_diff = −0.005; Fisher p ≈ 1.0 → **REJECT** (`negligible_diff`). Liver
replication not run (primary not PASS).

Converges with G9c blood REJECT: no public-desk enrichment of common Alu∩CTCF
SNVs for cis-eQTL hit-rate in either blood or LCL under these rules.

## Evidence chain

- Claim / decision / result: `tracks/te_alu_3d/09_outputs/prospective/G11_*`
- Panel: `g9c_common_alu_ctcf_panel_freeze_v1.json` (sha256 verified)
- Script: `run_g11_common_alu_lcl_eqtl.py`

## What This Result Does NOT Mean

1. Not a rescue or re-analysis of G9c blood.  
2. Not erythroid / HUDEP-2 expression.  
3. Not causal Alu→CTCF→eQTL.  
4. Not wet-lab GO / holdout unlock.

## Allowed next steps

- Independent Hi-C on new anchors (G10) if not yet closed  
- EGA erythroblast unlock with new claim  
- Human B0 wet signature  
- **Not:** more GTEx tissues on the same panel after seeing LCL/blood nulls
  (tissue fishing)
