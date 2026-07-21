# Null result — TE divergence/age bin vs cross-assay loop-call reproducibility?

**ID:** 20260721-te-age-vs-loop-reproducibility  
**Date:** 2026-07-21  
**Track:** te_alu_3d  
**Experiment:** `tracks/te_alu_3d/experiments/exp_te_age_loop_reproducibility/`  
**Candidate:** C-D1  
**Verdict:** REJECT (`FAIL_KILL`)

## Claim (frozen)

Δ_repro = mean(repro | old milliDiv tertile) − mean(repro | young) ≥ 0.10 among
TE-hit 1 kb Pol II∪Hi-C loop-anchor windows (K562; ENCFF511QFN vs ENCFF693XIL);
kill if Δ < 0.05.

## Result

Primary Δ **−0.0037** (boot CI entirely below 0); Alu-only Δ **−0.0043**. Both ≪ 0.05.
Absolute repro rates ~2.5–3.0% across tertiles (near-flat).

## What this does NOT mean

1. Does **not** imply TE age is irrelevant to loop biology outside this Pol II↔HiCCUPS
   midpoint-window design.  
2. Does **not** reopen C-A1 / C-H1 / C-L1 / C-F1 / C-G1 closed desks.  
3. Does **not** authorize wet / holdout / C1 work.  
4. Does **not** claim milliDiv tertiles equal a calibrated molecular clock.
