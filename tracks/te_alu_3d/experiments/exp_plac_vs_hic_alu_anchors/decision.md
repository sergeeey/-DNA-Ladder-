# Decision — exp_plac_vs_hic_alu_anchors (C-K1)

**Date:** 2026-07-20  
**Status:** `BLOCKED_DATA` (desk **CLOSED** at T0)  
**OR:** *not computed*  
**null_results:** not filed (data unavailable ≠ REJECT/INCONCLUSIVE falsification)

## Verdict

**Terminal desk status: `BLOCKED_DATA`.**

Frozen claim (H3K4me3 PLAC-seq AluSz OR ≥ 1.5 vs matched Hi-C; falsify OR < 1.1 after
umap ≥ 0.3) **cannot be tested**: no released **processed PLAC-seq loop bedpe** (GRCh38)
for GM12878 or K562 on ENCODE or 4DN.

| Probe arm | Result |
|-----------|--------|
| ENCODE assay `PLAC-seq` / `HiChIP` | **404** (facet absent) |
| ENCODE free-text `PLAC-seq` | Placenta name collision — not PLAC-seq |
| ENCODE H3K4me3 ChIA-PET K562 `ENCSR000FDF` | Archived **hg19** loop TSV only — **rejected** (not PLAC; not GRCh38 bedpe) |
| 4DN K562 PLAC `4DNESWX1J3QU` | pairs / hic / mcool — **no bedpe loops** |
| 4DN GM12878 PLAC sets | pairs / hic / mcool — **no bedpe loops** |
| 4DN bedpe mentioning PLAC | Multi-assay **union** HFFc6 / H1-hESC — **rejected** as PLAC primary |

Evidence: `data/t0_accession_probe.json` (metadata-only probe).

## What WAS tested

1. Descriptive L0 prereg (`claim.md` / `controls.md` / `notes.md`).
2. T0 portal probe ENCODE + 4DN for processed PLAC loop bedpe.
3. Explicit rejection of near-miss substitutes (ChIA-PET hg19; multi-assay union).

## What was NOT tested

- CTCF gate, AluSz OR, umap sensitivity (blocked before download).
- Calling loops from pairs/.hic (forbidden without new claim freeze).

## Forbidden overclaim language

- Do **not** treat BLOCKED_DATA as scientific REJECT of OR ≥ 1.5.
- Do **not** invent OR from contact matrices on this desk.
- Do **not** reopen C-A1 / SE nulls / wet / holdout / C1.

## Gate checklist

| Gate | Status |
|------|--------|
| L0 Descriptive prereg | DONE |
| T0 PLAC GRCh38 bedpe | **FAIL → BLOCKED_DATA** |
| CTCF / AluSz / umap | N/A |
| Holdout / wet / C1 | SEALED / FORBIDDEN |

## What this does NOT mean

1. Not proof that PLAC Alu enrichment is absent.  
2. Not license to substitute ChIA-PET or union bedpe as “PLAC”.  
3. Not wet / holdout / C1 authorization.  
4. Not reopening C-A1 INCONCLUSIVE or C-B1 REJECT.

## Next fruit

Recommend **C-A2** — CTCF ChIA-PET vs Hi-C AluSz discordance (Deep Research original
C-K1 estimand; this desk used C-K1 for the PLAC slot). Do not auto-start without queue.
See `NEXT_FRUIT_NOTE.md`.
