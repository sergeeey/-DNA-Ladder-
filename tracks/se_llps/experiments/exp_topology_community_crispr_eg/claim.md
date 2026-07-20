---
experiment: exp_topology_community_crispr_eg
date: 2026-07-20
ladder_tier: Standard
question_type: Predictive
status: PENDING_KILL_TEST
candidate_id: C-B1
candidate_alias: C-B1-topology-crispr-eg
source: standing_order_post_C-A1_close + Deep Research next-fruit slot
accession_freeze: ACCESSION_FREEZE_v1.md
rE2G_audit: ENCODE_R2G_FEATURE_AUDIT_v1.md
t0_status: PASS_FREEZE
---

# Claim: 3D CRE-community topology adds predictive ΔAUC over linear SE membership for CRISPR-validated E–G pairs (K562)

## Status

**PENDING_KILL_TEST** — Standard tier; claim + T0 freeze + rE2G audit done; **no ΔAUC fit yet**.  
Chromosome-holdout kill-test is the next session’s job (community features not built in this PR).

**ID note:** Deep Research registry `C-B1` originally scored AluY@CTCF+RAD21+AG (TE track).
After C-A1 `INCONCLUSIVE_CROSS_CELL` close, standing order promotes **this** Predictive
estimand into the C-B1 desk slot (topology incremental over SE for CRISPR E–G). The TE
AluY/AG candidate remains **PARKED** as `C-B1-TE-AluY-AG` (see registry note). Do not
conflate the two.

## EstimandOps L0

**Question type:** Predictive.

Among frozen CRISPR-validated enhancer–gene (E–G) pairs in K562, does a **3D CRE-community
topology** feature set improve discrimination of CRISPR-positive vs powered-negative pairs
by **ΔAUC ≥ 0.05** relative to a **linear SE-membership** baseline (same universe, same
chromosome holdout protocol)?

Explicitly **not causal**: no claim that communities “cause” regulation. Explicitly **not**
a reopening of closed SE→LLPS / VUS / Gnocchi / R-loop / G4 enrichment claims. Explicitly
**not** C-A1 TE-discordance OR.

## Scientific question

Does higher-order 3D community structure among candidate cis-regulatory elements (CREs)
carry incremental predictive signal for CRISPR FlowFISH / CRISPRi E–G labels beyond whether
the element sits inside a super-enhancer?

## Frozen claim (pre-results)

Before any model fitting on the primary holdout:

> On the frozen K562 CRISPR E–G benchmark (chromosome-holdout evaluation), a pre-registered
> topology+SE model achieves **ΔAUC ≥ 0.05** over the SE-membership-only baseline
> (primary metric: ROC-AUC unless otherwise frozen in `controls.md` as AUPRC-primary with
> AUC reported in parallel).

**Kill / falsification (pre-registered):** if chromosome-holdout **ΔAUC < 0.02**, claim is
**REJECT** (topology does not clear the desk kill threshold over SE).

**Support band:** ΔAUC ≥ 0.05 → provisional SUPPORT (still subject to controls).  
**Gray zone:** 0.02 ≤ ΔAUC < 0.05 → INCONCLUSIVE (not SUPPORT; not REJECT).

## Primary estimand

| Slot | Definition |
|------|------------|
| **Universe** | Frozen CRISPR E–G pairs in K562 (EngreitzLab `EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz` + ENCODE Flow-FISH processed tables as cited in freeze) |
| **Label** | `Regulated` / Significant positive vs powered negative (as in benchmark; no re-thresholding after seeing ΔAUC) |
| **Baseline features** | Linear SE membership of the element (overlap with track SE intervals `k562_super_enhancers_grch38.json`); optional distance-to-TSS recorded but **not** mixed into baseline unless pre-registered as `baseline_SE_plus_distance` sensitivity |
| **Topology features** | CRE-community co-membership / community-graph features built from frozen K562 Hi-C **loops** (`ENCFF693XIL`) on cCRE nodes (v3 preferred; v4 documented fallback) — **not** raw pairwise contact frequency alone (see rE2G audit) |
| **Split** | Hold-one-chromosome-out (or frozen chromosome fold list) — same discipline as ENCODE-rE2G CRISPR CV |
| **Summary measure** | ΔAUC = AUC(topology+SE) − AUC(SE-only) |
| **MCID** | ΔAUC ≥ 0.05 |
| **Kill** | ΔAUC < 0.02 |

## Novelty check (mandatory)

| Closed / adjacent direction | Why this claim is distinct |
|-----------------------------|----------------------------|
| SE vs typical BRD4/MED1 ChIP | Descriptive LLPS enrichment — **REJECT**; here Predictive E–G labels |
| ClinVar VUS in SE / SE vs typical | Frequency / constraint — **REJECT**; different outcome |
| Gnocchi SE vs typical | Constraint — **REJECT** |
| R-loop / G4 SE vs typical | Non-B DNA overlap — **REJECT** |
| Continuous SE-size dichotomization | Below-MCID signal — **REJECT-with-signal**; not CRISPR E–G prediction |
| **C-A1** TE ChIA vs Hi-C discordance | Descriptive TE OR on loop anchors — **INCONCLUSIVE_CROSS_CELL**; no CRISPR labels, no SE baseline, no ΔAUC |
| Registry **C-B1-TE-AluY-AG** | TE + AG allele prior — **PARKED**; different L0 / data |

Honest frontier caveat: ENCODE-rE2G already uses 3D **contact** (and Extended uses **loop**/PET/TAD features) to predict the same CRISPR labels. This claim therefore **survives only with redesign** as incremental value of **higher-order community topology over SE membership**, not as “first use of 3D for E–G prediction.” See `ENCODE_R2G_FEATURE_AUDIT_v1.md`.

## Datasets (targets for T0 freeze)

| Role | Source | Expected freeze artifact |
|------|--------|--------------------------|
| CRISPR E–G labels (K562) | EngreitzLab ENCODE_rE2G `reference/EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz` (includes FlowFISH_K562); ENCODE Flow-FISH CRISPR screens as supporting processed tables | SHA-256 + URL/commit pin |
| Hi-C loops K562 | `ENCSR545YBD` / preferred_default bedpe **`ENCFF693XIL`** (same as C-A1 Hi-C primary) | Accession freeze |
| cCRE registry | SCREEN Registry-V3 `GRCh38-cCREs.bed` (preferred v3); ENCODE portal v3 K562 `ENCSR940SYU` / `ENCFF210CAN`; v4 agnostic `ENCSR800VNX` / `ENCFF420VPZ` as documented fallback | URL + size/etag or ENCFF |
| SE membership | Track `tracks/se_llps/data/input/k562_super_enhancers_grch38.json` | Already on disk |

## Allowed claim language

- “Topology+SE improves / does not improve CRISPR E–G discrimination by ΔAUC=… over SE-only under chromosome holdout.”
- “Predictive association on frozen public CRISPR labels; not causal.”

## Forbidden claim language

- Causal: “communities drive enhancer targeting,” “SE biology falsified/confirmed.”
- Reopening closed SE enrichment nulls as if newly tested.
- Claiming novelty as “first 3D E–G predictor” (rE2G already uses contact/loops).
- Wet-lab GO, holdout unblind, C1 E/P edits, TE AluY/AG analysis under this folder.

## Decision gate

See `decision.md` — remains `PENDING_T0` until probe JSON + freeze + rE2G audit land; then
`PENDING_KILL_TEST` (no full ML in this session unless all T0 artifacts frozen).
