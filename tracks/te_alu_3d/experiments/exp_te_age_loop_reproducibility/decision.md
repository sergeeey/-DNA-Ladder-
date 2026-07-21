# Decision — exp_te_age_loop_reproducibility (C-D1)

**Date:** 2026-07-21  
**Verdict:** **REJECT** (`FAIL_KILL`)  
**Stage:** Primary Δ_repro + Alu-only sensitivity complete

## Gate

Frozen claim: Δ_repro = repro(old milliDiv tertile) − repro(young) ≥ **0.10**;  
kill if Δ **< 0.05**.

| Contrast | Δ_repro | Bootstrap 95% CI | Verdict |
|----------|---------|------------------|---------|
| Primary SINE∪LINE∪LTR | **−0.0037** | [−0.0062, −0.0014] | **REJECT** |
| Alu-only sensitivity | **−0.0043** | [−0.0068, −0.0019] | **REJECT** |

Young / mid / old repro rates (primary): **0.0292 / 0.0272 / 0.0255**  
(n TE-hit windows = 493 522; tertile cuts milliDiv q33=111, q66=194).

Class-stratified exploratory |Δ| all ≪ 0.05 (LINE +0.006; LTR +0.001; SINE −0.004).

Arts: `results/primary_delta_repro.{json,md}`, `results/sensitivity_alu_only.{json,md}`.

## What this does NOT mean

1. NOT a claim that TE age is irrelevant to 3D genome biology outside Pol II↔HiCCUPS K562 mid-1kb windows.
2. NOT a reopening of C-A1 AluSz discordance (different estimand).
3. NOT wet / holdout / C1 / pathogenicity license.
4. Low absolute repro (~3%) reflects Pol II-heavy exclusive window mass vs sparse Hi-C — age contrast remains near-null.

## Next fruit

Recommend **C-E1** T0 (mappability-matched TE vs non-TE rare-SNV PWM Δ; non-HBB) or human pause. Holdout / C1 / wet untouched.
