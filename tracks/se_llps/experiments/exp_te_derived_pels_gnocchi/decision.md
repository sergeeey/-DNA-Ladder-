# Decision — exp_te_derived_pels_gnocchi (C-H1)

**Date:** 2026-07-21 (robustness amendment; primary SUPPORT 2026-07-20)  
**Verdict:** **SUPPORT_WITH_CAVEATS**  
**Primary (unchanged):** |\Delta mean Gnocchi Z| = **0.211** ≥ MCID 0.15  
**Robustness:** core alternate-matching / blacklist / chromosome-holdout all keep |\Delta| ≥ 0.15; **LINE-only** class split collapses to kill (|\Delta|=0.025) → caveats required.

## Primary result (frozen 2026-07-20)

| Metric | Value |
|--------|------:|
| TE∩pELS (universe) | 62 471 |
| Non-TE pool | 109 423 |
| 1:1 matched (lock) | 53 846 |
| Pairs with Gnocchi coverage | 30 962 |
| mean Δ (TE − non-TE) | **−0.211** |
| \|\Δ\| | **0.211** |
| Bootstrap 95% CI (mean Δ) | [−0.239, −0.183] |
| Cliff's δ | −0.064 |

## Sensitivity battery (2026-07-21)

Artifact: `results/sensitivity_result.json`.

| Scenario | \|\Δ\| | n pairs | Gate |
|----------|------:|--------:|------|
| Primary recompute | 0.211 | 30 962 | SUPPORT |
| Alt seed `20260721` | 0.223 | 30 896 | SUPPORT |
| Match without TSS | 0.203 | 32 143 | SUPPORT |
| GC bins q5 (vs q10) | 0.228 | 31 619 | SUPPORT |
| Exclude ENCODE blacklist | 0.226 | 30 875 | SUPPORT |
| Chrom parity odd | 0.214 | 16 784 | SUPPORT |
| Chrom parity even | 0.208 | 14 178 | SUPPORT |
| LOCO min across chroms | **0.202** | — | SUPPORT |
| TE class **SINE** | 0.251 | 17 711 | SUPPORT |
| TE class **LINE** | **0.025** | 11 427 | **REJECT (kill)** |
| TE class **LTR** | 0.358 | 6 947 | SUPPORT |

**Second Gnocchi build:** UNAVAILABLE (public non-QC alternate 1 kb files 404 on gnomAD-nc-constraint-v31-paper bucket) — not run.

**Desk robust label:** `SUPPORT_WITH_CAVEATS` — matching / blacklist / chr-holdout are stable above MCID; the TE-union signal is **not** carried by LINE-derived pELS (SINE + LTR drive |\Δ|).

## Honest caveats (do not soften)

1. **Cliff's δ (−0.064) is small** — mean shift clears |\Δ| MCID; distributions overlap.
2. **~42% pair dropout** — Gnocchi QC drops many repeat-overlapping windows.
3. **LINE-only fragility** — |\Δ|=0.025 < 0.05; do **not** claim TE-class-uniform constraint shift.
4. Germline metric only — not cell-type selection; not causal TE → constraint.
5. Does **not** claim wet-lab, pathogenicity, Micro-C recovery, or SE heritability reopen.

## Artifacts

- `results/matching_lock.json`, `results/primary_result.json`
- `results/sensitivity_result.json`, `results/sensitivity_run.log`
- Scripts: `run_c_h1_analysis.py`, `run_c_h1_sensitivity.py`, `c_h1_lib.py`
- Tests: `tests/test_c_h1_unit.py`

## Next fruit

**C-F1** Mustache vs HiCCUPS TE-anchor concordance (standing order). Holdout / C1 / wet untouched.
