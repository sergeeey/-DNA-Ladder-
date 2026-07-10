---
experiment: exp_gnocchi_constraint_se_vs_typical_enhancer
date: 2026-07-10
ladder_tier: Standard
question_type: Descriptive
status: REJECT -- analysis complete, see decision.md
---

# Claim: Constituent enhancers inside super-enhancers show a different germline
# mutational-constraint (Gnocchi Z-score) signature than length-matched typical
# (non-SE) H3K27ac enhancers, in the same cell line

## Background

Direct methodological upgrade of `exp_heritability_vus_se_frequency` (REJECT,
2026-07-08) and its refinement `exp_heritability_vus_se_vs_typical_enhancer`
(still running). Both used ClinVar VUS allele-frequency comparison, which
carries ClinVar ascertainment/gene-panel/submission bias (verified via WebSearch
earlier this session -- a real, documented concern, not a hypothetical one).

`boyko-specialist` (2nd targeted run, 2026-07-10) located Gnocchi -- Chen,
Francioli, Karczewski et al. 2023, *Nature* 625:92-100, DOI
10.1038/s41586-023-06045-0 -- a genome-wide, GRCh38-native, population-WGS-only
(gnomAD v3.1.2, 76,156 genomes) mutational constraint map, entirely independent
of ClinVar. This removes the ascertainment-bias confound at the data-source
level, not just the comparator level.

An external methodological critique (pasted by user, 2026-07-10) correctly
flagged three problems with the naive "intersect 1kb windows + Mann-Whitney"
design: (1) unresolved novelty vs. the original Gnocchi paper's own enhancer
analyses, (2) K562/HepG2 are cancer cell lines -- Gnocchi measures **germline**
constraint, so a positive result must not be over-interpreted as "cell-type-
specific selection", (3) pooling all 1kb windows that overlap a region into one
Mann-Whitney test pseudoreplicates (windows within one region are not
independent draws). All three are addressed below.

## Gate 0 -- Novelty check (per falsification-ladder.md Step -3)

Checked: GitHub `atgu/gnomad_nc_constraint` README (WebFetch) and WebSearch for
"Gnocchi super-enhancer typical enhancer comparison". No evidence found of the
original paper computing SE-vs-typical-enhancer within K562/HepG2 specifically.
**[UNKNOWN] not [CONFIRMED-NOVEL]** -- the paper's full supplementary PDF is
paywalled and not indexed by search; this is an honest limitation, not a
guarantee no one has done this exact comparison. Proceeding is still justified:
even if a similar comparison exists elsewhere, this is an independent
replication on our own SE/H3K27ac calls, not a copy of anyone's pipeline.

## EstimandOps L0

**Question type:** Descriptive. (Explicitly NOT causal -- see "What This Does
NOT Mean" below. Also explicitly NOT a claim about K562/HepG2-*specific*
selection -- Gnocchi is a germline, population-level metric; see limitation 2.)

"Among H3K27ac-marked active-enhancer regions in a given cell line (K562 or
HepG2), do those located inside a super-enhancer show a different distribution
of genome-wide germline mutational constraint (Gnocchi Z-score) than
length-matched H3K27ac regions outside any super-enhancer?"

## L1 Estimand

- **Population:** All ENCODE H3K27ac ChIP-seq peaks already fetched for K562
  (52,334 peaks) and HepG2 (`data/input/h3k27ac_{k562,hepg2}_grch38.json`),
  GRCh38, no new fetch needed.
- **Exposure:** Peak classified as "SE-constituent" if it falls inside a
  merged super-enhancer region (`data/input/{k562,hepg2}_super_enhancers_grch38.json`,
  738 K562 SEs from dbSUPER via liftover), else "typical enhancer".
- **Comparator:** SE-constituent H3K27ac peaks vs. **length-matched** typical
  H3K27ac peaks (nearest-neighbor greedy matching on log10(peak length),
  without replacement) -- NOT unmatched, correcting the exact class of
  confound already learned from the LLPS matched-control follow-up.
  Signal-intensity matching (H3K27ac ChIP signal strength) is NOT performed --
  our fetched peak files have no signal/score field (chrom/start/end only,
  verified by inspection). This is a real, acknowledged gap, not silently
  glossed over.
- **Endpoint:** Region-level Gnocchi Z-score, computed as the **length-weighted
  mean** Z across all 1kb windows overlapping the peak (weight = bp of overlap)
  -- one summary value per enhancer region, NOT one value per 1kb window. This
  directly addresses the pseudoreplication concern: the unit of analysis is the
  enhancer region, not the window.
- **Summary measure:** Mann-Whitney U + Cliff's delta on the region-level
  weighted-mean Z, same convention as prior experiments. A chromosome-block
  permutation test (shuffle SE/typical labels within matched pairs, 10,000
  permutations) is run as the primary significance check, since it does not
  assume independence across all pairs the way the analytic Mann-Whitney
  p-value does -- Mann-Whitney p is reported as a secondary/reference value.
- **MCID:** |Cliff's delta| >= 0.2 AND permutation p < 0.05 -- same threshold
  convention as prior experiments in this project, for comparability.
- **ICE:** None -- Gnocchi Z-score has no missingness analogous to AF=0; a
  window failing Gnocchi's own QC is simply absent from the file (not
  imputed) and any peak whose overlapping windows are ALL QC-failed is
  excluded from that cell line's analysis (reported count, not silently
  dropped).

## Limitations (stated before results, per Doubt-Driven Development)

1. **Germline vs. cell-type-specific selection.** Gnocchi is built from
   healthy-donor germline WGS (gnomAD). K562 (CML blast crisis) and HepG2
   (hepatoblastoma) are cancer-derived lines. A positive result means "regions
   the K562/HepG2 SE-caller marks as super-enhancers happen to sit in
   more/less germline-constrained DNA" -- it does NOT mean "these cell lines'
   super-enhancers are under active cell-type-specific selection". This
   distinction is stated here BEFORE running the analysis, not added after a
   positive result to soften it.
2. **No signal-intensity matching** (see Comparator above) -- length-matched
   only. If a positive result appears, a natural next check (not run yet) is
   whether it survives restricting to the top-quartile-by-length typical
   enhancers, which are more comparable in "how much real estate" to SE
   constituents.
3. **Gene density / promoter-proximity confound not controlled.** Prior
   experiments in this project (LLPS matched-control) flagged this same gap
   and left it unresolved; still unresolved here.
4. Does NOT prove causality in either direction (constraint does not "cause"
   SE formation, nor vice versa) -- descriptive association only.
5. Does NOT validate or contradict the parallel ClinVar-based heritability
   experiments -- different endpoint (germline constraint vs. clinical VUS
   frequency), independent test of a related but distinct question.

## Data on disk (verified, no re-fetch needed)

- `data/input/gnocchi_constraint_z_genome_1kb_qc.txt.gz` -- 1,984,900 QC-passed
  1kb windows, GRCh38, downloaded from
  `gs://gnomad-nc-constraint-v31-paper/download_files/` (public bucket,
  verified via GCS JSON API listing), row count cross-checked against the
  paper's own README (1,984,900 -- exact match).
- `data/input/h3k27ac_k562_grch38.json` (52,334 peaks), `h3k27ac_hepg2_grch38.json`
- `data/input/k562_super_enhancers_grch38.json` (738 SEs), `hepg2_super_enhancers_grch38.json`

## Status

Design-stage, Gate 0 complete, data downloaded and row-count-verified. Analysis
script not yet written.
