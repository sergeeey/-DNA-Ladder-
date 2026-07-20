# Controls — exp_topology_community_crispr_eg (C-B1 topology / CRISPR E–G)

**Status:** KILL_TEST_COMPLETE (2026-07-20) — **FAIL_KILL**  
**Parent claim:** `claim.md`  
**Adversarial gate:** `ENCODE_R2G_FEATURE_AUDIT_v1.md` → **SURVIVES_WITH_REDESIGN**

## Primary metric and kill protocol

| Item | Pre-registered rule |
|------|---------------------|
| Primary discrimination metric | **ROC-AUC** on frozen labels |
| Parallel report | AUPRC — secondary |
| Split | Train = all chroms except chr20–22; test = chr20–22 (+ LOCV mean secondary) |
| ΔAUC | AUC(baseline+topology) − AUC(baseline) on held-out chroms |
| MCID (SUPPORT / PASS_KILL) | ΔAUC ≥ **0.05** |
| Kill (FAIL_KILL / REJECT) | ΔAUC < **0.02** |
| Gray | 0.02 ≤ ΔAUC < 0.05 → INCONCLUSIVE |

## Baseline model (redesigned before fit)

1. `log10_distance`
2. `activity_els` — cCRE pELS/dELS overlap (`ENCFF210CAN`)
3. `se_membership` — dbSUPER K562 SE

## Topology model

Built from `ENCFF693XIL` intra-chromosomal loop graph:

1. enhancer loop degree
2. promoter loop degree (TSS ± 2 kb)
3. shared community size (connected component)
4. min loop-span rank (inverted for model)

**Excluded:** raw contact frequency alone; ABC; rE2G scores; claiming novelty from
`HiCLoop*` Extended features.

## Controls (executed)

| Control | Result |
|---------|--------|
| Distance alone AUC > 0.55 | **0.8796 PASS** |
| Shuffle-label null ΔAUC near 0 | mean **+0.009** (observed ΔAUC −0.007 within null noise) |
| No rE2G score leakage | Confirmed — not used |
| Chromosome isolation | Features from loops only; labels unused in feature build |

## Observed primary

ΔAUC = **−0.0073** → **FAIL_KILL**.
