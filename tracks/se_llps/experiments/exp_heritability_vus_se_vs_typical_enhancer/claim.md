---
experiment: exp_heritability_vus_se_vs_typical_enhancer
date: 2026-07-10
ladder_tier: Standard
question_type: Descriptive
status: DESIGN -- data available, not yet run
---

# Claim: ClinVar VUS inside super-enhancers show a different gnomAD frequency signature than VUS inside matched typical (H3K27ac) enhancers

## Background

Direct methodological refinement of `experiments/exp_heritability_vus_se_frequency`
(REJECT, 2026-07-08: VUS-in-SE vs VUS-anywhere-else showed no effect, Cliff's delta
-0.013/-0.032). That experiment's own "Recommendation" section flagged the comparator as
coarse. Separately, today's LLPS matched-control follow-up
(`experiments/exp_llps_promoter_vs_se_chip_evidence/decision.md`) demonstrated the exact same
class of problem for a different question: "vs whole genome" is too weak a comparator because
it mixes in inactive chromatin, inflating apparent effects that aren't actually SE-specific.
Applying that same lesson here.

## EstimandOps L0

**Question type:** Descriptive.
"Among ClinVar VUS located in H3K27ac-marked active chromatin (K562/HepG2), do those
specifically inside a super-enhancer show a different gnomAD population allele-frequency
distribution than those in matched typical (non-super) enhancers?"

## Novelty check (per falsification-ladder.md Step -3)

This is a direct refinement of a hypothesis already novelty-checked in
`exp_heritability_vus_se_frequency/claim.md` (general population-frequency-for-interpretation
principle established; this specific SE-vs-typical-enhancer-matched stratification not found
in a literature search). Re-checking Step -3 is not required for a same-day methodological
refinement of an already-cleared question -- flagged here for traceability, not re-run.

## L1 Estimand

- **Population:** Same 2,254,079 genome-wide ClinVar VUS already fetched
  (`data/input/clinvar_vus_grch38_se_classified.json`) -- reused, not re-fetched.
- **Exposure:** VUS position reclassified into 3 categories per cell line (K562, HepG2):
  super-enhancer (SE), typical enhancer (H3K27ac-marked, not SE), or neither -- using the
  H3K27ac data already fetched for the LLPS matched-control follow-up
  (`data/input/h3k27ac_k562_grch38.json`, `data/input/h3k27ac_hepg2_grch38.json`).
- **Comparator:** VUS-in-SE vs VUS-in-typical-enhancer (the matched comparison) -- NOT vs
  "neither" this time, correcting the original experiment's weak comparator.
- **Endpoint:** gnomAD v4 population allele frequency (same lookup method, cache reused where
  variants overlap with the already-annotated set from the original experiment).
- **Summary measure:** Mann-Whitney U + Cliff's delta on log10(AF), same convention as the
  original experiment and as ARCHCODE's Hypothesis C.
- **MCID:** |Cliff's delta| >= 0.2 AND BH-corrected p < 0.05 -- same threshold as the original
  experiment, for direct comparability.
- **ICE:** Same AF=0 -> floor(-7) strategy as the original experiment.

## Pre-registered subsampling (before touching any new AF data)

VUS-in-SE and VUS-in-typical-enhancer groups will each be capped at 3,000 (fixed seed=42),
same cap and seed as the original experiment, for gnomAD API tractability. Any variant already
in the gnomAD cache from the original experiment is reused without a new API call.

## What This Does NOT Mean

1. A positive result would NOT prove SE-located VUS are individually pathogenic -- population-
   level tendency only, same caveat as the original experiment.
2. Does NOT retroactively validate or invalidate the original REJECT verdict -- that was a
   different (weaker) comparator; this is an independent test of a different, more specific
   claim, matching the exact "different comparator, different claim" logic already applied to
   the LLPS matched-control follow-up.
3. Does NOT control for the same confounds the LLPS matched-control still didn't resolve (gene
   density, local mutation rate, sequencing coverage differences between SE and typical
   enhancer regions).

## Status

Design-stage. All required data already on disk (no new fetching needed except gnomAD AF
lookups for the newly-defined typical-enhancer VUS subsample). Not yet run.
