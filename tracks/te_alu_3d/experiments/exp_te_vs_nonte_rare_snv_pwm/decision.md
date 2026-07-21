# Decision — exp_te_vs_nonte_rare_snv_pwm (C-E1)

**Date:** 2026-07-21  
**Verdict:** **T0_PASS_FREEZE** / **PENDING_FETCH**  
**Stage:** T0 only — Cliff's δ **not computed**

## Gate

Claim frozen. Local probe (`data/t0_accession_probe.json`):

| Asset | Status |
|-------|--------|
| PWM scorer v1.1 | PRESENT |
| HBB gnomAD | PRESENT — excluded (dev set) |
| Holdout HO_* | SEALED — forbidden |
| Genome-wide non-HBB rare SNV TE∪non-TE panel | **ABSENT** |
| Umap k100 in exp `data/input` | **ABSENT** |

Primary analysis deferred until non-HBB panel + umap fetch. Not `BLOCKED_DATA`
(public gnomAD/Hoffman paths exist) — honest `PENDING_FETCH`.

## What this does NOT mean

1. NOT a REJECT/SUPPORT of TE vs non-TE PWM Δ (outcomes not entered).
2. NOT license to reopen Track A HBB enrichment as primary.
3. NOT holdout unblind / wet / C1.

## Next

Fetch non-HBB rare-SNV panel (exclude HBB + HO), download umap, match-before-PWM,
then primary Cliff's δ. Or human pause.
