# Decision: exp_rloop_se_vs_typical_enhancer

**Date:** 2026-07-10
**Verdict:** REJECT

## Result

Pre-registered MCID (in `claim.md`, written before this analysis ran):
`abs(cliffs_delta) >= 0.2 AND p_value_permutation < 0.05`

| Metric | SE-constituent | Typical enhancer |
|---|---|---|
| n (matched pairs) | 5993 | 5993 |
| % with any R-loop overlap | 23.6% | 27.5% |
| median overlap fraction | 0.0 | 0.0 |

**Cliff's delta = -0.042** (wrong-for-the-hypothesis direction: typical enhancers show
*slightly more* R-loop overlap, not SE), **permutation p = 0.0001** (at the test's floor,
1/(n_perm+1) -- driven entirely by the large n=5993, not a meaningful effect size).
Fails the MCID: p is far below 0.05, but |delta|=0.042 is 1/5th of the pre-registered
practical threshold (0.2). Same "significant-by-sample-size, not by magnitude" pattern
seen repeatedly this session (Hypothesis C in ARCHCODE, the original ClinVar heritability
test, the Gnocchi K562 result).

## Relationship to the pre-run literature caveat

`claim.md`'s Gate 0 flagged this as NOT fully novel -- prior literature suggested SE
might show *more* R-loop/enhancer-RNA signal than typical enhancers. This experiment,
using a matched-length comparator and a single well-characterized canonical dataset
(SRX1070682, Sanz/Chédin 2016), does not reproduce that direction at all -- if anything
it trends (negligibly) the other way. This is consistent with this session's now-repeated
finding that "obvious" SE-associated claims tend to weaken or reverse under a properly
matched comparator (BRD4 in HepG2, Gnocchi constraint in both cell lines) -- not evidence
the underlying literature claim is wrong (different systems, different R-loop assay,
possibly different condition/mechanism), but evidence that a naive "SE vs whole genome"
or "SE vs same-cell-type not-matched" comparison would likely have overstated the effect.

## What This Result Does NOT Mean

1. Does NOT contradict the JUN-induced SE-RNA-to-R-loop mechanism paper or other cited
   literature -- different cell system/context, narrower and different question (this is
   K562 DRIP-seq broadPeak overlap, not nasopharyngeal-carcinoma SE-RNA mechanism).
2. Does NOT rule out R-loop differences using a different DRIP variant (DRIPc/sDRIP/R-ChIP,
   38 other K562 samples available in RLBase but not tested here -- see Limitation 1 in
   `claim.md`), a different lab's protocol, or a transcription-level-matched comparator
   instead of length-matched.
3. Does NOT establish causality in either direction -- descriptive only, as pre-specified.
4. Does NOT mean R-loops are absent from super-enhancers -- 23.6% of SE-constituent
   regions DO overlap an R-loop peak; the finding is that this rate is not higher (if
   anything marginally lower) than in length-matched typical enhancers, not that R-loops
   don't occur there at all.

## Recommendation

File to `null_results/`. This closes the primary (Sanz/Chédin canonical dataset,
length-matched) test of this direction. A natural, cheap follow-up (not run today) would
be repeating with the transcription-matched or GC-matched comparator flagged as
Limitation 2 in `claim.md`, or testing one of the other 38 K562 DRIP-family samples as a
sensitivity check -- neither is run by default per this project's "don't multiply
comparisons past the pre-registered primary test" discipline.
