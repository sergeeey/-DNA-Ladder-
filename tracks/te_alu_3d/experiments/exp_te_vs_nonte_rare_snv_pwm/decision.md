# Decision — exp_te_vs_nonte_rare_snv_pwm (C-E1)

**Date:** 2026-07-21  
**Verdict:** **REJECT** (`FAIL_KILL`)  
**Primary:** Cliff's δ (TE − non-TE) on |ctcf_pwm_delta_v1.1| = **0.033** (boot 95% CI [0.005, 0.061])

## Gate

Claim frozen at T0 (`T0_PASS_FREEZE`). Fetch completed (real gnomAD GraphQL r4 +
Hoffman umap k100 + UCSC rmsk Alu/SVA). Match locked **before** PWM attach
(`results/matching_lock.json`). Holdout remained SEALED; HBB excluded.

## Result

| Element | Value |
|---------|------:|
| Scope | chr11 CTCF±250 bp neighborhoods; HBB + HO geography excluded |
| Rare SNVs (AF≤0.001) | 55 849 |
| TE (Alu/SVA) / non-TE | 2 961 / 52 888 |
| Matched pairs (chrom + umap q4) | 2 961 |
| Scored pairs | 2 961 |
| mean \|PWM Δ\| TE / non-TE | 4.087 / 4.087 |
| Cliff's δ | **0.033** |
| Boot CI 95% | [0.005, 0.061] |
| SUPPORT (≥0.20) | FAIL |
| Kill (\|δ\| < 0.05) | **HIT → REJECT** |

## Scorer diagnostic (honest)

Exploratory `ctcf_pwm_delta_v1.1` yields a near-discrete \|Δ\| mass at
≈ log₂(0.85/0.05) ≈ **4.087** for nearly all SNVs (PWM extreme contrasts). TE and
non-TE distributions are effectively identical under this frozen scorer — the
pre-registered estimand still falsifies (kill). This does **not** license a
post-hoc scorer swap.

## What this does NOT mean

1. NOT that TE vs non-TE rare SNVs never differ under a different disruption
   model (ARCHCODE / AlphaGenome confirmatory path remains separate).  
2. NOT license to reopen Track A HBB enrichment as primary.  
3. NOT holdout unblind / wet / C1.  
4. NOT a claim that mappability matching failed — umap-q4 1:1 lock completed.

## Artifacts

- `data/input/fetch_meta.json` (panel summary; bulky panel/umap gitignored)
- `results/matching_lock.json`, `results/primary_result_cliffs_delta.json`
- `results/matched_scored_pairs.jsonl`
- Scripts: `scripts/fetch_c_e1_panel.py`, `scripts/run_c_e1_analysis.py`, `scripts/c_e1_lib.py`
- Null: `null_results/20260721-te-vs-nonte-rare-snv-pwm.md`

## Next

**PAUSE** autonomous remaps. Remaining open registry fruit: **C-J1** only
(orientation vs loop-anchor asymmetry) among unscored Deep Research IDs; do not
auto-start infinite remaps. Holdout / C1 / wet untouched.
