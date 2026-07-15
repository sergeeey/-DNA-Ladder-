---
experiment: exp_llps_promoter_vs_se_hepg2_replication
date: 2026-07-08
ladder_tier: Standard
question_type: Descriptive
status: "SUPERSEDED 2026-07-10: the parent experiment (exp_llps_promoter_vs_se_chip_evidence) this replication tested against was itself REJECTed after a matched-control follow-up. Original PARTIAL REPLICATION result (MED1 clean, BRD4 marginal) preserved for the record but no longer the operative conclusion -- see that experiment's decision.md 'FINAL closure' section."
---

# Claim: BRD4/MED1 SE-favoring density ratio replicates in HepG2 (independent cell line)

## Background

Third DNA Ladder experiment -- generalization test for
`experiments/exp_llps_promoter_vs_se_chip_evidence` (K562: BRD4 ratio=0.414, MED1 ratio=0.523,
both SE-favoring, robust to a window-size sensitivity check). That experiment's own
`decision.md` explicitly flagged single-cell-line generalization as untested. This experiment
addresses that named limitation directly.

## EstimandOps L0

**Question type:** Descriptive.
"Does the same promoter/SE peak-density-ratio method, applied to BRD4/MED1/POLR2A ChIP-seq in
HepG2 (a different cell line, same GRCh38 build, same dbSUPER-derived SE-calling approach),
reproduce the SE-favoring pattern found in K562, or is that pattern K562-specific?"

## Novelty check (per falsification-ladder.md Step -3)

Not applicable in the usual sense -- this is an explicit, planned **replication** of this
project's own prior finding on independent data, not a new claim about the literature. No
Novelty Check is needed to establish that "replicate your own finding in a second cell line"
is a legitimate next step; it is standard scientific practice, pre-registered as the named
follow-up in the first experiment's own decision.md.

## L1 Estimand

- **Population:** BRD4, MED1, POLR2A ChIP-seq peaks, HepG2, GRCh38.
  Accessions confirmed available via ENCODE REST API, 2026-07-08:
  - BRD4: `ENCSR395MHA`, file `ENCFF898YRY` (IDR thresholded peaks, GRCh38, released)
  - MED1: `ENCSR959XNY`, file `ENCFF493UFO` (IDR thresholded peaks, GRCh38, released)
  - POLR2A: `ENCSR000EEM`, file `ENCFF354VWZ` (IDR thresholded peaks, GRCh38, released;
    note a treated variant `ENCSR000EEP` (forskolin) exists and is explicitly excluded)
- **Exposure/Comparator:** Identical method to the K562 experiment -- promoter-proximal
  (2kb/5kb TSS windows, GENCODE v47 native GRCh38, same file reused) vs. dbSUPER HepG2
  super-enhancer calls (hg19, lifted to GRCh38 via this repo's own `scripts/liftover.py`,
  same as K562).
- **Endpoint:** Peak density (peaks/kb) in promoter-only vs SE-only region space.
- **Summary measure:** Promoter/SE density ratio, identical formula and code
  (`scripts/llps_promoter_vs_se_analysis.py`, parameterized for HepG2 inputs).
- **MCID (pre-registered before running, identical to the K562 experiment for direct
  comparability):** ratio >=1.5 promoter-favoring / <=0.67 SE-favoring / between = no clear
  preference. **Replication criterion:** HepG2 counts as replicating the K562 finding if BOTH
  BRD4 and MED1 classify as SE-favoring (<=0.67) at the primary 2kb window AND the direction is
  unchanged (not necessarily identical magnitude) at the 5kb sensitivity window.
- **ICE:** None anticipated.

## What This Does NOT Mean

1. A replication in HepG2 would NOT prove the pattern is universal across all cell
   types -- two cell lines is still a small n of biological contexts.
2. A failure to replicate would NOT invalidate the K562 finding -- it would mean the SE-favoring
   pattern is cell-type-dependent, which is itself informative (regulatory landscapes differ
   substantially between K562 (erythroleukemia) and HepG2 (hepatocellular carcinoma)).
3. Does NOT test mechanism (LLPS vs. conventional recruitment) -- same limitation as the first
   experiment.

## Status

Design-stage. Data availability confirmed (`[VERIFIED-bash]`, ENCODE REST API, all 3 factors +
dbSUPER HepG2 super-enhancers, GRCh38). Not yet fetched or analyzed.
