# Decision: exp_g4_se_vs_typical_enhancer

**Date:** 2026-07-10
**Verdict:** REJECT

## Result

Pre-registered MCID (in `claim.md`, written before this analysis ran):
`abs(cliffs_delta) >= 0.2 AND p_value_permutation < 0.05`

| Cell line | n pairs | % SE with G4 overlap | % typical with G4 overlap | Cliff's delta | permutation p |
|---|---|---|---|---|---|
| K562 | 5993 | 15.08% | 19.86% | **-0.047** | 0.0001 (floor, n-driven) |
| HepG2 | 1889 | 20.22% | 22.71% | **-0.024** | 0.995 (not significant at all) |

Both cell lines: wrong-for-hypothesis direction (typical enhancers show marginally MORE
G4 overlap than SE-constituents, not less), both far below MCID. K562's p is at the
permutation floor purely from n=5993 (same "significant by sample size, not by effect"
pattern as every other REJECT this session); HepG2 shows no signal at all (p=0.995).

## Liftover quality check

9205 K562 / 8805 HepG2 hg19 peaks -> 9174 / 8780 GRCh38 (31 / 25 failed to lift, 0.3%/0.3%
loss rate) -- consistent with the loss rates seen in the original dbSUPER SE liftover
earlier this session, not an anomaly.

## Relationship to the direction's overall pattern

This is the **fifth REJECT** in the "does SE membership distinguish enhancer subclasses"
direction today, across five genuinely different data types: BRD4/MED1 ChIP-seq
occupancy, ClinVar VUS frequency (x2 comparators), Gnocchi germline constraint, R-loop
(DRIP-seq) overlap, and now G4 (BG4 ChIP-seq) overlap. Every single test, regardless of
data source or biological mechanism, converges on the same answer: length-matched
SE-vs-typical-enhancer comparison shows no meaningful, direction-consistent effect. This
is now less "five separate null results" and more one very consistent finding about the
limits of super-enhancer classification as a distinguishing biological variable at this
resolution, using this project's SE-calling method (dbSUPER/H3K27ac stitching).

## What This Result Does NOT Mean

1. Does NOT contradict GSE145090's own headline finding that G4s are broadly enriched at
   active chromatin/TF-binding sites in general -- this tests a narrower distinction
   (SE vs. typical, both already active) that the source paper did not itself test.
2. Does NOT control for GC-content/sequence-composition differences between SE and
   typical enhancers (flagged in `claim.md` as the most significant limitation for this
   specific comparison, since G4 formation is strongly G-rich-sequence dependent) -- a
   real GC-skew confound could exist in either direction and this design cannot detect it.
3. Does NOT establish causality -- descriptive only, as pre-specified.
4. Does NOT rule out a different G4-detection method (G4-seq, CUT&Tag) showing a
   different result -- single dataset/protocol per cell line, as stated in Limitation 2.

## Recommendation

File to `null_results/`. This closes the non-B DNA (G4) sub-direction opened today.
Combined with the R-loop REJECT, both halves of the original "non-B DNA structures"
research direction (`RESEARCH_DIRECTIONS.md` #6) are now tested and closed with real
processed data -- the direction as a whole is exhausted for the SE-vs-typical-enhancer
framing specifically (a different framing, e.g. G4/R-loop density vs. gene expression
level or vs. replication timing, was not tested and remains open if pursued).
