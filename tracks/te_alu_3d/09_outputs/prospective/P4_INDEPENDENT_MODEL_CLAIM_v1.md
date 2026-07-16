# P4 — Independent model matrix (desk)

**Status:** PRE-REGISTERED (before classification results)
**Date locked:** 2026-07-16
**L0:** Descriptive panel audit — multi-model agreement classes for frozen alleles
**Not wet-lab. Not holdout. ARCHCODE is exploratory prior only (not independent validation).**

## Purpose

Same table for C1 + frozen panel:

```text
ARCHCODE (exploratory prior lean)
motif-only baseline
distance-only baseline
activity prediction (AG CHIP_TF)
AlphaGenome contact Δ
observed WT contact (Hi-C / G4a)
```

Classify each allele:

| Class | Rule (locked) |
|-------|----------------|
| **convergence** | ≥2 of {motif_high, activity_high, ag_contact_high} positive **or** (activity_high **and** WT contact PASS) |
| **principled_disagreement** | motif_high XOR activity_high, with concrete `mechanism_prior` (M1/M3) |
| **unsupported** | exactly one scorer positive **and** no observed WT contact |
| **negative_consistent** | role matched_negative **and** activity_low **and** not motif_high |
| **incomplete** | required AG or motif field missing |

## Thresholds (locked)

| Flag | Rule |
|------|------|
| motif_high | motif_only score ≥ 0.5 (from CTCF PWM Δ, no peak boost) |
| motif_low | motif_only score < 0.2 |
| activity_high | AG CHIP_TF MAE ≥ 0.20 |
| activity_low | AG CHIP_TF MAE < 0.12 |
| ag_contact_high | AG contact MAE ≥ 0.002 |
| WT contact PASS | only where G4a (or equivalent) recorded PASS_DESK* |

## Hard constraints

- Do **not** treat ARCHCODE as scientific validation (`exploratory_prior_only`)
- Do **not** move E/P or Stage-3 slots from this matrix
- Disagreement with AG is allowed if frozen as principled_disagreement

## Labels (panel-level)

| ID | Rule |
|----|------|
| **P4_MATRIX_COMPLETE** | All frozen SNV alleles classified |
| **P4_PARTIAL** | Some incomplete rows |
| **P4_BLOCKED** | Cannot read stage1 / panel registry |

## Arts

Script: `pilot_scaffold/scripts/run_p4_independent_model_matrix.py`
Out: `P4_independent_model_matrix_v1.md` / `.json`
Also fills desk copy: `P4_G2b_independence_notes_v1.md` (what is/isn't independent)
