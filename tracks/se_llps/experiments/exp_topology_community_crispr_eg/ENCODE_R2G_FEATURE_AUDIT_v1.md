# ENCODE-rE2G feature audit v1 — adversarial gate for C-B1

**Experiment:** `exp_topology_community_crispr_eg`  
**Date:** 2026-07-20  
**Audit type:** Desk literature / public docs / public feature tables (no model retrain)  
**Question:** Does ENCODE-rE2G already include loop / topology features that would make a
naive “add 3D topology for CRISPR E–G prediction” claim non-novel or already answered?

## Sources inspected

1. Gschwind et al. encyclopedia of enhancer–gene interactions (ENCODE companion; PMC10680627 /
   Nature 2026 companion lineage) — model feature narrative.
2. EngreitzLab/`ENCODE_rE2G` public repo feature tables:
   - `models/dhs_megamap/feature_table.tsv` (portable / DNase+megamap Hi-C style model)
   - `models/extended/feature_table.tsv` (ENCODE-rE2G **Extended**)
3. ENCODE portal Annotation sets for K562 ENCODE-rE2G predictions (e.g. `ENCSR512SWG`,
   extended `ENCSR621BIJ`) — confirms released prediction products exist (not used as
   training leakage for this claim).

## Finding — base ENCODE-rE2G

The portable model already includes **3D contact frequency** (averaged / megamap Hi-C) and
**ABC score** (activity × contact), plus distance, DNase activity, nearby-enhancer activity,
and promoter-class features.

**Implication:** pairwise 3D contact is **already** a first-class predictor of CRISPR E–G
labels in the field’s SOTA supervised baseline.

## Finding — ENCODE-rE2G Extended

Extended feature table explicitly includes loop- and domain-adjacent features, including
(names from `models/extended/feature_table.tsv`):

| Feature | Nice name / meaning |
|---------|---------------------|
| `HiCLoopOutsideNormalized` | Hi-C loops spanning E–P pair |
| `HiCLoopCrossNormalized` | Hi-C loops crossing E–P pair |
| `PEToutsideNormalized` / `PETcrossNormalized` | CTCF ChIA-PET span/cross |
| `inTAD` / `inCCD` | Domain co-membership flags |
| `3DContact` / `ABCScore` | Contact + ABC (as in base) |
| GraphReg / EpiMap / histone gradients | Additional multi-assay topology-ish signal |

**Implication:** **binary/span Hi-C loop features and domain flags are already inside
rE2G Extended.** A claim that “loops have never been used for CRISPR E–G prediction” is
**false**.

## What is NOT clearly in rE2G (gap for redesign)

Public feature tables do **not** list Louvain/Leiden **CRE-community IDs**, community size,
or same-community(E, promoter) indicators derived from a CRE–CRE loop graph as distinct
columns. Higher-order **community topology** (graph clustering over CRE nodes) is therefore
the only honest incremental angle relative to rE2G’s pairwise contact/loop/domain features.

## Verdict for C-B1

**`SURVIVES_WITH_REDESIGN`**

| Naive framing | Honest framing (required) |
|---------------|---------------------------|
| “Does 3D add predictive value for CRISPR E–G?” | Already answered affirmatively by rE2G (contact/ABC; Extended loops) |
| “Do Hi-C loops predict CRISPR E–G?” | Partially absorbed by rE2G Extended loop-span features |
| “Does **CRE-community co-membership** add ΔAUC ≥ 0.05 over **linear SE membership** under chrom holdout?” | **Still open** — different baseline (SE, not full rE2G) and different feature class (community vs pairwise loop/contact) |

## One-line conclusion

**rE2G already includes 3D contact (base) and Hi-C loop / PET / TAD features (Extended); C-B1 survives only as higher-order CRE-community topology incremental over SE membership — not as a claim that 3D/loops are novel for CRISPR E–G prediction.**

## Operational consequences

1. Proceed with prereg + T0 freeze under the redesigned estimand (claim.md).
2. Do **not** use ENCODE-rE2G scores as primary features (leakage / non-estimand).
3. Do **not** treat beating SE-only as beating rE2G; optional EXPLORATORY ceiling vs
   distance or vs published rE2G scores may be reported later with explicit labeling.
4. If community features collapse to near-duplicates of `HiCLoop*` / `inTAD`, pre-declare
   failure mode → likely REJECT or INCONCLUSIVE, not silent rebrand.
