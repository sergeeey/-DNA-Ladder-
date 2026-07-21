# Controls — exp_te_loop_caller_concordance (C-F1)

**Status:** PREREGISTERED (2026-07-21) — blocked at Mustache accession gate  
**Parent claim:** `claim.md`

## Planned (not executed — BLOCKED_DATA)

| Control | Rule |
|---------|------|
| Same-library preference | Mustache + HiCCUPS on `ENCSR545YBD` if both exist |
| TE strata | AluSz and SVA (family-level); report n minima before Jaccard |
| Non-TE comparator | Anchors with zero TE-class overlap; length/GC/umap match if available |
| Optional CTCF sanity | CTCF-anchor Jaccard should stay high (report-only) |

## Forbidden substitutions

- DELTA / localizer / intact-Hi-C callers **must not** be labeled Mustache
- Synthetic / mock loops forbidden

## Checklist

- [x] claim.md written before outcome analysis
- [x] T0 Mustache probe filed
- [x] BLOCKED_DATA decision (no ΔJaccard)
- [ ] ΔJaccard — N/A until Mustache bedpe exists
