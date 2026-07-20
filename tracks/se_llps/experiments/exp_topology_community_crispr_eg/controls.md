# Controls — exp_topology_community_crispr_eg (C-B1 topology / CRISPR E–G)

**Status:** PREREGISTERED_DESK (2026-07-20)  
**Parent claim:** `claim.md`  
**Adversarial gate:** `ENCODE_R2G_FEATURE_AUDIT_v1.md` **must** be filed before kill-test.

## Primary metric and kill protocol

| Item | Pre-registered rule |
|------|---------------------|
| Primary discrimination metric | **ROC-AUC** on frozen labels |
| Parallel report | AUPRC (ENCODE-rE2G convention) — secondary; does not override kill |
| Split | Hold-one-chromosome-out (or frozen chromosome list identical across models) |
| ΔAUC | AUC(topology+SE) − AUC(SE-only) on the **same** held-out chromosomes |
| MCID (SUPPORT) | ΔAUC ≥ **0.05** |
| Kill (REJECT) | ΔAUC < **0.02** |
| Gray | 0.02 ≤ ΔAUC < 0.05 → INCONCLUSIVE |

No post-hoc switch of primary metric after seeing results.

## Baseline model (frozen)

**SE-only:** binary (or continuous SE-rank if pre-declared) membership of the CRISPR element
interval in track SE calls (`k562_super_enhancers_grch38.json`), plus intercept.

**Optional sensitivity (not primary):** `SE + distanceToTSS` — report separately; kill-test
remains vs SE-only unless claim.md is amended **before** fit.

## Topology model (frozen intent)

Build a CRE graph from frozen K562 Hi-C **loop** calls (`ENCFF693XIL`) with nodes = cCRE
intervals (v3 preferred). Pre-registered topology features (final column list locked in
`ACCESSION_FREEZE_v1.md` / a future `feature_freeze.md` before fit):

1. **Same-community(E, gene-TSS or promoter cCRE)** — Louvain / Leiden community ID match
2. **Community size** of element’s community
3. **Intra-community degree** of element (loop-anchor degree within community)
4. SE membership (included so the comparison is nested / incremental)

**Excluded from “topology”** (already covered by rE2G or too close to contact baselines):

- Raw Hi-C contact frequency alone as the sole novel feature
- ABC score / DNase×contact products (rE2G core)
- Claiming novelty from `HiCLoopOutsideNormalized` / `HiCLoopCrossNormalized` as if unused
  by the field (they appear in ENCODE-rE2G **Extended**)

If T0 shows only pairwise contact is available and community construction is blocked →
status `BLOCKED_DATA` or `SURVIVES_WITH_REDESIGN` demotion — do not silently swap in ABC.

## Positive control gate

**Distance-to-TSS alone** should beat chance (AUC ≫ 0.5) on the same CRISPR labels.
Failure → `BLOCKED_PIPELINE` (label/join bug) before interpreting topology ΔAUC.

## Negative / leakage controls

1. **Chromosome isolation:** no feature computed using held-out chromosome edges/labels.
2. **No rE2G score leakage:** do not include ENCODE-rE2G prediction scores as features in the
   primary SE vs topology+SE comparison (optional *exploratory* ceiling analysis only,
   labeled EXPLORATORY).
3. **No SE enrichment reopen:** do not re-test G4/R-loop/Gnocchi/VUS endpoints in this
   experiment folder.
4. **C-A1 firewall:** do not compute TE-subfamily ORs or assay-discordance sets here.

## Adversarial requirement (FIRST)

Before the main ΔAUC kill-test, complete desk audit:

> Does ENCODE-rE2G already include loop / topology features?

Document in `ENCODE_R2G_FEATURE_AUDIT_v1.md` with honest
`SURVIVES` / `SURVIVES_WITH_REDESIGN` / `KILLED_BY_FRONTIER` verdict.

**Expected posture (pre-audit hypothesis):** SURVIVES_WITH_REDESIGN — contact and Extended
loop features exist; higher-order community co-membership over **SE baseline** may still be
testable if clearly scoped.

## Checklist before kill-test (T1+)

| Item | Status |
|------|--------|
| claim.md frozen | DONE (this PR) |
| rE2G feature audit filed | THIS PR |
| CRISPR benchmark SHA pinned | T0 |
| Hi-C loops accession frozen | T0 |
| cCRE v3 availability recorded | T0 |
| SE intervals on disk | YES (track input) |
| Community feature columns frozen | PENDING (next session) |
| Chromosome folds frozen | PENDING (next session) |
| Full ML ΔAUC | **NOT THIS SESSION** |

## Forbidden post-hoc moves

- Changing kill threshold after seeing ΔAUC
- Switching baseline from SE to “empty” or to full rE2G to manufacture ΔAUC
- Dropping chromosomes that hurt topology
- Relabeling gray-zone as SUPPORT
