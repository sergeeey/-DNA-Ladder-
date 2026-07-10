---
experiment: exp_rloop_se_vs_typical_enhancer
date: 2026-07-10
ladder_tier: Standard
question_type: Descriptive
status: REJECT -- analysis complete, see decision.md
---

# Claim: Constituent enhancers inside super-enhancers show different R-loop
# overlap than length-matched typical (non-SE) H3K27ac enhancers, in K562

## Background

New research direction (`boyko-specialist`, 2026-07-10, 2nd targeted run this session)
after the "missing heritability via SE membership" direction closed with 3 convergent
nulls (`null_results/META_missing_heritability_2026-07-10.md`). Original premise from
`RESEARCH_DIRECTIONS.md` #6 (checked 2026-07-08) -- "only 21GB raw G4-seq data exists" --
was **partially falsified** on re-check: no small processed G4 file was found, but a
completely different, verified, small processed dataset exists for R-loops: **RLBase**
(Miller/Chédin/Bishop 2023, *NAR* 51(D1):D1129, PMID 36039757), a curated reprocessing
of 810 R-loop mapping experiments with public `hg38 broadPeak` files on
`s3://rlbase-data/` (verified directly via S3 API listing, not taken from the paper's
description).

## Gate 0 -- Novelty check (per falsification-ladder.md Step -3)

WebSearch found this is **NOT fully novel**: existing literature suggests R-loops /
enhancer-associated RNA are more prevalent at super-enhancers than typical enhancers
(e.g. a JUN-induced super-enhancer-RNA-to-R-loop mechanism paper, and a separate report
of higher RNA coverage at SE vs typical enhancers). **This changes the framing**, per
this session's established pattern (Ser5P, LLPS reformulations): this experiment is NOT
a first discovery, it is an **independent, matched-control replication** of a
plausible-but-not-rigorously-tested claim, using the same rigor (length-matching,
permutation test, positive-control-validated code) that reversed or nullified several
"obvious" claims already this session (BRD4/MED1, Gnocchi constraint). Whether the
literature's suggestive association survives a properly matched comparator is itself
the open, falsifiable question here.

## EstimandOps L0

**Question type:** Descriptive.

"Among H3K27ac-marked active-enhancer regions in K562, do those located inside a
super-enhancer show a different degree of R-loop (DNA:RNA hybrid) overlap than
length-matched H3K27ac regions outside any super-enhancer?"

## L1 Estimand

- **Population:** K562 H3K27ac ChIP-seq peaks already on disk (52,334 peaks,
  `data/input/h3k27ac_k562_grch38.json`), reused from prior experiments -- no new fetch.
- **Exposure:** Peak classified as "SE-constituent" (inside
  `data/input/k562_super_enhancers_grch38.json`, 738 SEs) vs. "typical enhancer"
  (outside any SE) -- identical classification code already written and tested for
  `exp_gnocchi_constraint_se_vs_typical_enhancer`.
- **Comparator:** SE-constituent vs. length-matched typical enhancers (same greedy
  nearest-neighbor log-length matching, same seed=42 convention as the prior two
  experiments in this direction, for methodological consistency).
- **Data source:** RLBase-processed R-loop peaks, sample **SRX1070682** (GEO GSM1720619,
  Sanz & Chédin 2016, K562 DRIP-seq, GSE70189/SRP059800, PMID 27373332) -- the original,
  most-cited canonical K562 DRIP-seq dataset in the RLBase catalog (chosen over pooling
  all 39 K562 DRIP-family samples to avoid mixing labs/protocols/conditions within one
  primary analysis; single well-characterized dataset is the more defensible primary
  choice, consistent with "one clean primary source, note alternatives as sensitivity"
  practice already used in this project). 44,753 peaks genome-wide, hg38, downloaded and
  row-count-verified directly from the file (not from a claimed count).
- **Endpoint:** Fraction of each enhancer region's length overlapped by an R-loop
  (broadPeak) interval -- 0.0 to 1.0, computed via the already-tested
  `merge_intervals`/`subtract_intervals`-style overlap logic
  (`tests/verify_interval_math.py`), not a new implementation.
- **Summary measure:** Mann-Whitney U + Cliff's delta on the matched-pair overlap
  fractions, plus a paired permutation test (10,000 perms) as primary significance
  measure -- identical statistical machinery to `exp_gnocchi_constraint_se_vs_typical_enhancer`
  (already positive-control-validated this session).
- **MCID:** |Cliff's delta| >= 0.2 AND permutation p < 0.05 -- same threshold convention
  as every prior experiment in this direction, for direct comparability.
- **ICE:** None -- a region with zero overlapping R-loop peaks gets overlap_fraction=0.0,
  not treated as missing.

## Limitations (stated before results)

1. **Single dataset, single lab, single condition ("S96").** Not pooled across the 39
   available K562 DRIP-family samples. A real effect specific to a different condition,
   lab, or DRIP variant (DRIPc/sDRIP/R-ChIP) would not be caught here. Flagged as a
   natural sensitivity-check candidate if this primary result is positive, not run by
   default (matches this project's "don't multiply comparisons past the pre-registered
   primary test" discipline).
2. **R-loop formation is itself associated with high transcription and GC-skew**, both
   of which likely differ between SE and typical enhancers independent of any SE-specific
   mechanism -- this experiment does NOT control for local transcription level or GC
   content, only length. A positive result here would be consistent with, but would not
   isolate, an SE-specific R-loop mechanism versus a transcription-level confound.
3. Same germline-vs-cancer-cell-line caveat pattern as before does not directly apply
   here (R-loops are not a germline-constraint measure), but K562 is still a single
   cancer cell line -- no cross-cell-line generalization claim is made.
4. Does NOT establish causality (SE causing R-loops, or vice versa) -- descriptive
   association only.
5. Does NOT resolve the literature ambiguity in general -- a null result here would mean
   "this comparator, this dataset, this cell line" shows no effect, not that the
   published JUN/SE-RNA mechanism is wrong (different system, different question).

## Status

Design-stage. Data downloaded and verified (SRX1070682_hg38.broadPeak, 44,753 peaks,
row count confirmed by direct file inspection). Analysis not yet run.
