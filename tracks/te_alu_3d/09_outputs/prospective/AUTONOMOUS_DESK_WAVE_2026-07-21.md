# Autonomous desk wave — 2026-07-21 (C-E1 close)

**Status:** **PAUSE** after C-E1 REJECT.  
**Branch:** `cursor/c-e1-rare-snv-analysis-a6fa` → merge `master`.  
**Hard rules honored:** no holdout unblind; no C1 E/P; no wet GO; no fake data; no bulk gnomAD.

## Wave outcomes (this amendment)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| **C-E1** | TE vs non-TE rare-SNV PWM Δ (non-HBB; umap-matched) | `te_alu_3d/.../exp_te_vs_nonte_rare_snv_pwm/` | **REJECT** — δ **0.033** FAIL_KILL |

## Prior outcomes same day (still stand)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| **C-D1** | TE milliDiv tertile vs Pol II↔Hi-C repro | `te_alu_3d/.../exp_te_age_loop_reproducibility/` | **REJECT** — Δ **−0.0037** |
| **C-H1** (robust) | TE-pELS Gnocchi sensitivity | `se_llps/.../exp_te_derived_pels_gnocchi/` | **SUPPORT_WITH_CAVEATS** |
| **C-F1** | Mustache vs HiCCUPS TE-anchor Jaccard | `te_alu_3d/.../exp_te_loop_caller_concordance/` | **BLOCKED_DATA** |
| **C-G1** | RAD21 vs CTCF ChIA TE odds | `te_alu_3d/.../exp_rad21_vs_ctcf_chia_te_odds/` | **BLOCKED_DATA** |

## Prior wave (2026-07-20) still stands

See `AUTONOMOUS_DESK_WAVE_2026-07-20.md` for C-A1…C-L1 closes.

## C-E1 summary

- Prereg Standard claim; T0 freeze; then fetch gnomAD GraphQL r4 (chr11 CTCF±250 bp,
  n=55 849 rare SNVs; 2 961 Alu/SVA) + Hoffman umap k100.
- Match chrom + umap q4 **before** PWM; 2 961 pairs scored with `ctcf_pwm_delta_v1.1`.
- Primary Cliff's δ **0.033** (CI [0.005, 0.061]) < 0.05 → FAIL_KILL / REJECT.
- Scorer \|Δ\| mass ≈4.087 (PWM extreme contrast); TE≈non-TE under frozen scorer.
- null_results REJECT filed.

## PAUSE — open list (no infinite remaps)

| ID | Status |
|----|--------|
| **C-J1** | still open (Deep Research: TE insertion orientation vs loop-anchor asymmetry) — **not auto-started** |
| C-C1 | unscored Deep Research card — park |
| C-B1-TE-AluY-AG | PARKED (creds) |
| C-K1-CTCF-chia-fallback / C-L1-crosscell | PARKED |
| Holdout / C1 / wet | untouched |

## Recommendation

Merge this wave. **Human pause.** Only remaining unscored primary fruit worth a
queued desk is **C-J1** — do not spawn remaps overnight.
