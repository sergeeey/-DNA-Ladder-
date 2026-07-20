# Notes — exp_plac_vs_hic_alu_anchors (C-K1)

**Date:** 2026-07-20  
**Source:** Standing order after C-A1 `INCONCLUSIVE_CROSS_CELL` + C-B1 `FAIL_KILL` /
REJECT; PLAC vs Hi-C Alu-anchor fruit (C-A1 optional robustness had **SKIPPED** PLAC for
lack of cheap K562 bedpe — this desk re-probes ENCODE **and** 4DN formally).

## Why this estimand

| Axis | This desk (C-K1 PLAC) | C-A1 (closed) |
|------|------------------------|---------------|
| Assay A | H3K4me3 **PLAC-seq** | Pol II ChIA-PET |
| Contrast | PLAC vs Hi-C AluSz enrichment | Discordant-anchor TE OR |
| MCID | OR ≥ **1.5** | OR ≥ 1.3 |
| Primary TE | AluSz | AluSz |
| Kill-test | umap ≥ 0.3 → OR < 1.1 | MAPQ/umap + replication |

## ID note (registry)

Deep Research originally scored **C-K1** as CTCF ChIA-PET TE-discordance fallback
(final 6.93). Standing order fills the C-K1 desk slot with this **PLAC** estimand.
Original CTCF fallback is **parked** and recommended next as **C-A2**.

## T0 findings (summary)

1. ENCODE `assay_title`/`assay_term_name` = `PLAC-seq` → **404** (no such assay facet).
2. Free-text `PLAC` → placenta ChIP/RNA collision, not PLAC-seq.
3. ENCODE H3K4me3 ChIA-PET K562 `ENCSR000FDF`: archived **hg19** loop TSV only —
   rejected as PLAC/GRCh38 bedpe substitute.
4. 4DN K562 PLAC `4DNESWX1J3QU`: pairs + hic + mcool — **no** processed loop bedpe.
5. 4DN GM12878 PLAC sets: same (pairs/hic/mcool only).
6. 4DN bedpe mentioning PLAC: multi-platform **union** loops for HFFc6 / H1-hESC —
   not PLAC-primary, wrong cell for claim preference.
7. GEO hits (e.g. GSE161873) are not a drop-in GRCh38 processed bedpe freeze for this desk.

→ **BLOCKED_DATA** per claim stop condition. Do not invent OR from matrices.

## Reuse from C-A1

Scripts/patterns to copy if a future processed PLAC bedpe appears:
`t2_positive_control_ctcf_gate.py`, `t3_primary_alusz_or.py`, `t4_mappability_sensitivity.py`
(anchor merge, AluSz Fisher OR, umap gate).

## Explicit non-actions

- Do not call loops from pairs/.hic on this desk without a new claim freeze  
- Do not substitute ChIA-PET H3K4me3 hg19 TSV as “PLAC”  
- Do not unseal holdout / wet / C1 E/P  
- Do not reopen C-A1 or SE nulls  
