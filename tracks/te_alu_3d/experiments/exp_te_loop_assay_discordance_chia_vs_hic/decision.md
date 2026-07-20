# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `INCONCLUSIVE_REPLICATION` (K562 FAIL strengthened by umap; GM12878 OR mid-zone)

## Verdict

**Combined (claim.md falsification rule): NOT yet claim-level REJECT.**

| Arm | AluSz Fisher OR | Woolf 95% CI | Gate |
|-----|-----------------|--------------|------|
| K562 desk (T3) | **0.908** | 0.851–0.967 | `FAIL_DESK_PRIMARY` (OR < 1.1) |
| K562 umap ≥ 0.3 (T4 primary) | **0.898** | 0.842–0.957 | strengthens FAIL |
| K562 umap ≥ 0.5 (sensitivity) | **0.894** | — | still < 1.1 |
| GM12878 replication (T5) | **1.252** | 1.172–1.339 | `INCONCLUSIVE_REPLICATION` (1.15 ≤ OR < 1.3) |

**MAPQ:** `N/A` on processed bedpe (`ENCFF511QFN` / `ENCFF693XIL`); Umap k100 mean is the
preregistered MAPQ≥30-spirit proxy (`results/sensitivity_mappability.*`).

**null_results/:** **Not filed.** Preregistered filing rule requires (a) OR < 1.1 after
mappability **and** (b) replication OR < 1.15 or opposite. Arm (a) met; arm (b) not
(GM12878 OR ≈ 1.25). Cross-cell-type sign differs (K562 depletion vs GM12878 mild elevation
below MCID) — recorded honestly; does **not** authorize post-hoc TE switch or claim inflation.

Primary TE remains frozen **AluSz**.

## Current gate

| Gate | Status |
|------|--------|
| Deep Research promote | `VALIDATE_DESK` (C-A1; score 7.06) |
| Standard-tier preregistration | Written |
| T0 / accession freeze K562 | **DONE** — Pol II `ENCFF511QFN`; Hi-C `ENCFF693XIL` |
| T2 CTCF gate K562 | **PASS** (OR 5.12) |
| T3 primary AluSz OR | **DONE** → `FAIL_DESK_PRIMARY` |
| T4 MAPQ/umap kill-test | **DONE** — MAPQ=N/A; umap≥0.3 OR **0.898** < 1.1 |
| Replication freeze | **DONE** — GM12878 `ACCESSION_FREEZE_replication_v1.md` |
| T5 GM12878 AluSz OR | **DONE** — OR **1.252** → `INCONCLUSIVE_REPLICATION` |
| T5 GM12878 CTCF gate | **PASS** (OR ≈ 10.74) |
| Holdout | SEALED |
| Wet-lab / oligos | FORBIDDEN |
| null_results filing | **Deferred** (replication not in falsify zone) |

## Stop / branch rules

- Desk OR < 1.1 → `FAIL_DESK_PRIMARY` (done).
- Umap≥0.3 still OR < 1.1 → strengthens FAIL (done); MAPQ=N/A documented.
- Claim REJECT + `null_results/` only if umap-gated OR < 1.1 **and** replication OR < 1.15
  or opposite — **not met** (replication OR 1.252).
- Do not promote exploratory AluJo / SVA_F; do not switch primary TE.
- Do not claim mechanism / wet GO / holdout / C1 E–P edits.

## What this does NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  
5. Not claim-level REJECT (replication inconclusive vs falsify rule)  
6. Not enrichment support at MCID (K562 fails; GM12878 OR < 1.3)  
7. Not authorization to rebrand GM12878 mid-zone OR as SUPPORT

## Arts

- `results/sensitivity_mappability.json|.md`
- `results/replication_gm12878_OR_CI.json|.md`
- `ACCESSION_FREEZE_replication_v1.md`
