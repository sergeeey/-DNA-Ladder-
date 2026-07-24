# Decision: Within-CTCF Alu vs non-Alu × HUDEP-2 DNase (G12b)

**Date:** 2026-07-24  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — INCONCLUSIVE (effect_uncertain)

## Result

Residual test after G12 PASS (Alu∩CTCF vs Alu-nonCTCF DHS enrichment). Same DNase
primary `ENCFF626FHU`; cases = G9c CASE_CTCF_ALU; controls = AF-matched **CTCF ∩ non-Alu**:

| Arm | DHS hit-rate |
|-----|-------------:|
| CTCF ∩ Alu | 50/200 = 0.250 |
| CTCF ∩ non-Alu | 69/200 = 0.345 |

risk_diff = −0.095 (wrong direction vs Alu-enrichment); Fisher p = 0.049 > α=0.01 →
**INCONCLUSIVE** (`effect_uncertain`). Replication not run.

Together with G12: HUDEP-2 DHS enrichment of Alu∩CTCF vs Alu-outside-CTCF is real but
**explained by CTCF occupancy**, not an Alu-specific residual inside CTCF peaks.

## Evidence chain

- Claim / freeze / result / decision under `tracks/te_alu_3d/09_outputs/prospective/G12b_*`
- Parent PASS: `G12_common_alu_ctcf_hudep2_dnase_decision_v1.md`

## What This Result Does NOT Mean

1. Does not overturn G12 descriptive PASS (different contrast).  
2. Does not prove Alu never affects accessibility.  
3. Does not reopen eQTL / Hi-C / wet GO.

## Allowed next steps

- Human B0 signature  
- EGA erythroblast eQTL  
- **Not:** further DHS threshold fishing on these panels
