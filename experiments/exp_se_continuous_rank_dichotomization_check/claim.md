---
experiment: exp_se_continuous_rank_dichotomization_check
date: 2026-07-10
ladder_tier: Standard
question_type: Descriptive
status: REJECT (of MCID) with partial signal -- see decision.md
---

# Claim: Within super-enhancers, SE size (continuous) correlates with
# Gnocchi constraint / R-loop overlap / G4 overlap, even though SE-vs-typical
# (binary) membership did not

## Background

Follow-up to a convergent finding from three independent hypothesis-generation
passes (`cross-domain`, `narrow-discovery-engines`, `hypothesis-revival`) run
after 5 straight REJECTs on "does binary SE-vs-typical-enhancer membership
predict X" (BRD4/MED1, ClinVar VUS x2, Gnocchi, R-loop, G4).

`cross-domain` identified a formal structural match to the statistics
literature on **dichotomization of continuous variables** (MacCallum et al.
2002) -- artificially binning a continuous predictor at a threshold
systematically inflates standard errors and can suppress or reverse true
effects. `hypothesis-revival` found this critique already exists specifically
for super-enhancers: **[VERIFIED]** Pott & Lieb 2015, *Nature Genetics*
47(1):8-12, DOI 10.1038/ng.3167 -- argued the SE/typical distinction (ROSE's
inflection-point threshold on ranked H3K27ac signal) may not be a real
discrete class. **[VERIFIED]** Blobel/Higgs/Mitchell/Notani/Young 2021,
*Nature Reviews Genetics* 22:749-755, DOI 10.1038/s41576-021-00398-w, PMID
34480110 -- the debate remained open 6 years later, with Young (SE concept
co-originator) himself revisiting it.

## Honest scope limitation (stated before running)

A full test of "replace binary SE membership with a continuous score across
the ENTIRE enhancer population" would require per-peak H3K27ac signal
intensity, which is **not in our fetched data** (`h3k27ac_k562_grch38.json` /
`_hepg2_grch38.json` have only chrom/start/end, no signal column -- verified
by inspection). Re-fetching signal-value peak files is not a "toy test
measured in hours" -- out of scope for this pass.

**What IS testable cheaply with data already on disk:** within the
SE-constituent group only, does the SIZE of the enclosing super-enhancer
(continuous, already available in `k562_super_enhancers_grch38.json` /
`hepg2_super_enhancers_grch38.json` -- no new fetch) correlate with the same
three endpoints already computed this session (Gnocchi Z, R-loop overlap
fraction, G4 overlap fraction)? SE size is an imperfect but real proxy for
"how super" a super-enhancer is (ROSE-style stitching ranks partly track
region size), available for free.

## EstimandOps L0

**Question type:** Descriptive.

"Among constituent H3K27ac peaks located inside a super-enhancer, does the
size (bp span) of the enclosing super-enhancer correlate with Gnocchi
constraint / R-loop overlap / G4 overlap of that peak?"

## L1 Estimand

- **Population:** SE-constituent H3K27ac peaks already classified this
  session (K562: 5993, HepG2: 1889).
- **Predictor (continuous):** bp length of the enclosing super-enhancer
  interval.
- **Endpoints (reused, not recomputed from scratch):** per-peak Gnocchi
  weighted-mean Z (K562+HepG2), R-loop overlap fraction (K562 only -- no
  HepG2 R-loop data available), G4 overlap fraction (K562+HepG2).
- **Summary measure:** Spearman rank correlation (implemented from scratch,
  rank-transform + Pearson on ranks, consistent with this project's no-scipy
  convention and its existing average-rank tie-handling in `mann_whitney_u`),
  with a permutation test (10,000 shuffles) for significance -- same
  significance-testing philosophy as every prior experiment this session.
- **MCID:** |Spearman rho| >= 0.2 AND permutation p < 0.05 -- same threshold
  family as the group-difference tests, for comparability, though this is now
  a correlation not a group difference.
- **ICE:** None.

## What This Does NOT Mean (stated before results)

1. A positive correlation would NOT fully vindicate the "dichotomization
   explains everything" hypothesis -- it would only show a within-SE
   size-gradient effect exists, not that it accounts for all 5 prior REJECTs.
2. A null result here would NOT rule out dichotomization as an issue
   elsewhere -- SE size is an imperfect proxy for "how super" (true ROSE rank
   uses cumulative signal, which we don't have); a null could mean "size isn't
   the right continuous variable" rather than "no continuous effect exists."
3. Does NOT test the typical-enhancer population at all -- this is a
   within-SE-only gradient check, narrower than the full dichotomization
   hypothesis as originally framed.
4. Does NOT establish causality.

## Status

Design-stage. Reuses all data and loader functions already on disk/written
this session. Analysis not yet run.
