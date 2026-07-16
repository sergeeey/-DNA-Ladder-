# P4 / G2b — independence notes (desk fill)

**Date:** 2026-07-16
**Related template:** `templates/G2b_model_independence_matrix.yaml` (still mostly empty for external nets)

## What we actually ran

| Model / track | Run status | Allele-Δ validated | Dependence |
|---------------|------------|--------------------|------------|
| AlphaGenome CHIP_TF | PRESENT (stage1) | desk MAE only | sequence net |
| AlphaGenome contact | PRESENT (stage1) | desk MAE only | **same net as CHIP_TF** |
| motif_only CTCF PWM | PRESENT | exploratory | shares peak layer with distance |
| distance_only | PRESENT | n/a | shares peak layer with motif |
| ARCHCODE | NOT_RUN | n/a | — |
| UniChrom / Hi-Compass / enhancer3D | NOT_RUN | — | — |
| HUDEP-2 WT Hi-C (G4a) | PRESENT for C1 E–P | observational | independent of sequence nets |

## Rule

Do not sell AG CHIP + AG contact as two independent votes.
