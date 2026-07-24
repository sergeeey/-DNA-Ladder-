# Decision: TE/Alu common Alu∩CTCF × GTEx blood eQTL

**Date:** 2026-07-23  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — INCONCLUSIVE (api_error_rate; also underpowered n=23)

## Result

After G8 DATA_GAP_STOP on rare variants, G9 tested whether **common** SNVs in
Alu/SVA ∩ HUDEP-2 CTCF peaks on chr11 are enriched for significant GTEx
whole-blood cis-eQTL hits vs AF-matched Alu SNVs outside CTCF peaks.

| Item | Value |
|------|-------|
| Freeze | 23 case / 23 ctrl (AF 0.05–0.50) |
| Primary | eQTL Catalogue QTD000356 |
| Case | hit 1 / miss 17 / error 5 |
| Ctrl | hit 8 / miss 10 / error 5 |
| Error rate | 21.7% (>10% gate) |
| Verdict | **INCONCLUSIVE** |

Fisher was not applied. Replication QTD000373 was not run.

## Evidence chain

- Claim: `tracks/te_alu_3d/09_outputs/prospective/G9_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`
- Freeze: `.../g9_common_alu_ctcf_panel_freeze_v1.json`
- Result: `.../g9_common_alu_ctcf_blood_eqtl_v1.json`
- Decision: `.../G9_common_alu_ctcf_blood_eqtl_decision_v1.md`
- Tests: `tracks/te_alu_3d/tests/test_g9_eqtl_lib.py` (16 passed)

## What This Result Does NOT Mean

1. It does not show that Alu∩CTCF common SNVs lack blood eQTL effects.  
2. It does not support enrichment (observed successful queries lean the other way, but are non-decision under the error gate).  
3. It does not reopen Stage-3 Hi-C or authorize wet-lab GO.

## Allowed next steps

- New pre-registered claim with broader chromosomes and/or HTTP-400→MISS rule  
- EGA erythroblast access  
- Pause
