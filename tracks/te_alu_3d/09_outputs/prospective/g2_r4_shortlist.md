# G2 prep — R4 shortlist C1–C3 (motif vs AlphaGenome)

**Date:** 2026-07-14  
**PWM:** `ctcf_pwm_delta_v1.1` fp `54a2ad823a0e6b6f`  
**Holdout:** SEALED / not scored  
**Status:** G2_PREP_COMPLETE — descriptive ranks only (n=3)

| ID | Variant | Motif-only | Δlogodds | Dist-only | AG contact MAE | AG CHIP_TF MAE | Arm lean |
|----|---------|-----------:|---------:|----------:|---------------:|---------------:|----------|
| C1 | `chr11:62753923:A:G` | 0.065 | -4.087 | 0.003 | 0.0049 | 0.541 | ARM_B_AG_GT_MOTIF |
| C2 | `chr11:62753923:A:T` | 0.065 | -4.087 | 0.003 | 0.0021 | 0.255 | ARM_B_AG_GT_MOTIF |
| C3 | `chr11:72434037:C:T` | 0.870 | 4.087 | 0.003 | 0.0016 | 0.271 | ARM_B_MOTIF_GT_AG |

## Rank table

| ID | Rank AG contact | Rank AG CHIP_TF | Rank motif | AG vs motif |
|----|----------------:|----------------:|-----------:|-------------|
| C1 | 1 | 1 | 2 | DISAGREE |
| C2 | 2 | 3 | 3 | DISAGREE |
| C3 | 3 | 2 | 1 | DISAGREE |

## Interpretation

- Higher AG contact rank with lower motif rank → **Arm B** (architecture-leaning, need strong WT contact).
- Same ranks → **Arm A** convergence (still not wet-lab GO).
- Motif alone remains exploratory PWM — cannot authorize confirmatory primary.

## Non-claims
- No G9 freeze / no wet-lab / no holdout unblind / no 3D disruption

Artifacts: `g2_r4_shortlist_report.json`, `g2_r4_shortlist_scores.tsv`
