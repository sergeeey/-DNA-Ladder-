# Autonomous desk wave — 2026-07-21

**Status:** **CONTINUE** after PAUSE_HUMAN («го») → C-D1 closed.  
**Branch:** `cursor/te-age-vs-loop-reproducibility-fc8c` → merge `master`.  
**Hard rules honored:** no holdout unblind; no C1 E/P; no wet GO; no fake data.

## Wave outcomes (this amendment)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| **C-D1** | TE milliDiv tertile vs Pol II↔Hi-C repro | `te_alu_3d/.../exp_te_age_loop_reproducibility/` | **REJECT** — Δ **−0.0037** (Alu −0.0043); FAIL_KILL |
| **C-E1** (T0) | TE vs non-TE rare-SNV PWM Δ (non-HBB) | `te_alu_3d/.../exp_te_vs_nonte_rare_snv_pwm/` | **T0_PASS_FREEZE** / PENDING_FETCH — no genome-wide non-HBB panel on disk |

## Prior outcomes same day (still stand)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| **C-H1** (robust) | TE-pELS Gnocchi sensitivity | `se_llps/.../exp_te_derived_pels_gnocchi/` | **SUPPORT_WITH_CAVEATS** — core/LOCO \|\Δ\|≥0.20; LINE-only \|\Δ\|=0.025 kill |
| **C-F1** | Mustache vs HiCCUPS TE-anchor Jaccard | `te_alu_3d/.../exp_te_loop_caller_concordance/` | **BLOCKED_DATA** — no Mustache K562 GRCh38 bedpe |
| **C-G1** | RAD21 vs CTCF ChIA TE odds | `te_alu_3d/.../exp_rad21_vs_ctcf_chia_te_odds/` | **BLOCKED_DATA** — no RAD21 GRCh38 loop bedpe |

## Prior wave (2026-07-20) still stands

See `AUTONOMOUS_DESK_WAVE_2026-07-20.md` for C-A1…C-L1 closes.

## C-D1 summary

- Prereg Standard claim before outcomes; accessions frozen (`ENCFF511QFN` / `ENCFF693XIL` / UCSC rmsk).
- Unit = 1 kb midpoint windows; age = min milliDiv among overlapping SINE/LINE/LTR; tertiles.
- Primary Δ_repro (old−young) **−0.0037** (boot CI [−0.0062, −0.0014]); Alu-only **−0.0043**.
- Absolute repro ~2.5–3.0% flat across tertiles; class-stratified |Δ|≪0.05.
- null_results REJECT filed.

## Parked / next

| ID | Status |
|----|--------|
| C-E1 | **T0_PASS_FREEZE** / PENDING_FETCH — primary δ deferred |
| C-J1 / C-L1-crosscell | parked |

## Recommendation

Merge this wave. Next: **C-E1 fetch** (non-HBB rare-SNV panel + umap) or human pause. Holdout / C1 / wet remain untouched.
