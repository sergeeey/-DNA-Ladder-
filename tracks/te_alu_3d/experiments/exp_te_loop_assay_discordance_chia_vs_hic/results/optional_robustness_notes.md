# Optional cheap robustness notes (C-A1)

**Date:** 2026-07-20  
**Status:** documented; no new primary estimands

## 1. PLAC-seq / H3K4me3 vs Hi-C Alu anchor — SKIPPED

**Reason:** Cheap ENCODE portal probes (2026-07-20) did not yield a ready K562
H3K4me3 PLAC-seq (or equivalent HiChIP) **processed bedpe loop** call set with a clear
preferred_default path matching the frozen Pol II ChIA-PET vs Hi-C estimand.

- `assay_term_name=PLAC-seq` / HiChIP+K562 structured searches returned 404 or empty.
- Free-text `PLAC` bedpe hits resolved to **placenta** intact Hi-C (name collision), not PLAC-seq.
- Adding a new assay class would invent a secondary primary estimand outside the frozen claim.

→ **SKIP** with written reason; do not fabricate PLAC OR.

## 2. Chromosome holdout / block consistency (from existing T3 bootstrap)

Already present in `results/primary_result_OR_CI.json` → `primary_result.block_bootstrap`:

| Metric | Value |
|--------|-------|
| Method | chromosome block bootstrap (resample chroms w/ replacement) |
| n_boot | 500 |
| OR mean | ≈ 0.911 |
| 95% CI | **0.866 – 0.958** |

Point estimate OR 0.908 sits inside the chrom-block CI; CI entirely below 1.0 and below
fail threshold 1.1 → K562 depletion / null-enrichment is **not** a single-chromosome artifact
under this resampling scheme.

No new chromosome-holdout analysis run; sealed variant holdout remains **untouched**.

## 3. Caller-swap (see T6)

DELTA (`ENCFF657QKE`) OR ≈ 0.913 vs HiCCUPS 0.908 — FAIL robust. Mustache unavailable.
Intact localizer (`ENCFF256ZMD`) OR ≈ 1.107 is assay+caller sensitivity only.
