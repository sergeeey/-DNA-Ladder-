# Controls — exp_te_derived_pels_gnocchi (C-H1 true)

**Status:** PREREGISTERED (2026-07-20) — matching frozen **before** Gnocchi attach  
**Parent claim:** `claim.md`

## No leakage

Matching covariates and the 1:1 matched null are locked **before** any Gnocchi Z is
attached to cCREs. Forbidden in the matching step: Z, oe, expected/observed counts, or any
transform of constraint windows.

## Matching covariates (pre-registered)

| Covariate | Rule |
|-----------|------|
| `chrom` | Exact match (autosomes + chrX; drop chrY/chrM) |
| `length_bin` | Quartiles of registry-pELS length (universe frozen before match) |
| `gc_bin` | Deciles of GC% over the cCRE interval (hg38.2bit) |
| `tss_dist_bin` | \(\log_{10}(d_{\mathrm{TSS}}+1)\) bins: [0,3), [3,4), [4,5), [5,∞) |

**Match ratio:** 1:1 without replacement within each covariate key.  
**RNG seed:** `20260720` (frozen).  
Undermatched TE indices (empty pool for key) are dropped and counted.

## Exposure / comparator

| Set | Rule |
|-----|------|
| TE-derived pELS | Registry pELS ∩ ≥1 bp TE-class rmsk |
| Non-TE pool | Registry pELS with **zero** TE-class overlap |
| Drop | (none beyond chrom filter) — partial TE family stratification is **not** primary |

## Endpoint / coverage

- Region-level length-weighted mean Z (SE Gnocchi script convention).
- Pair dropped if either side has no overlapping QC-passed Gnocchi window (report count).

## Sensitivity (pre-registered; non-primary)

1. Autosomes only  
2. Cliff's \|\δ\| ≥ 0.2 as alternate practical threshold (report only; does not override \|\Delta\| gates)  
3. Restrict TE exposure to SINE-only (exploratory)

## Checklist

- [x] claim.md written before results
- [x] matching covariates frozen
- [x] SUPPORT / kill thresholds frozen
- [ ] outcomes attached after match lock
