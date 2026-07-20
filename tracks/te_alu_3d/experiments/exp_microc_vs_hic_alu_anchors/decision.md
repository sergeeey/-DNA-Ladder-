# Decision — exp_microc_vs_hic_alu_anchors (C-I1)

**Date:** 2026-07-20  
**Verdict:** **BLOCKED_DATA**  
**Stage:** T0 only — OR not computed

## Gate

No released **processed Micro-C loop bedpe** (GRCh38) usable for Alu-anchor OR vs Hi-C.

| Probe | Result |
|-------|--------|
| ENCODE `assay_title=Micro-C` / `micro-C` | **404** (assay absent) |
| ENCODE `searchTerm=Micro-C` | False positives = **microRNA-seq** (e.g. ENCSR291HNO) |
| ENCODE bedpe + “Micro-C” | Annotation “thresholded links” — **not** Micro-C loops |
| 4DN Micro-C sets (H1/HFF/HeLa/…) e.g. `4DNESWST3UBH` | pairs / hic / mcool / boundaries — **no bedpe** |

Full JSON: `data/t0_accession_probe.json`.

## What this does NOT mean

1. NOT a scientific REJECT of Micro-C vs Hi-C Alu recovery (data never entered).
2. NOT license to call loops from pairs/mcool on the desk without a new claim freeze.
3. NOT wet / holdout / C1 license.
4. Does NOT reopen C-A1 / C-H1 Gnocchi SUPPORT / SE nulls.

## Next fruit

Recommend **C-L1** (cross-cell transfer) — Micro-C path exhausted at processed-bedpe gate (same class as C-K1 PLAC BLOCKED_DATA).
