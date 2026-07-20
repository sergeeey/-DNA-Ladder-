# Primary result — AluSz OR (T3 desk)

**Computed:** `2026-07-20T07:03:22.039182+00:00`  
**Primary TE:** `AluSz` (frozen; not post-hoc)  
**Desk verdict:** `FAIL_DESK_PRIMARY`  
**MAPQ / mappability:** `PENDING_MAPPABILITY`

## Estimand

Fisher odds ratio for **AluSz** overlap in **fixed 1 kb midpoint windows** of
non-redundant merged anchors (≥1 kb) from Pol II ChIA-PET (`ENCFF511QFN`) vs
Hi-C (`ENCFF693XIL`), K562 / GRCh38.

Descriptive association in processed public call sets only — **not** causal.
Full-span overlap is reported only as width-confounded sensitivity.

## Anchor counts

| Arm | Raw unique | Merged ≥1 kb | 1 kb scoring windows |
|-----|------------|--------------|----------------------|
| Pol II ChIA-PET | 1463166 | 572808 | 572808 |
| Hi-C | 24049 | 17183 | 17183 |

## Primary AluSz statistics

| Metric | Value |
|--------|-------|
| Pol II AluSz+ / n | 31531 / 572808 (rate 0.0550) |
| Hi-C AluSz+ / n | 1036 / 17183 (rate 0.0603) |
| Fisher OR | **0.9075** |
| Fisher p (two-sided) | 3.3562e-03 |
| Woolf OR 95% CI | 0.8514 – 0.9673 |
| Chrom block-bootstrap 95% CI | 0.8659 – 0.9581 (n_boot=500) |
| MCID support / fail | ≥1.3 / <1.1 |

**Verdict note:** OR=0.9075 < falsify threshold 1.1 at desk primary stage. Full claim REJECT per claim.md still requires MAPQ≥30 (or equivalent) + replication — not filed as null_results REJECT yet.

## Matched-null permutations

| Metric | Value |
|--------|-------|
| n_perm | 200 |
| Matching | chromosome + width quartile (pooled arms); GC PENDING (no FASTA) |
| Null OR mean / median | 0.9852 / 0.9820 |
| Null OR 95% central | 0.9302 – 1.0493 |
| Empirical p (two-sided) | 0.01493 |

## Full-span sensitivity (not primary)

| Metric | Value |
|--------|-------|
| Fisher OR (full merged span) | 0.1358 |
| Note | Full merged-interval overlap; confounded by non-overlapping width distributions across assays. Not the primary estimand. |

## Limitations (honest)

1. `PENDING_MAPPABILITY` — Processed ENCODE bedpe (ENCFF511QFN / ENCFF693XIL) lack per-anchor MAPQ fields usable for MAPQ≥30 filtering; umap track not available in this worktree. Primary OR reported with PENDING_MAPPABILITY caveat; MAPQ/umap sensitivity deferred.
2. GC matching not applied (no hg38 FASTA in worktree) — chromosome + width strata (widths equalized at 1 kb for primary).
3. Single cell type (K562); claim.md full REJECT needs MAPQ gate + replication.

## Exploratory secondary (NOT primary)

See `exploratory_secondary_TE.tsv` for SVA_F and AluJo. Do not promote to claim language.

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT wet-lab / oligo / C1 E–P authorization.
3. NOT holdout unseal.
4. NOT a multi-cell-type replicated claim.

