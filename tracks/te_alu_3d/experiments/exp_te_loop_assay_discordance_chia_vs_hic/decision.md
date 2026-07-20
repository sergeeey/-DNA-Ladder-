# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `INCONCLUSIVE_REPLICATION` (three-cell synthesis; not claim REJECT)

## Verdict

**Combined (claim.md thresholds): NOT SUPPORT; NOT claim-level REJECT.**

Cross-cell pattern is **FAIL_INCONSISTENT** in sign (K562 depletion vs GM12878/HCT116
mild elevation below MCID), but falsification rule is **not** met because both
replication arms land in 1.15–1.3 mid-zone (not < 1.15 / opposite).

| Arm | AluSz Fisher OR | Woolf 95% CI | Gate |
|-----|-----------------|--------------|------|
| K562 desk (T3) | **0.908** | 0.851–0.967 | `FAIL_DESK_PRIMARY` (OR < 1.1) |
| K562 umap ≥ 0.3 (T4) | **0.898** | 0.842–0.957 | strengthens FAIL |
| GM12878 replication (T5) | **1.252** | 1.172–1.339 | `INCONCLUSIVE_REPLICATION` |
| HCT116 replication (T5b) | **1.280** | 1.162–1.410 | `INCONCLUSIVE_REPLICATION` |
| HCT116 umap ≥ 0.3 (optional) | **1.281** | — | still mid-zone |

**Claim thresholds (honest):**

- **Support** needs primary OR ≥ 1.3 **and** replication ≥ 1.15 same direction → **FAIL**
  (K562 primary OR < 1.1; replications < 1.3).
- **Falsify / REJECT** needs OR < 1.1 after mappability **and** replication not supporting
  (OR < 1.15 or opposite) → arm (a) met; arm (b) **not** (GM12878 1.252; HCT116 1.280).

**null_results/:** **Not filed.** Filing requires both falsification arms; replication does
not enter the falsify zone on either independent cell type.

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
| Replication freeze GM12878 | **DONE** — `ACCESSION_FREEZE_replication_v1.md` |
| T5 GM12878 AluSz OR | **DONE** — OR **1.252** → mid-zone |
| T5 GM12878 CTCF gate | **PASS** (OR ≈ 10.74) |
| Replication freeze HCT116 | **DONE** — `ACCESSION_FREEZE_replication_HCT116_v1.md` |
| T5b HCT116 AluSz OR | **DONE** — OR **1.280** → mid-zone |
| T5b HCT116 CTCF gate | **PASS** (OR ≈ 8.35) |
| HCT116 umap≥0.3 (optional) | **DONE** — OR **1.281** mid-zone |
| Holdout | SEALED |
| Wet-lab / oligos | FORBIDDEN |
| null_results filing | **Deferred** (replication arms not in falsify zone) |

## Stop / branch rules

- Desk OR < 1.1 → `FAIL_DESK_PRIMARY` (done).
- Umap≥0.3 still OR < 1.1 → strengthens FAIL (done); MAPQ=N/A documented.
- Claim REJECT + `null_results/` only if umap-gated OR < 1.1 **and** replication OR < 1.15
  or opposite — **not met** (GM12878 1.252; HCT116 1.280).
- Do not promote exploratory AluJo / SVA_F; do not switch primary TE.
- Do not claim mechanism / wet GO / holdout / C1 E–P edits.
- Honest stop: leave as `INCONCLUSIVE_REPLICATION` with documented cross-cell inconsistency.

## What this does NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  
5. Not claim-level REJECT (replication mid-zone on GM12878 **and** HCT116)  
6. Not enrichment support at MCID (K562 fails; both replications OR < 1.3)  
7. Not authorization to rebrand mid-zone OR as SUPPORT or to switch primary TE  
8. Not proof that GM12878/HCT116 mild elevation is biological (descriptive call-set association only)

## Arts

- `results/sensitivity_mappability.json|.md`
- `results/replication_gm12878_OR_CI.json|.md`
- `results/replication_hct116_OR_CI.json|.md`
- `results/replication_hct116_umap_sensitivity.json|.md`
- `ACCESSION_FREEZE_replication_v1.md`
- `ACCESSION_FREEZE_replication_HCT116_v1.md`
