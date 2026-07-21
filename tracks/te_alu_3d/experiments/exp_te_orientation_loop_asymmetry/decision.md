# Decision — exp_te_orientation_loop_asymmetry (C-J1)

**Date:** 2026-07-21  
**Verdict:** **REJECT** (`FAIL_KILL`)  
**Stage:** Primary |Δ_orient| + Alu-only sensitivity complete

## Gate

Frozen claim: |Δ_orient| = |p(+|left) − p(+|right)| ≥ **0.10** among TE-hit
1 kb Hi-C loop-anchor windows (K562; `ENCFF693XIL`); kill if |Δ| **< 0.05**.

| Contrast | \|Δ_orient\| | Bootstrap 95% CI (Δ) | Verdict |
|----------|-------------|----------------------|---------|
| Primary SINE∪LINE∪LTR | **0.0064** | [−0.0193, 0.0084] | **REJECT** |
| Alu-only sensitivity | **0.0196** | [−0.0417, 0.0074] | **REJECT** |

Primary rates: p(+|left)=**0.4975** (n=11 008); p(+|right)=**0.5039** (n=11 027).  
Fisher OR(+|left vs right) **0.975** (CI 0.925–1.028).  
Both-TE exploratory: f_opp **0.505** (|f−0.5|=0.0047; n=9 113).

Arts: `results/primary_delta_orient.{json,md}`, `results/sensitivity_alu_only.{json,md}`.

## What this does NOT mean

1. NOT a claim that TE strand is irrelevant to loop biology outside this HiCCUPS
   left/right 1 kb design.
2. NOT a test of CTCF motif convergence (parked C-B1-TE-AluY-AG).
3. NOT a reopening of C-A1 / C-D1 / C-E1 / C-L1 / C-H1 closed desks.
4. NOT wet / holdout / C1 / pathogenicity license.

## Next fruit

**PAUSE / NONE** — all Deep Research primary fruits scored (or BLOCKED_DATA /
PARKED). Do not invent remaps. Holdout / C1 / wet untouched.
