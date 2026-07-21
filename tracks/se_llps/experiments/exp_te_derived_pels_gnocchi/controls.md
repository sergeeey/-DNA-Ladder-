# Controls — exp_te_derived_pels_gnocchi (C-H1 true)

**Status:** PREREGISTERED (2026-07-20) + sensitivity executed (2026-07-21)  
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

## Sensitivity (executed 2026-07-21; non-primary)

1. Alternate matching: seed `20260721`; drop TSS; GC bins q5
2. Exclude ENCODE hg38 blacklist v2 overlaps
3. Chromosome holdout: leave-one-chrom-out |\Δ|; odd/even parity
4. TE class split: SINE / LINE / LTR vs same non-TE pool
5. Cliff's \|\δ\| ≥ 0.2 as alternate practical threshold (report only; does not override \|\Δ\| gates)
6. Second Gnocchi build — UNAVAILABLE (SKIP)

See `results/sensitivity_result.json` → desk label **SUPPORT_WITH_CAVEATS**.

## Checklist

- [x] claim.md written before results
- [x] matching covariates frozen
- [x] SUPPORT / kill thresholds frozen
- [x] outcomes attached after match lock
- [x] sensitivity battery filed
