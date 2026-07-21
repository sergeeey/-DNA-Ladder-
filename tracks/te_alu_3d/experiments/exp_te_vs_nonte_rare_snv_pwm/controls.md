# Controls — exp_te_vs_nonte_rare_snv_pwm (C-E1)

**Status:** PREREGISTERED 2026-07-21 — T0 freeze  
**Parent:** `claim.md`

## Matching (planned)

| Covariate | Rule |
|-----------|------|
| chrom | Exact |
| umap_bin | Quartiles of mean k100 umap ±50 bp of SNV |
| Optional | GC of ±50 bp if fasta available |

Match **before** PWM Δ attach. Seed `20260721`.

## Exclusions (hard)

- HBB chr11:5200000–5300000
- Holdout HO_A/B/C while `unblind_authorized: false`
- C1 E/P coordinates as universe seeds

## Checklist

- [x] claim before analysis
- [x] T0 probe filed
- [ ] non-HBB rare-SNV fetch
- [ ] umap match lock
- [ ] primary Cliff's δ
