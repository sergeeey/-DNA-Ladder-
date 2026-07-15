---
experiment: exp_g4_se_vs_typical_enhancer
date: 2026-07-10
ladder_tier: Standard
question_type: Descriptive
status: REJECT -- analysis complete, see decision.md
---

# Claim: Constituent enhancers inside super-enhancers show different G-quadruplex
# (G4) overlap than length-matched typical (non-SE) H3K27ac enhancers, in K562 and HepG2

## Background

Second `boyko-specialist` re-search this session on the non-B DNA direction. First pass
found the niche (BG4 CUT&Tag / Balasubramanian lab) but the specific processed file was
`[UNKNOWN]`. This targeted re-search found a stronger, fully verified source: **GSE145090**
(Spiegel, Cuesta, Adhikari et al. 2021, *Genome Biology* 22:117, PMC8063395,
Balasubramanian/Hänsel-Hertsch lab lineage -- same niche identified in the first pass),
official NCBI GEO FTP processed BED files for **both K562 (9205 peaks) and HepG2 (8805
peaks)** -- matches this project's exact cell-line pair, unlike the earlier ambiguous
CUT&Tag 2024 lead. Peak counts cross-verified: both match the paper's own abstract exactly
(9205 K562 / 8805 HepG2), confirming these are the final published peak sets, not an
intermediate artifact.

## Gate 0 -- Novelty check (per falsification-ladder.md Step -3)

Not explicitly re-run as a fresh search (would substantially duplicate the R-loop
experiment's Gate 0 reasoning) -- the same class of prior-literature caveat applies by
analogy: G4 structures are known to be enriched at active promoters/enhancers in general
(this is essentially GSE145090's own headline finding -- G4s as TF-binding hubs at active
chromatin). Whether G4 density specifically distinguishes SE from typical (both already
H3K27ac-active) enhancers is the narrower, not-obviously-answered question tested here,
following the same "matched-comparator replication of a plausible-but-untested specific
claim" framing established for R-loop and Gnocchi this session.

## EstimandOps L0

**Question type:** Descriptive.

"Among H3K27ac-marked active-enhancer regions in K562/HepG2, do those located inside a
super-enhancer show a different degree of G-quadruplex (BG4 ChIP-seq) overlap than
length-matched H3K27ac regions outside any super-enhancer?"

## L1 Estimand

- **Population:** K562 (52,334 peaks) and HepG2 (48,298 peaks) H3K27ac ChIP-seq peaks
  already on disk -- no new fetch, reused from all three prior experiments in this
  direction.
- **Exposure:** SE-constituent (inside `k562_super_enhancers_grch38.json` /
  `hepg2_super_enhancers_grch38.json`) vs. typical enhancer (outside) -- identical
  classification code already tested twice this session.
- **Comparator:** Length-matched typical enhancers (same greedy log-length matching,
  seed=42, as every prior experiment in this direction).
- **Data source:** GSE145090 official GEO-deposited processed BED files
  (`GSE145090_20180108_K562_async_rep1-3.mult.5of8.bed.gz`, 9205 peaks;
  `GSE145090_HepG2_async_rep1-3.mult.6of9.bed.gz`, 8805 peaks) -- BG4 ChIP-seq,
  Spiegel/Cuesta/Adhikari et al. 2021, PMC8063395. **Genome build: hg19** (confirmed via
  the authors' own pipeline repo, github.com/sblab-bioinformatics/G4-vs-TFs) -- lifted to
  GRCh38 via this project's own from-scratch `scripts/liftover.py` (already used and
  reviewer-fixed for the original dbSUPER SE liftover in the LLPS experiment).
- **Endpoint:** Fraction of each enhancer region's length overlapped by a G4 peak (0.0 to
  1.0) -- identical `overlap_fraction`-style logic to the R-loop experiment, reusing
  `merge_intervals` for the G4 peak set before computing overlap (same latent
  double-counting fix already applied there).
- **Summary measure:** Mann-Whitney U + Cliff's delta + paired permutation test (10,000
  perms), same statistical machinery as every prior experiment in this direction.
- **MCID:** |Cliff's delta| >= 0.2 AND permutation p < 0.05 -- same convention throughout.
- **ICE:** None -- zero overlap is a valid 0.0 value, not missing.

## Limitations (stated before results)

1. **hg19-to-GRCh38 liftover introduces a small, known source of coordinate imprecision**
   (single-bp-scale, per the reviewer-verified fix from the LLPS experiment) -- immaterial
   at the enhancer-region kb-scale used here, but stated for completeness.
2. **Single dataset/protocol per cell line** (BG4 ChIP-seq, one lab) -- does not test
   whether a different G4-detection method (e.g. G4-seq, CUT&Tag) would replicate.
3. Same length-only (not GC-content or transcription-matched) comparator limitation as the
   R-loop and Gnocchi experiments -- G4 formation is strongly sequence-composition (G-rich)
   dependent, so this is a more significant caveat here than for R-loops: a positive result
   would be confounded by any GC-skew difference between SE and typical enhancers that this
   design does not control for.
4. Does NOT establish causality -- descriptive association only.
5. A null result here would NOT contradict GSE145090's own headline finding (G4s enriched
   at active chromatin generally) -- this tests a narrower SE-vs-typical distinction within
   already-active enhancers, not G4-vs-inactive-genome.

## Status

Design-stage. Data downloaded and peak-count-verified against the source paper's abstract
(exact match). Liftover and analysis not yet run.
