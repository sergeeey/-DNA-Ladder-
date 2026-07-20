# Controls — exp_l1hs_ctcf_loop_anchors (C-L1)

**Status:** PREREGISTERED 2026-07-20 — match before L1HS outcome  
**Parent:** `claim.md`

## Matching (pre-outcome)

| Covariate | Rule |
|-----------|------|
| chrom | Exact (chr1–22,X) |
| length_bin | Quartiles of CTCF peak length (case uses intersecting CTCF length; control = peak length) |
| umap_bin | Quartiles of mean k100 umap over the 1 kb analysis window |

**k=1**; seed `20260720`. Undermatched cases dropped + counted.

## L1HS 5′UTR proxy (frozen)

For each rmsk row with `repName==L1HS` and strand in `+/-`:
- `+`: `[genoStart, genoStart+2000)` clipped to element end
- `-`: `(genoEnd-2000, genoEnd]` clipped to element start

Full-element L1HS OR is sensitivity only (non-primary).

## Umap kill

Recompute OR restricting **both** case and control windows to mean umap ≥ 0.3.
If OR < 1.1 → REJECT.

## Checklist

- [x] claim before OR
- [ ] matching lock
- [ ] primary OR
- [ ] umap falsify
- [ ] HCT116 replication
