# Null result — SVA_F dELS active↔inactive switching vs matched non-TE

**Date:** 2026-07-20  
**Track:** `te_alu_3d`  
**Experiment:** `tracks/te_alu_3d/experiments/exp_sva_f_ccre_state_switching/`  
**Candidate:** C-A2 (true; **not** ChIA-PET)  
**Verdict:** **REJECT** (desk closed as `FAIL_KILL`)

## Pre-registered claim (frozen)

OR(switcher | SVA_F-overlapping dELS) ≥ **1.4** vs 1:k matched non-TE dELS across a frozen
ENCODE v3 Full-classification cell-type panel.

**Falsification:** OR &lt; 1.1 in ≥2 independent (odd/even) cell-type sub-panels → REJECT.

Switcher (pre-specified): active in ≥1 and inactive in ≥3 biosamples; active = SCREEN
classification `dELS` / `dELS,*` with `All-data/Full-classification`.

Matching (before outcomes): chrom + length quartile + GC decile + TSS-distance bin +
held-out SK-N-SH baseline active.

## Result summary

| Arm | OR | 95% CI | Kill OR&lt;1.1? |
|-----|-----:|--------|:---:|
| Primary (N=10) | **0.489** | 0.243–0.985 | yes |
| Odd panel | **0.655** | — | yes |
| Even panel | **0.411** | — | yes |

- n_SVA_F dELS = 68; k=5; undermatched = 0  
- Switcher rate: SVA_F 0.147 vs matched non-TE 0.268  
- Table [a,b,c,d] = [10, 58, 91, 249]

## What this does NOT mean

1. Does **NOT** mean SVA_F is irrelevant to all enhancer biology — only that the frozen
   switching-enrichment claim (OR≥1.4) is rejected on this panel.
2. Does **NOT** authorize causal “SVA_F silences / switches enhancers” language.
3. Does **NOT** license wet-lab GO, oligo order, holdout unblind, or C1 E/P edits.
4. Does **NOT** reopen C-A1 INCONCLUSIVE, C-K1 BLOCKED_DATA, or SE/LLPS nulls.
5. Does **NOT** validate the parked ChIA-PET `C-K1-CTCF-chia-fallback` estimand.
6. Does **NOT** by itself establish a protective (OR&lt;1) claim — that would need a new
   preregistered estimand.

## Recommendation

Close C-A2 desk. Next fruit: **C-H1** (if Micro-C processed loops available) or **C-L1**.
Do not auto-start without human queue.
