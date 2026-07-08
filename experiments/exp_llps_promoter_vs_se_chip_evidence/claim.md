---
experiment: exp_llps_promoter_vs_se_chip_evidence
date: 2026-07-08
ladder_tier: Standard
question_type: Descriptive
status: DESIGN -- L0/Novelty done, K562 ChIP-seq data CONFIRMED available (BRD4/MED1/POLR2A/POLR2A-phosphoS5); super-enhancer call set not yet sourced
---

# Claim: ChIP-seq occupancy patterns of condensate-associated factors are more consistent with a promoter-centric than a super-enhancer-centric model of Pol II condensation

## Background

First DNA Ladder experiment, from the LLPS/Pol-II-condensates literature pass (2026-07-08,
`Research Library/evidence_matrices/llps-pol2-condensates.md`). Report's own "Hypothesis A"
(promoter-first condensate model) is the starting point, reformulated below after a Novelty
Check.

## EstimandOps L0

**Question type:** Descriptive.
"Genome-wide, in a well-characterized human cell line, is BRD4/MED1/Pol II ChIP-seq peak
co-occupancy more strongly enriched at promoters or at super-enhancers, and does this static
genomic-distribution pattern favor a promoter-centric or SE-centric interpretation of where
condensate-associated factors concentrate?"

Descriptive, not causal: no perturbation, no DAG. Also explicitly NOT a live-cell/single-molecule
test (see Novelty Check below for why that specific claim is out of scope here).

## Novelty check (mandatory, per falsification-ladder.md Step -3)

Ran via `Research Library` CrossRef-verification tooling before any data work, 2026-07-08:

**The broad claim is NOT novel and is currently the field's own frontier hypothesis, not
available for DNA Ladder to "discover":**
- Bogdanović et al. 2026, "Large RNA polymerase II condensates are promoter-centric assemblies
  associated with early stages of transcription at all expressed genes" — DOI
  [10.64898/2026.05.25.727590](https://doi.org/10.64898/2026.05.25.727590), independently
  verified via CrossRef 2026-07-08.
- Pandey et al. 2026, "Transcription condensates are promoter hubs that enhance transcriptional
  bursts" — DOI [10.64898/2026.05.24.727549](https://doi.org/10.64898/2026.05.24.727549),
  independently verified via CrossRef 2026-07-08.

Both are 2026 preprints making essentially this exact claim, using live-cell single-molecule
imaging -- a methodology this project has no access to. Running the same imaging-based test
would not be novel even if it were feasible.

**Reformulated, honest scope:** this experiment does NOT attempt to replicate or discover the
promoter-centric imaging finding. It asks a *different, complementary* question using a
*different methodology* this project CAN actually run with real public data: whether the
static, population-averaged genomic distribution of condensate-associated factors (ChIP-seq
peaks, not live imaging) is independently consistent with the promoter-centric model. This is
the same "different data source, complementary not duplicative" pattern ARCHCODE used for its
own enhancer-proximity replication (`ARCHCODE/experiments/exp_enhancer_proximity_replication`)
-- a positive result here would be independent corroborating evidence from an orthogonal
method (genomics vs. imaging), not a discovery of the mechanism itself; a negative result would
not falsify the imaging-based papers (different methodology, different claim resolution).

## L1 Estimand

- **Population:** BRD4, MED1, and Pol II (POLR2A) ChIP-seq peaks in a single well-characterized
  human cell line (candidate: K562, matches ARCHCODE's existing ENCODE usage -- to be confirmed
  once data availability is checked).
- **Exposure:** Peak distance/overlap classification: promoter-proximal (within N bp of a
  GENCODE-annotated TSS) vs. super-enhancer-associated (within a called super-enhancer region,
  e.g. from ROSE/dbSUPER or an ENCODE-derived call set) vs. neither.
- **Comparator:** Relative enrichment of BRD4/MED1 signal at promoter-proximal vs.
  SE-associated vs. neither-class regions; Pol II occupancy/signal as the readout variable.
- **Endpoint:** Peak co-occupancy and signal-intensity patterns by region class.
- **Summary measure:** Not yet finalized -- pending data availability check (candidates:
  odds ratio of co-occupancy by class, or a rank-based comparison of signal intensity
  distributions, matching this project's from-scratch stats conventions from ARCHCODE
  (Mann-Whitney U, Cliff's delta, BH correction)).
- **MCID:** Not yet set -- to be pre-registered once the summary measure is finalized, before
  any data is pulled.
- **ICE:** None anticipated (complete-case peak-calling data).

## What This Does NOT Mean

1. Does NOT test or replicate the live-cell imaging claims of Bogdanović 2026 / Pandey 2026 --
   different methodology, different resolution, different claim.
2. A positive result does NOT prove causality or mechanism -- static ChIP-seq co-occupancy is
   correlational by construction.
3. A negative result does NOT falsify the promoter-centric imaging papers -- ChIP-seq averages
   over a cell population and over time; it may simply lack the resolution to detect a dynamic,
   transient, single-cell phenomenon those papers report.
4. Does NOT establish which mechanism (LLPS vs. multivalent recruitment vs. chromatin
   co-condensation) explains any observed pattern -- see
   `Research Library/evidence_matrices/llps-pol2-condensates.md` "LLPS vs non-LLPS" table;
   ChIP-seq alone cannot distinguish these.

## Status

**Data availability check (2026-07-08, via ENCODE REST API, `[VERIFIED-bash]`):** confirmed
real released ChIP-seq experiments exist in K562 for all core factors:
- BRD4: `ENCSR583ACG`
- MED1: `ENCSR269BSA`
- POLR2A: 10 experiments; `ENCSR031TFS`/`ENCSR388QZF` are untreated baseline candidates
  (`ENCSR000EHP` is IFNg-treated, excluded for a baseline test)
- POLR2A-phosphoS5 (bonus): `ENCSR000BKR` -- directly relevant to the CTD-phosphorylation-switch
  mechanism in `Research Library/evidence_matrices/llps-pol2-condensates.md`

**Not yet sourced:** a super-enhancer call set for K562 (candidates: dbSUPER, or derive via
ROSE from the H3K27ac data ARCHCODE already has cached for K562 --
`ARCHCODE/data/encode_cache/ENCFF252DWA_H3K27ac_K562_hg19.bed.gz` -- reusing ARCHCODE data
would need a genome-build check, hg19 vs whatever build these new accessions use, before any
reuse, per the hg19/hg38 lesson from ARCHCODE's own bug history).

Next step: source/derive the SE call set, finalize summary measure + MCID, then fetch peak
files and run the analysis. Not yet done -- no results exist.
