---
experiment: exp_heritability_vus_se_frequency
date: 2026-07-08
ladder_tier: Standard
question_type: Descriptive
status: REJECT -- Cliff's delta -0.013 (K562-SE) / -0.032 (HepG2-SE), neither significant nor meeting MCID; see decision.md
---

# Claim: ClinVar VUS inside super-enhancers show a different gnomAD population-frequency signature than VUS outside super-enhancers

## Background

Third DNA Ladder research direction (backlog item 8, "missing heritability / regulatory-variant
interpretation" -- `RESEARCH_DIRECTIONS.md`). Reuses two things this project already has
verified and working: the ClinVar/gnomAD fetch-and-compare pattern proven in ARCHCODE (a
sibling project, methodology reused, code not copied across repos), and the dbSUPER
super-enhancer call sets already fetched and GRCh38-lifted for K562/HepG2 in
`exp_llps_promoter_vs_se_chip_evidence` / `exp_llps_promoter_vs_se_hepg2_replication`.

## EstimandOps L0

**Question type:** Descriptive.
"Among ClinVar Variants of Uncertain Significance (VUS), genome-wide, do those located inside
a super-enhancer region (K562 and/or HepG2 dbSUPER calls, GRCh38) show a different gnomAD
population allele-frequency distribution than VUS located outside super-enhancer regions?"

**Motivating logic (missing-heritability angle):** if a subset of "uncertain significance"
variants are actually functional regulatory variants contributing to disease risk or trait
variance not captured by known pathogenic/GWAS variants (the "missing heritability" hypothesis
for regulatory variation), such variants would be expected to sit under stronger negative
selection than truly neutral variants -- and therefore be systematically RARER in gnomAD --
specifically when located inside a known functional regulatory hub (a super-enhancer) versus
elsewhere. This is a plausibility test for that hypothesis, not proof of it.

## Novelty check (mandatory, per falsification-ladder.md Step -3)

Ran via WebSearch before any data work, 2026-07-08.

**Not novel (established, cited literature):** using gnomAD population frequency as one input
to variant interpretation/reclassification is standard, widely published ACMG-adjacent
practice (e.g. Gudmundsson et al. 2022 Human Mutation, "Variant interpretation using population
databases: lessons from gnomAD" -- found via WebSearch). The general principle "rare = more
likely functional/pathogenic" is foundational, not something this project can discover.

**Reformulated, honest scope:** the specific, narrower comparison -- gnomAD frequency of VUS
STRATIFIED BY super-enhancer membership, genome-wide, as a systematic test rather than a
single-locus/single-variant reclassification exercise -- was not found in the literature
search conducted. This experiment tests that specific, narrow stratification, not the general
"population frequency matters for interpretation" principle (which is not in question).

## L1 Estimand

- **Population:** ClinVar entries genome-wide, GRCh38, `ClinicalSignificance` == "Uncertain
  significance" (strict, single-category, excludes conflicting-interpretation entries),
  SNVs only (matches this project's and ARCHCODE's established convention for
  gnomAD/VEP-compatible querying).
- **Exposure:** Membership in a super-enhancer region (K562 and HepG2 dbSUPER calls, GRCh38,
  already fetched -- `data/input/k562_super_enhancers_grch38.json`,
  `data/input/hepg2_super_enhancers_grch38.json`) vs. not.
- **Comparator:** VUS inside vs. outside super-enhancer regions.
- **Endpoint:** gnomAD population allele frequency (highest available population AF, or overall
  AF -- to be finalized before fetching).
- **Summary measure:** Mann-Whitney U + Cliff's delta on log-transformed allele frequency
  (matching this project's/ARCHCODE's established from-scratch stats convention, e.g.
  `ARCHCODE/null_results/20260707-synonymous-codon-optimality.md`), reported separately for
  K562-SE and HepG2-SE stratification (2 tests, BH-corrected).
- **MCID:** |Cliff's delta| >= 0.2 AND BH-corrected p < 0.05 -- same threshold convention as
  ARCHCODE's Hypothesis C, chosen specifically because that experiment demonstrated a p<1e-6,
  sub-MCID-effect-size result on a similarly-large ClinVar population, and this experiment
  risks the same statistical-vs-practical-significance trap given genome-wide VUS counts will
  likely be large.
- **ICE:** Variants absent from gnomAD (not observed in any sequenced population) are a
  substantive category, not missing data -- planned strategy: treat as AF=0 (true absence in
  sampled populations), reported separately from "present but low AF", not imputed or dropped.

## What This Does NOT Mean

1. A positive result (VUS-in-SE rarer than VUS-outside-SE) would NOT prove any individual VUS
   is pathogenic or functional -- only a population-level statistical tendency consistent with,
   not proof of, the missing-heritability regulatory-variant hypothesis.
2. Does NOT establish causality between super-enhancer membership and rarity -- confounds
   (gene density, local mutation rate, GC content, sequencing coverage bias in SE-dense
   regions) are not controlled for in this design and would need to be addressed before any
   causal claim.
3. A negative result does NOT mean missing heritability isn't explained by regulatory variants
   generally -- only that THIS specific, coarse stratification (any-SE-membership, genome-wide,
   K562/HepG2 calls only) doesn't detect a signal with this method.
4. Does NOT replace or improve on real ACMG variant classification -- this is a population-level
   descriptive pattern test, not a clinical reclassification tool.

## Status

**Data fetched (2026-07-08, `[VERIFIED-bash]`):** 2,254,079 unique strict VUS genome-wide
(GRCh38). In K562 SE: 25,726. In HepG2 SE: 9,537.

**Addendum (2026-07-08, after seeing population sizes, BEFORE any gnomAD AF lookup or test
statistic was computed):** 25,726 + 9,537 individual gnomAD API calls is impractical in this
session. Pre-registering here: in-K562-SE and in-HepG2-SE groups are each randomly subsampled
to 3,000 (fixed seed=42, `random.Random(42).sample(...)`) if they exceed that size, matching
the outside-SE comparator's existing 3,000-sample cap and the same subsampling discipline used
in ARCHCODE's Hypothesis C (`ARCHCODE/null_results/20260707-synonymous-codon-optimality.md`).
Documented before touching any AF/outcome data, not after.

Next step: gnomAD v4 AF lookup + Mann-Whitney/Cliff's delta stats. Not yet run.
