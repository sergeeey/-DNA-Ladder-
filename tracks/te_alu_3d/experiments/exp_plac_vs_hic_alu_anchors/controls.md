# Controls — exp_plac_vs_hic_alu_anchors (C-K1)

**Status:** PREREGISTERED_DESK (2026-07-20) — **not executed** (`BLOCKED_DATA` at T0)  
**Parent claim:** `claim.md`

## Positive control gate — CTCF

**Purpose:** Sanity that the anchor-intersection pipeline recovers architecture signal
before trusting AluSz OR.

- Cell-matched CTCF peaks (reuse C-A1 freezes if unblocked: GM12878 `ENCFF796WRU` /
  K562 `ENCFF769AUF`).
- Gate: Fisher OR ≥ **2.0** for CTCF overlap on Hi-C (or PLAC) anchors vs chromosome-
  preserving shuffle → PASS.
- Failure → `BLOCKED_PIPELINE` (do not interpret AluSz biology).

**T0 status:** NOT RUN (no PLAC bedpe to gate against).

## Negative / contrast — AluJo

- AluJo tracked as contrast only; must not silently become the headline if AluSz fails.
- Primary TE remains **AluSz** (exact `repName`).

## Matched-null / contrast design (if unblocked)

| Covariate | Rule |
|-----------|------|
| Chromosome | Prefer same chr |
| Anchor width | Same bin (≥1 kb pad) |
| Mappability | Umap k100 mean; primary sensitivity **umap ≥ 0.3** |
| GC | Same bin if FASTA available; else PENDING_GC logged |

Contrast: PLAC anchors vs Hi-C anchors (same cell). Optional matched-null permutations
reuse C-A1 `t3_primary_alusz_or.py` discipline (n_perm≥200).

## Sensitivity list (pre-registered)

1. **umap ≥ 0.3** — primary falsification kill-test (OR < 1.1 → REJECT)  
2. umap ≥ 0.5 (stricter)  
3. Autosomes only  
4. Drop blacklist / segdup overlaps  
5. Window-size pad sensitivity  

## Checklist

| Item | Status |
|------|--------|
| claim.md L0 Descriptive | DONE |
| T0 PLAC processed bedpe (GM12878 or K562, GRCh38) | **FAIL → BLOCKED_DATA** |
| Matched Hi-C bedpe freeze | N/A |
| CTCF gate | N/A |
| Primary AluSz OR | N/A |
| umap ≥ 0.3 | N/A |
| null_results (REJECT/INCONCLUSIVE) | N/A — data block, not falsification |
