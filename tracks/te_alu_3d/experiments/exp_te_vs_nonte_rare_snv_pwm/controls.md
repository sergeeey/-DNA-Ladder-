# Controls — exp_te_vs_nonte_rare_snv_pwm (C-E1)

**Status:** COMPLETE 2026-07-21 — REJECT  
**Parent:** `claim.md`

## Matching (executed)

| Covariate | Rule |
|-----------|------|
| chrom | Exact (chr11 desk) |
| umap_bin | Quartiles of mean k100 umap ±50 bp of SNV |
| Optional | GC skipped (not required) |

Match **before** PWM Δ attach. Seed `20260721`.  
Result: 2961/2961 TE matched (`results/matching_lock.json`).

## Exclusions (hard)

- HBB chr11:5200000–5300000
- Holdout HO_A/B/C while `unblind_authorized: false`
- C1 E/P coordinates as universe seeds

## Checklist

- [x] claim before analysis
- [x] T0 probe filed
- [x] non-HBB rare-SNV fetch
- [x] umap match lock
- [x] primary Cliff's δ
