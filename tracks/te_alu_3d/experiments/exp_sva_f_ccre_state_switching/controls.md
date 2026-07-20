# Controls — exp_sva_f_ccre_state_switching (C-A2 true)

**Status:** PREREGISTERED (2026-07-20) — matching + switcher frozen **before** outcomes  
**Parent claim:** `claim.md`

## CRITICAL — no leakage

Matching covariates are computed and the 1:k matched null is locked **before** any
switching-panel active/inactive vector or switcher label is attached to cCREs.

Forbidden in the matching step:

- switcher label
- \(A\) / fraction active on the switching panel
- any transform of switching-panel classifications

Allowed for matching only: chrom, length, GC, distance-to-TSS, and **held-out** baseline
biosample activity (SK-N-SH), which is excluded from \(N\).

## Matching covariates (pre-registered)

| Covariate | Rule |
|-----------|------|
| `chrom` | Exact match (autosomes + chrX; drop chrY/chrM) |
| `length_bin` | Quartiles of registry-dELS length (universe frozen before match) |
| `gc_bin` | Deciles of GC% over the cCRE interval (hg38.2bit / FASTA) |
| `tss_dist_bin` | \(\log_{10}(d_{\mathrm{TSS}}+1)\) bins: [0,3), [3,4), [4,5), [5,∞) with \(d\) in bp to nearest protein-coding TSS |
| `baseline_signal` | Binary active (dELS*) in held-out **SK-N-SH** `ENCFF948UCK` — exact 0/1 match |

**Match ratio:** 1:k with **k=5** (without replacement within each SVA_F index; if pool
`<k`, take all and log `undermatched`).  
**RNG seed:** `20260720` (frozen).

## Exposure / comparator

| Set | Rule |
|-----|------|
| SVA_F dELS | Registry dELS ∩ ≥1 bp `repName=SVA_F` |
| Non-TE pool | Registry dELS with **zero** overlap to rmsk `repClass ∈ {SINE,LINE,LTR,DNA,Retroposon}` |
| Drop | dELS overlapping other TEs but not SVA_F (neither exposure nor pool) |

## Active / inactive (SCREEN column rule)

From each frozen cell-type bed (11 columns):

- col4 = cCRE id (`EH38E…`)
- col10 = classification
- col11 = completeness

**Active** iff col11 == `All-data/Full-classification` AND (col10 == `dELS` OR col10
startswith `dELS,`).  
Else **inactive** (including Low-DNase, pELS, PLS, CTCF-only, Missing-data rows — Missing
rows must not appear in frozen Full-classification files; if they do, that biosample is
invalid for the panel).

## Switcher (primary)

\(N\) = |switching panel| (all frozen Full-classification biosamples **except** SK-N-SH).  
Switcher = \((A \ge 1) \land (N-A \ge 3)\).

## Falsification panels

Ordered switching panel (alphabetical by biosample name, frozen in
`ACCESSION_FREEZE_v1.md`):

1. **Odd panel:** indices 0,2,4,…  
2. **Even panel:** indices 1,3,5,…  

Recompute switcher within each sub-panel using the **same** rule with that sub-panel’s
\(N_{\mathrm{sub}}\) (require \(N_{\mathrm{sub}} \ge 4\) else skip and log).  
Kill if OR < 1.1 on **both** odd and even (i.e. ≥2 independent panels).

## Sensitivity list (pre-registered; non-primary)

1. k=3 and k=10 match ratios  
2. Autosomes only  
3. Stricter active = `dELS` exact only (no `dELS,CTCF-bound`)  
4. Drop undermatched SVA_F indices  

## Checklist

| Item | Status |
|------|--------|
| claim.md L0 Descriptive | DONE |
| Switcher definition frozen | DONE |
| Matching covariates frozen (incl. held-out baseline) | DONE |
| ACCESSION_FREEZE panel (≥8 Full-class beds) | PENDING T0 |
| Match before outcomes | PENDING T2 |
| Primary Fisher OR | PENDING T3 |
| Odd/even kill panels | PENDING T3 |
| null_results if REJECT/INCONCLUSIVE | PENDING |
