# Decision — exp_te_derived_pels_gnocchi (C-H1)

**Date:** 2026-07-20  
**Verdict:** **SUPPORT**  
**Primary:** |\Delta mean Gnocchi Z| = **0.211** ≥ MCID 0.15 (kill was |\Delta| < 0.05)

## Result (pre-registered gates)

| Metric | Value |
|--------|------:|
| TE∩pELS (universe) | 62 471 |
| Non-TE pool | 109 423 |
| 1:1 matched (lock) | 53 846 |
| Pairs with Gnocchi coverage | 30 962 (22 884 dropped, no QC window) |
| mean Z (TE) | 0.817 |
| mean Z (matched non-TE) | 1.028 |
| mean Δ (TE − non-TE) | **−0.211** |
| \|\Delta\| | **0.211** |
| Bootstrap 95% CI (mean Δ) | [−0.239, −0.183] |
| Cliff's δ | −0.064 |
| Paired permutation p | 0.0001 (floor) |

**SUPPORT** on the frozen primary: |\Delta| ≥ 0.15. Direction: TE-derived pELS are **less** germline-constrained (lower Gnocchi Z) than GC/length/TSS-matched non-TE pELS.

CI for mean Δ excludes 0 and excludes the kill band; does **not** reopen SE-vs-typical Gnocchi REJECT (different universe).

## Honest caveats (do not soften SUPPORT)

1. **Cliff's δ (−0.064) is small** — mean shift clears |\Delta| MCID, but distributions overlap heavily. Practical importance is mean-shift, not rank separation.
2. **~42% pair dropout** — Gnocchi QC drops many repeat-overlapping 1 kb windows; surviving TE-pELS Z often comes from non-masked flank within the cCRE. Estimand is conditional on QC coverage.
3. **Germline metric** — not cell-type-specific selection; descriptive population constraint only.
4. Does **not** claim causal TE → constraint, Micro-C recovery, or SE heritability reopen.

## Artifacts

- `results/matching_lock.json` (pre-outcome)
- `results/primary_result.json`
- Scripts: `scripts/run_c_h1_analysis.py`, `scripts/c_h1_lib.py`
- Tests: `tests/test_c_h1_unit.py`

## Next fruit

Start **C-I1** = Micro-C vs Hi-C Alu-anchor recovery (Deep Research original C-H1 Micro-C estimand; desk remapped). If processed Micro-C loops unavailable → `BLOCKED_DATA` / fallback **C-L1**.
