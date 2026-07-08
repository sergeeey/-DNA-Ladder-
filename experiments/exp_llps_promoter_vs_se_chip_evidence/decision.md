---
experiment: exp_llps_promoter_vs_se_chip_evidence
date: 2026-07-08
verdict: SE-FAVORING (opposite of the reformulated question's promoter-centric direction) — robust to sensitivity check, does not contradict the imaging-based literature (different methodology)
---

# Decision — Promoter vs. Super-Enhancer ChIP-seq Occupancy (BRD4/MED1, K562)

## Result

Primary test (2kb promoter window, pre-registered):

| Factor | n peaks | promoter-only | SE-only | density_promoter/kb | density_SE/kb | ratio | Classification |
|---|---|---|---|---|---|---|---|
| BRD4 | 4489 | 1953 | 933 | 0.0277 | 0.0670 | **0.414** | SE-favoring |
| MED1 | 325 | 74 | 28 | 0.0011 | 0.0020 | **0.523** | SE-favoring |
| POLR2A (baseline) | 25548 | 11900 | 2265 | 0.1689 | 0.1626 | 1.039 | No clear preference |

Pre-registered sensitivity check (5kb promoter window):

| Factor | ratio (2kb) | ratio (5kb) | Direction stable? |
|---|---|---|---|
| BRD4 | 0.414 | 0.177 | Yes -- same direction, stronger |
| MED1 | 0.523 | 0.287 | Yes -- same direction, stronger |
| POLR2A (baseline) | 1.039 | 0.501 | Shifts to SE-favoring at wider window -- expected for a broad-binding baseline, not treated as a primary result |

## Interpretation

The reformulated question (claim.md) asked whether static ChIP-seq co-occupancy of
condensate-associated coactivators independently supports a promoter-centric model (the
direction claimed by Bogdanović 2026 / Pandey 2026's live-cell imaging). **It does not — the
opposite pattern is observed, robustly.** Both BRD4 and MED1 show peak density 2-6x higher in
super-enhancer-only regions than in promoter-only regions, in K562, and this holds (gets
stronger, not weaker) under a 2.5x wider promoter-window sensitivity check.

This is a genuine, well-powered finding in the direction of the CLASSIC coactivator-condensate
model (Sabari et al. 2018, Boija et al. 2018 -- both in `Research Library/sources/llps-transcription/`)
rather than the newer 2026 promoter-centric imaging papers. It is NOT a failure to find
signal -- it is a positive result pointing the other way from what the reformulated hypothesis
anticipated.

## What this does NOT mean

1. Does NOT falsify Bogdanović 2026 / Pandey 2026 -- those are live-cell, single-molecule,
   dynamic measurements; this is population-averaged, static ChIP-seq. A real biological
   process can be genuinely promoter-centric in dynamic/live-cell terms while population-level
   ChIP-seq signal still concentrates more densely at super-enhancers -- these are not
   contradictory claims about the same measurement, they are different measurements
   (pre-registered as a possible outcome in claim.md's "What This Does NOT Mean" #3).
2. Does NOT establish LLPS/phase-separation as the mechanism -- ChIP-seq co-occupancy is
   consistent with LLPS, conventional high-affinity recruitment, or chromatin co-condensation
   alike (see `Research Library/evidence_matrices/llps-pol2-condensates.md`, "LLPS vs non-LLPS"
   table) -- this experiment cannot and does not distinguish between them.
3. Does NOT mean the promoter-only region class is "unimportant" -- BRD4/MED1 do occupy
   promoters at non-trivial density (0.0277/0.0011 peaks/kb respectively); the finding is about
   RELATIVE density between the two region classes, not absence at promoters.
4. Only tests K562, one cell line, one super-enhancer call set (dbSUPER), one promoter-window
   definition family (2kb/5kb). Generalization to other cell types or SE-calling methods is
   untested.

## Caveats / limitations

- **Go/No-Go criterion gap:** claim.md pre-registered a per-factor MCID classification (>=1.5
  promoter-favoring / <=0.67 SE-favoring / between = no preference) but did not pre-register an
  aggregate PROMOTE/REPEAT/REJECT verdict term for the overall experiment, since the L0
  question type is Descriptive, not a strict single hypothesis test. Noted here as an honest
  process gap, not silently patched after seeing results -- the per-factor classification
  itself WAS fully pre-registered and is what's reported above.
- dbSUPER's K562 super-enhancer calls were lifted from hg19 to GRCh38 via this repo's own
  from-scratch UCSC-chain liftOver (`scripts/liftover.py`) -- sanity-checked against a known
  coordinate (NOC2L TSS, matched GENCODE's native GRCh38 annotation to within 10bp) but 4/742
  (0.5%) super-enhancers failed to lift (fell in a chain gap) and were dropped, not imputed.
- Peak calling, cell-line passage, and antibody differences between the BRD4/MED1/POLR2A
  ENCODE experiments are not controlled for (different experiments, different labs' standard
  ENCODE pipeline runs) -- a known source of between-factor noise not addressed here.

## Recommendation

This is a real, reportable, orthogonal-method finding: genomic ChIP-seq occupancy of BRD4/MED1
in K562 favors super-enhancers over promoters, robust to a promoter-window sensitivity check.
Filed as a positive descriptive result (not to `null_results/` -- it is not a rejected
hypothesis, it is a completed, informative test whose direction differs from the reformulated
question's expectation). Worth citing alongside the imaging literature as a genuinely
complementary, not duplicative, line of evidence -- exactly the role this experiment was
designed to play per its Novelty Check.
