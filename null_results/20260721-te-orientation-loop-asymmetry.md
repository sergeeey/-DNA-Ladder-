# Null result — TE insertion orientation vs loop-anchor asymmetry?

**ID:** 20260721-te-orientation-loop-asymmetry  
**Date:** 2026-07-21  
**Track:** te_alu_3d  
**Experiment:** `tracks/te_alu_3d/experiments/exp_te_orientation_loop_asymmetry/`  
**Candidate:** C-J1  
**Verdict:** REJECT (`FAIL_KILL`)

## Claim (frozen)

|Δ_orient| = |p(+strand | left Hi-C anchor) − p(+strand | right)| ≥ 0.10 among
TE-hit 1 kb windows on K562 HiCCUPS loops (`ENCFF693XIL`); kill if |Δ| < 0.05.

## Result

Primary |Δ| **0.0064** (boot CI on Δ crosses 0); Alu-only |Δ| **0.0196**. Both ≪ 0.05.
Left/right +strand rates ≈0.50/0.50; both-TE opposite fraction ≈0.505.

## What this does NOT mean

1. Does **not** imply TE insertion strand is irrelevant to 3D genome biology outside
   this HiCCUPS left/right midpoint-window design.  
2. Does **not** test CTCF motif orientation / convergent-anchor geometry.  
3. Does **not** reopen C-A1 / C-D1 / C-E1 / C-L1 / C-H1 / C-F1 / C-G1 closed desks.  
4. Does **not** authorize wet / holdout / C1 work.  
5. Does **not** license inventing new remaps after primary-fruit exhaustion.
