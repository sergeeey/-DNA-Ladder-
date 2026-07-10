---
experiment: exp_llps_promoter_vs_se_chip_evidence
date: 2026-07-08
ladder_tier: Standard
question_type: Descriptive
status: "FINAL 2026-07-10: REJECT. Matched-control test (H3K27ac typical enhancers) falsifies the original SE-favoring claim: BRD4 no preference/reverses in both cell lines; MED1 splits 1-1 across K562/HepG2 with no explanation. ENCODE data exhausted for both factors (BRD4: 2 valid + 1 revoked; MED1: 2 total) -- no 3rd cell line exists to test further. Filed to null_results/. Full timeline in decision.md."
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
- **Summary measure (finalized 2026-07-08, BEFORE running the analysis script):** for BRD4 and
  MED1 separately (the two coactivator/condensate-associated factors; POLR2A is reported as
  a broad-binding sanity baseline, not a primary test, since Pol II occupies gene bodies far
  more broadly than promoters/SEs specifically), classify each peak's midpoint as
  promoter-proximal (within 2kb of the nearest GENCODE GRCh38 TSS), SE-associated (falls
  within a lifted-to-GRCh38 dbSUPER K562 super-enhancer interval), both, or neither. Compute
  **peak density** (peaks per kb of accessible region) separately for the promoter-only-class
  region-space and the SE-only-class region-space (accounts for the fact these two region
  classes cover very different total genomic bp -- raw peak counts alone would be misleading).
  Primary summary measure: **promoter/SE density ratio** = density_promoter_only /
  density_SE_only.
- **MCID (finalized 2026-07-08, BEFORE running the analysis script):** density ratio >= 1.5
  -> promoter-favoring (supports the reformulated question's promoter-centric direction);
  density ratio <= 0.67 -> SE-favoring; between 0.67 and 1.5 -> no clear preference / mixed.
  Chosen as a symmetric log-scale threshold (1.5x / (1/1.5)x) rather than a p-value, matching
  this project's "effect size over p-value" discipline from ARCHCODE's Hypothesis C
  (`ARCHCODE/null_results/20260707-synonymous-codon-optimality.md` -- a p<1e-6 result with a
  sub-threshold effect size was correctly REJECTed there; the same practical-significance bar
  applies here).
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

**Genome build decision (2026-07-08, `[VERIFIED-bash]` via ENCODE REST API, BEFORE any peak
data fetched):** checked file-level assembly availability, not just experiment-level -- MED1
(`ENCSR269BSA`) has no hg19 files at all, only GRCh38 released status; BRD4 (`ENCSR583ACG`) has
hg19 files but they are archived (superseded), with GRCh38 released current; POLR2A
(`ENCSR031TFS`/`ENCSR388QZF`) has released files in both builds. **Decision: standardize on
GRCh38** for all ChIP-seq peaks (matches what's actually current/released for all 3 factors)
rather than hg19 (which would force using an archived BRD4 file and finding a non-ENCODE MED1
source). dbSUPER's K562 super-enhancer call set is hg19-only (confirmed --
`asntech.org/dbsuper/data/bed/hg38/K562.bed` and `.../GRCh38/K562.bed` both 404) -- will be
lifted to GRCh38 via the standard UCSC `hg19ToHg38.over.chain.gz` chain file, not re-derived or
approximated. GENCODE TSS annotations will be fetched directly in GRCh38. Recorded BEFORE
fetching any peak file, specifically to avoid the hg19/hg38 mismatch bug class ARCHCODE hit
multiple times this same session.

Next step: implement the liftover, fetch the GRCh38 peak files for BRD4/MED1/POLR2A, fetch
GRCh38 GENCODE TSS annotations, finalize summary measure + MCID, then run the analysis. Not
yet done -- no results exist.
