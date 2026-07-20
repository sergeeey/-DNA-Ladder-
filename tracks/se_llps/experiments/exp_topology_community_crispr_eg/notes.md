# Notes — exp_topology_community_crispr_eg (C-B1)

## Why this desk fruit now

C-A1 (TE ChIA-PET vs Hi-C discordance) closed **INCONCLUSIVE_CROSS_CELL** on 2026-07-20.
Deep Research next-fruit slot pointed at “C-B1.” Standing order for this session fills that
slot with a **Predictive** topology-vs-SE CRISPR E–G question (not the registry’s parked
AluY+AG TE candidate).

## Why under `tracks/se_llps/`

Baseline is **SE membership**; estimand is incremental topology over SE for CRISPR pairs.
Not TE-specific → not `te_alu_3d` primary science. Track already holds SE intervals and
closed SE enrichment nulls we must not reopen.

## ID collision (registry vs standing order)

| ID | Estimand | Status |
|----|----------|--------|
| **C-B1** (this folder) | Topology community ΔAUC ≥ 0.05 over SE for CRISPR E–G (K562) | **ACTIVE desk** |
| **C-B1-TE-AluY-AG** | AluY @ convergent CTCF+RAD21 + AG allele-prior (registry score 7.47) | **PARKED** (needs AG creds; TE track) |

## Adversarial posture

ENCODE-rE2G already predicts CRISPR E–G with DNase + **3D contact** + ABC; Extended adds
**Hi-C loop** span/cross features, ChIA-PET PET counts, TAD/CCD flags, GraphReg, etc.
Therefore this experiment **cannot** claim “3D is novel for E–G prediction.” It can only
ask whether **higher-order CRE-community topology** adds ΔAUC over a deliberately weak
**SE-membership** baseline. Full audit: `ENCODE_R2G_FEATURE_AUDIT_v1.md`.

## Session boundary

This PR: prereg + T0 probe + accession freeze + rE2G audit + docs.  
**Stop before** chromosome-holdout ML ΔAUC unless all freezes are in hand (they will be
metadata-frozen here; feature engineering / fit deferred).

## Links

- Closed C-A1: `tracks/te_alu_3d/experiments/exp_te_loop_assay_discordance_chia_vs_hic/`
- Deep Research: `tracks/te_alu_3d/09_outputs/prospective/DEEP_RESEARCH_REPORT_C_A1_v1.md`
- null_results SE track: `null_results/INDEX.md`
