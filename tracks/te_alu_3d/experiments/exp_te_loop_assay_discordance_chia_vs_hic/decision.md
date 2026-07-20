# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `FAIL_DESK_PRIMARY`

## Verdict

**T3 primary AluSz desk OR: `FAIL_DESK_PRIMARY`.**

Fisher OR for AluSz overlap (1 kb midpoint windows of merged ≥1 kb anchors),
Pol II ChIA-PET (`ENCFF511QFN`) vs Hi-C (`ENCFF693XIL`):

| Metric | Value |
|--------|-------|
| n Pol II / n Hi-C | **572808** / **17183** |
| AluSz+ Pol II / Hi-C | 31531 / 1036 |
| Fisher OR | **0.908** |
| Woolf 95% CI | **0.851 – 0.967** |
| Chrom block-bootstrap 95% CI | 0.866 – 0.958 (n_boot=500) |
| Matched-null | **run** (n_perm=200; chr + width; GC PENDING) |
| Null OR mean | 0.985 |
| Emp. p (two-sided) | 0.015 |
| MAPQ / mappability | `PENDING_MAPPABILITY` |
| Desk threshold | support ≥1.3; fail <1.1 |
| Desk verdict | **FAIL_DESK_PRIMARY** (OR < 1.1) |

Single-cell-type (K562) stage only. Per `claim.md`, full **REJECT** still requires
MAPQ≥30 (or equivalent high-mappability gate) **and** replication — **not** filed
in `null_results/` yet. Pending replication cell type / biorep + mappability kill-test.

Exploratory secondary (not claim): AluJo OR≈0.988 (near 1, as expected contrast);
SVA_F OR≈0.985 (wide CI). Primary subfamily remains frozen **AluSz** (no post-hoc swap).

## Current gate

| Gate | Status |
|------|--------|
| Deep Research promote | `VALIDATE_DESK` (C-A1; score 7.06) |
| Standard-tier preregistration | Written (`claim.md`, `controls.md`, `notes.md`) |
| T0 ENCODE accession probe | **PASS** |
| Accession freeze | **DONE** — Pol II `ENCFF511QFN`; Hi-C `ENCFF693XIL` |
| Primary bedpe on-disk download + md5 | **DONE** |
| CTCF accession freeze | **DONE** — `ENCFF769AUF` |
| T2 CTCF positive control gate | **PASS** (OR 5.12) |
| T1 TE annotation skeleton | **EXPLORATORY_PARTIAL** |
| T3 primary AluSz OR | **DONE** → `FAIL_DESK_PRIMARY` |
| MAPQ / umap kill-test | **PENDING_MAPPABILITY** |
| Replication cell type | **PENDING** |
| Holdout | SEALED (untouched) |
| Wet-lab / oligos | FORBIDDEN |
| null_results filing | **Deferred** (desk fail ≠ claim REJECT yet) |

### T3 primary summary

Source: `results/primary_result_OR_CI.json` / `.tsv` / `.md`;
`results/permutation_null_summary.json`; `results/exploratory_secondary_TE.tsv`.

### T2 CTCF gate summary

| Metric | Value |
|--------|-------|
| Fisher OR | **5.119** |
| Verdict | **PASS** |

## Stop / branch rules

- Desk OR < 1.1 → `FAIL_DESK_PRIMARY` (triggered); await MAPQ + replication before claim REJECT.
- MAPQ≥30 + replication yield OR < 1.1 for all pre-registered subfamilies → `REJECT` + `null_results/`.
- Do not promote exploratory AluJo / SVA_F to primary.
- Do not claim mechanism / wet GO / holdout / C1 E–P edits.

## What this does NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  
5. Not a finalized multi-cell-type REJECT (MAPQ + replication still open)  
6. Not enrichment support for AluSz (desk OR below falsify threshold)

## Next edit to this file

After MAPQ/umap sensitivity and/or independent cell-type / biorep replication →
upgrade to SUPPORT / REJECT / INCONCLUSIVE with honest numbers; file `null_results/`
only on claim-level REJECT/FAIL per falsification rule.
