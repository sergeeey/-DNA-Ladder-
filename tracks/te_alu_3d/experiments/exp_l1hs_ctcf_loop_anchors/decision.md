# Decision — exp_l1hs_ctcf_loop_anchors (C-L1)

**Date:** 2026-07-20  
**Verdict:** **REJECT** (`FAIL_KILL`)  
**Primary cell:** K562 OR = **0.143** (< 1.1); umap≥0.3 OR = **0.143**

## Result

| Cell | n matched | median len case/ctrl | table [a,b;c,d] | OR (95% CI) | umap≥0.3 OR | Verdict |
|------|----------:|---------------------:|-----------------|-------------:|------------:|---------|
| K562 (primary) | 1514 | 424/424 | [0,1514;3,1511] | **0.143** (0.007–2.76) | 0.143 | REJECT |
| HCT116 | 5312 | 376/379 | [0,5312;2,5310] | **0.200** (0.010–4.17) | 0.200 | REJECT |

L1HS 5′UTR overlap at CTCF peaks is **extremely rare** (≤3 events in matched controls; **0** in matched on-anchor cases). Point estimate is below kill threshold in both cells; direction opposite of enrichment.

## Unit gate (honest)

1. Mid-1 kb windows → ~0 L1HS hits (underpowered).  
2. Hi-C-anchor-as-unit (median ~10 kb) cannot length-match CTCF peaks (~0.4 kb).  
3. **Primary unit:** CTCF peak on vs off Hi-C anchor, length+umap matched — lengths balanced (424/424 K562).

## What this does NOT mean

1. NOT that L1HS never touches loops — only that L1HS **5′UTR ∩ CTCF peak** is not enriched on anchors under this estimand.  
2. NOT a reopen of C-A1 AluSz discordance.  
3. NOT wet / holdout / C1 license.  
4. Sparse events → wide CIs; kill is on OR&lt;1.1 after umap, which holds.

## Artifacts

- `results/matching_lock.json`, `results/primary_result_OR_CI.json`
- Scripts: `scripts/run_c_l1_analysis.py`, `scripts/c_l1_lib.py`
- Null: `null_results/20260720-l1hs-ctcf-loop-anchor-enrichment.md`

## Next

**STOP autonomous wave** — write `AUTONOMOUS_DESK_WAVE_2026-07-20.md`. Do not auto-start C-F1/C-D1/C-E1/C-G1/C-J1 overnight.
