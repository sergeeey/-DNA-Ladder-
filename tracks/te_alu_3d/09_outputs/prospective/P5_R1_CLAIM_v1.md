# P5 R1 — Context-length sign stability for reporter plan

**Status:** PRE-REGISTERED (before results)  
**Date locked:** 2026-07-15  
**L0:** Predictive desk test of AlphaGenome REF→ALT **signed** CHIP_TF direction across context lengths.  
**Not wet-lab. Not holdout. Does not reshape Stage-3.**

## Honest proxy note

AlphaGenome `predict_variant` supports sequence lengths **16 kb / 100 kb / 500 kb / 1 Mb** only  
(`SUPPORTED_SEQUENCE_LENGTHS`). It cannot score the literal Stage-2 windows **301 / 1001 / 2001 bp**.

Therefore R1 uses the **nearest available length ladder** as a **genomic-context sensitivity** proxy for Branch B:

| Reporter intent | AG proxy used here |
|-----------------|--------------------|
| short / minimal | `SEQUENCE_LENGTH_16KB` |
| mid | `SEQUENCE_LENGTH_100KB` |
| long | `SEQUENCE_LENGTH_500KB` |

This tests whether predicted activity-direction is an artifact of AG context width — **not** a wet transfection of 301 bp oligos.

## Primaries

- Alleles: **C1** (must), **C2**, **C3**, **N3** (negative expectation)
- Endpoint: `chip_tf_mean_signed = mean(alt − ref)` over CHIP_TF channels  
  (sign = predicted direction; `|chip_tf_mae|` secondary)
- Contact signed mean reported; **not** primary for Branch B R1

## Pre-registered kills

| ID | Rule |
|----|------|
| **R1_HARD** | For C1: `sign(chip_tf_mean_signed)` flips **16→100** **and** again **100→500** |
| **R1_SOFT** | For C1: exactly one adjacent flip (16↔100 or 100↔500) |
| **R1_PASS** | For C1: no adjacent sign flips |

Panel notes (not auto-kills):

- If C3 flips hard while C1 passes → note architecture/activity split  
- If N3 has large signed effect that also flips → matching control concern (`N3_UNSTABLE`)

## Branch B consequence

| Verdict | Consequence |
|---------|-------------|
| `R1_HARD` | Branch B remains **exploratory only**; do not treat 301 bp as length-invariant primary |
| `R1_SOFT` | Conditionally keep B; prefer 100 kb–stable narrative; disclose |
| `R1_PASS` | Length-sensitivity does **not** kill B on this AG proxy |

Does **not** authorize oligo order.

## Script

`pilot_scaffold/scripts/run_p5_r1_window_length_ag.py`
