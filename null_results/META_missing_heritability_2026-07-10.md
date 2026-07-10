# Meta-conclusion: "missing heritability via super-enhancer membership" direction

**Date:** 2026-07-10
**Status:** Direction closed. Not a failure — a validated negative result.

## What did NOT confirm (the biological hypotheses)

1. Stable BRD4/MED1 enrichment in super-enhancers vs. active chromatin
   (`20260710-llps-promoter-vs-se-chip-evidence`)
2. VUS frequency difference: inside SE vs. everywhere else
   (`20260708-heritability-vus-se-frequency`)
3. VUS frequency difference: inside SE vs. matched typical enhancers
   (`20260710-heritability-vus-se-vs-typical-enhancer`)
4. Elevated germline constraint (Gnocchi) in SE vs. matched typical enhancers
   (`20260710-gnocchi-constraint-se-vs-typical-enhancer`)

In every case: effect near zero, or sign flipped between K562 and HepG2.

## What DID confirm (harder, more important findings)

### 1. The pipeline works
Positive control (CDS exons vs. length-matched intergenic regions, same unmodified
`weighted_mean_z`/`mann_whitney_u`/`paired_permutation_test` code): Cliff's delta
**+0.609**, correctly signed, p at the permutation floor. The method detects real
signal when it exists — the SE-vs-typical nulls are not a broken-pipeline artifact.

### 2. The core idea does not survive convergent testing
Three independent estimands, two independent data sources (ClinVar clinical variants,
gnomAD/Gnocchi germline constraint), two cell lines — all converge on the same answer:
**super-enhancer membership itself does not explain VUS frequency or germline
constraint in this formulation.** This is a coherent, well-powered null, not three
unlucky rolls.

### 3. A real infrastructure finding for the next direction
The premise that only heavy raw data exists for R-loop mapping was itself false —
RLBase (Miller/Chédin/Bishop 2023, NAR, PMID 36039757) provides verified, public,
processed `hg38 broadPeak` files (76KB-11MB each, not GB-scale) for 75 K562 R-loop
experiments. Confirmed by direct S3 bucket query, not taken on faith from the paper.

## Why this matters for a falsification-first project

For this project's own stated standard (`CLAUDE.md`: "Презумпция ложности любого
сгенерированного артефакта"), a hypothesis that fails to survive convergent,
independently-sourced, pipeline-validated testing is a *successful* application of the
method, not a disappointing session. The alternative — declaring victory on a
borderline p-value from a single weak comparator — is exactly the failure mode this
project's protocols (matched controls, positive controls, multi-source convergence)
exist to prevent.
