---
experiment: exp_plac_vs_hic_alu_anchors
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: BLOCKED_DATA
candidate_id: C-K1
candidate_alias: C-K1-plac-h3k4me3-alu-anchors
source: standing_order_post_C-B1_FAIL + Deep Research next-fruit slot (PLAC estimand)
decision_gate: BLOCKED_DATA
---

# Claim: H3K4me3 PLAC-seq AluSz-anchor enrichment vs matched Hi-C anchors

## Status

**BLOCKED_DATA** — Standard tier; desk **CLOSED** at T0.  
No released **processed PLAC-seq loop bedpe** for GM12878 or K562 (ENCODE assay term
absent; 4DN K562/GM12878 PLAC releases are pairs/hic/mcool only).  
OR not computed. See `decision.md`. Next fruit: **C-A2**.

## EstimandOps L0

**Question type:** Descriptive.

Genome-wide in ≥1 preferred cell type (prefer **GM12878** if K562 PLAC bedpe missing;
else K562), among processed loop call sets from **H3K4me3 PLAC-seq** and matched **Hi-C**,
is AluSz membership enriched at PLAC anchors relative to Hi-C anchors at **OR ≥ 1.5**?

Explicitly **not causal**. Explicitly **not** C-A1 (Pol II ChIA-PET vs Hi-C discordance).
Explicitly **not** closed SE/LLPS claims.

## Frozen claim (pre-results)

> H3K4me3 PLAC-seq enriches Alu-anchor loops with **OR ≥ 1.5** vs matched Hi-C anchors in
> ≥1 cell type (prefer GM12878 if K562 PLAC bedpe missing).

**Primary TE (pre-specified):** **AluSz** only (exact RepeatMasker `repName`; consistency
with C-A1). All-Alu collapse is exploratory only — not headline.

**Falsification (pre-registered):** after umap ≥ 0.3 (MAPQ proxy), OR **< 1.1** → claim
**REJECT**.

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | Loop anchors from frozen processed bedpe (GRCh38) |
| Exposure | AluSz overlap on fixed midpoint windows (≥1 kb pad; same as C-A1) |
| Outcome / contrast | PLAC-seq anchors vs matched Hi-C anchors (same cell type) |
| Summary | Fisher OR + Woolf 95% CI |
| MCID (SUPPORT) | OR ≥ 1.5 in ≥1 cell type |
| Falsify | OR < 1.1 after umap ≥ 0.3 |

## Datasets — T0 probe (no freeze)

| Role | Portal probe result | Status |
|------|---------------------|--------|
| H3K4me3 PLAC-seq GM12878/K562 processed **bedpe** | ENCODE: no `PLAC-seq` assay; free-text hits = placenta. 4DN: K562 `4DNESWX1J3QU` + GM12878 PLAC sets = pairs/hic/mcool **only** | **MISSING** |
| Near-miss: ENCODE H3K4me3 ChIA-PET K562 `ENCSR000FDF` | Archived **hg19** loop TSV — not GRCh38 bedpe, not PLAC-seq | **REJECTED** (wrong assay/build) |
| Near-miss: 4DN multi-assay union bedpe (HFFc6/H1) | Mentions PLAC among platforms; not PLAC-primary; wrong cell type | **REJECTED** |
| Matched Hi-C loops | Would reuse C-A1 freezes (`ENCFF781ASD` GM12878 / `ENCFF693XIL` K562) **if** PLAC bedpe existed | N/A |
| CTCF gate | Would reuse C-A1 CTCF freezes | N/A |
| TE / umap | UCSC rmsk hg38; Hoffman Umap k100 | N/A (blocked) |

Full probe JSON: `data/t0_accession_probe.json`.

## Controls

See `controls.md` (CTCF positive gate ≥ 2.0; AluJo contrast; umap ≥ 0.3 kill-test).
**Not run** — blocked before download.

## Allowed claim language

- “PLAC vs Hi-C AluSz OR = … (descriptive, processed call sets).”
- “BLOCKED_DATA: no processed PLAC loop bedpe on ENCODE/4DN for preferred cells.”

## Forbidden claim language

- Causal PLAC/TE → loop mechanism
- Substituting H3K4me3 ChIA-PET hg19 TSV or multi-assay union bedpe as primary PLAC
- Reopening C-A1 / SE / HBB / wet / holdout / C1 E/P

## Novelty note

- Distinct from **C-A1** (Pol II ChIA-PET vs Hi-C **discordance** stratification).
- Distinct from Deep Research registry title that originally used C-K1 for CTCF ChIA-PET
  fallback — that estimand is **parked** as `C-K1-CTCF-chia-fallback` / queued as **C-A2**.
- Does not overlap closed SE enrichment nulls or C-B1 topology REJECT.

## What this does NOT mean

1. NOT that H3K4me3–promoter contacts lack Alu biology — only that cheap processed bedpe
   for the frozen PLAC estimand is unavailable.
2. NOT authorization to call loops from pairs/hic on the desk without a new claim freeze.
3. NOT wet / holdout / C1 license.
4. NOT a scientific REJECT of the OR≥1.5 claim (data never entered).

## Next step

Desk **CLOSED** `BLOCKED_DATA`. Recommend **C-A2** (CTCF ChIA-PET vs Hi-C AluSz
discordance — original Deep Research C-K1 estimand). Do not auto-start without queue.
