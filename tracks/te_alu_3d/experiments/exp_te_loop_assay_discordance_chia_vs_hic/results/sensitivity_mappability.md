# Mappability sensitivity — AluSz OR (T4)

**Computed:** `2026-07-20T10:48:45.955134+00:00`  
**Primary TE:** `AluSz` (frozen)  
**MAPQ:** `N/A`  
**Umap track:** `k100.Umap.MultiTrackMappability.bw` (k100 multi-read)

## MAPQ status

Processed ENCODE bedpe ENCFF511QFN (7-col ChIA-PET clusters) and ENCFF693XIL (HiCCUPS bedpe) lack per-anchor MAPQ fields usable for MAPQ≥30 filtering. Umap mean ≥0.3 is the preregistered proxy for 'MAPQ≥30 spirit' (claim.md / controls.md).

## Estimand

Same as T3 primary: Fisher OR for AluSz overlap in fixed 1 kb midpoint windows of
merged ≥1 kb anchors, Pol II ChIA-PET (`ENCFF511QFN`) vs Hi-C (`ENCFF693XIL`), K562 /
GRCh38 — restricted to windows with mean Umap ≥ threshold.

## Results

| Filter | n Pol II | n Hi-C | AluSz+ Pol II / Hi-C | Fisher OR | Woolf 95% CI | OR < 1.1 |
|--------|----------|--------|----------------------|-----------|--------------|----------|
| Unfiltered (T3 baseline) | 572808 | 17183 | 31531 / 1036 | **0.9075** | 0.8514–0.9673 | True |
| Mean umap ≥ 0.3 (primary) | 572808 | 16879 | 31531 / 1028 | **0.8978** | 0.8421–0.9572 | True |
| Mean umap ≥ 0.5 (sensitivity) | 572793 | 16728 | 31531 / 1023 | **0.8939** | 0.8383–0.9532 | True |

**Retention:** umap≥0.3 keeps 100.0% Pol II / 98.2% Hi-C;
umap≥0.5 keeps 100.0% / 97.4%.

## Verdict

- Primary filter umap≥0.3 OR = **0.8978**
- Sensitivity umap≥0.5 OR = **0.8939**
- Strengthens FAIL: **True**

After umap≥0.3, AluSz OR remains <1.1 → strengthens FAIL_DESK_PRIMARY (MAPQ-spirit proxy). Full claim REJECT still needs replication arm.

## What this does NOT mean

1. NOT a causal TE → loop claim.
2. NOT proof that mappability "explains" the null (OR already <1.1 unfiltered).
3. NOT MAPQ≥30 on raw BAM (unavailable here) — umap proxy only.
4. NOT claim-level REJECT without the replication arm.

