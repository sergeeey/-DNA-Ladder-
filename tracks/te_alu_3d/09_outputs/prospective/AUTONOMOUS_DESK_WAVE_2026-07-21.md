# Autonomous desk wave — 2026-07-21 (C-J1 close → PAUSE/NONE)

**Status:** **PAUSE / NONE** after C-J1 REJECT. All Deep Research primary fruits scored
(or BLOCKED_DATA / PARKED).  
**Branch:** `cursor/c-j1-fruit-completion-60fb` → merge `master`.  
**Hard rules honored:** no holdout unblind; no C1 E/P; no wet GO; no fake data; no
new remaps.

## Wave outcomes (this amendment)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| **C-J1** | TE insertion orientation vs left/right Hi-C loop-anchor asymmetry | `te_alu_3d/.../exp_te_orientation_loop_asymmetry/` | **REJECT** — \|Δ\| **0.0064** FAIL_KILL |

## Prior outcomes same day (still stand)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| **C-E1** | TE vs non-TE rare-SNV PWM Δ (non-HBB; umap-matched) | `te_alu_3d/.../exp_te_vs_nonte_rare_snv_pwm/` | **REJECT** — δ **0.033** |
| **C-D1** | TE milliDiv tertile vs Pol II↔Hi-C repro | `te_alu_3d/.../exp_te_age_loop_reproducibility/` | **REJECT** — Δ **−0.0037** |
| **C-H1** (robust) | TE-pELS Gnocchi sensitivity | `se_llps/.../exp_te_derived_pels_gnocchi/` | **SUPPORT_WITH_CAVEATS** |
| **C-F1** | Mustache vs HiCCUPS TE-anchor Jaccard | `te_alu_3d/.../exp_te_loop_caller_concordance/` | **BLOCKED_DATA** |
| **C-G1** | RAD21 vs CTCF ChIA TE odds | `te_alu_3d/.../exp_rad21_vs_ctcf_chia_te_odds/` | **BLOCKED_DATA** |

## Prior wave (2026-07-20) still stands

See `AUTONOMOUS_DESK_WAVE_2026-07-20.md` for C-A1…C-L1 closes.

## C-J1 summary

- Prereg Standard claim; accession freeze Hi-C `ENCFF693XIL` + UCSC rmsk strand.
- Keep bedpe **pairs**; 1 kb mid left/right windows; TE strand = max-overlap rmsk.
- Primary |Δ_orient| **0.0064** (p+ left 0.498 / right 0.504; n≈11k/arm).
- Alu-only |Δ| **0.0196**; both-TE f_opp ≈0.505.
- null_results REJECT filed.

## PAUSE / NONE — open list

| ID | Status |
|----|--------|
| **Primary fruits** | **all scored** (SUPPORT / REJECT / BLOCKED_DATA / INCONCLUSIVE) |
| C-C1 | unscored Deep Research card — remain park (not a queued primary after wave) |
| C-B1-TE-AluY-AG | PARKED (creds) |
| C-K1-CTCF-chia-fallback / C-L1-crosscell | PARKED |
| Holdout / C1 / wet | untouched |

## Recommendation

Merge this wave. **`next_fruit_recommend: PAUSE_NONE`**. Do not spawn remaps.
