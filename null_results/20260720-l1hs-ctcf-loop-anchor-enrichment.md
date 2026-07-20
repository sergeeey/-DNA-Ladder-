# Null result — L1HS 5′UTR enrichment at CTCF∩Hi-C loop anchors?

**ID:** 20260720-l1hs-ctcf-loop-anchor-enrichment  
**Date:** 2026-07-20  
**Track:** te_alu_3d  
**Experiment:** `tracks/te_alu_3d/experiments/exp_l1hs_ctcf_loop_anchors/`  
**Candidate:** C-L1 (true L1HS@CTCF; not cross-cell transfer)  
**Verdict:** REJECT (`FAIL_KILL`)

## Claim (frozen)

OR(L1HS 5′UTR | CTCF peak on Hi-C anchor) ≥ 1.4 vs length/umap-matched background CTCF;
kill if OR &lt; 1.1 after umap ≥ 0.3.

## Result

K562 primary OR **0.143** (umap 0.143); HCT116 OR **0.200**. Both &lt; 1.1. Events sparse (0 vs 3 K562).

## What this does NOT mean

1. Does **not** imply L1HS is irrelevant to 3D genome biology outside CTCF-peak∩5′UTR.  
2. Does **not** reopen C-A1 / C-H1 / SE nulls.  
3. Does **not** authorize wet / holdout / C1 work.  
4. Does **not** validate mid-1kb or Hi-C-anchor-as-unit designs (rejected at unit gate).
