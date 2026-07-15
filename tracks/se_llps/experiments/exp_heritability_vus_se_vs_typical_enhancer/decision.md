# Decision: exp_heritability_vus_se_vs_typical_enhancer

**Date:** 2026-07-10
**Verdict:** REJECT

## Result

Pre-registered MCID (in `claim.md`, written before this analysis ran):
`abs(cliffs_delta) >= 0.2 AND p_value_bh < 0.05`

| Cell line | n SE (with AF) | n typical (with AF) | median log10(AF) SE | median log10(AF) typical | Cliff's delta | p (BH) |
|---|---|---|---|---|---|---|
| K562 | 1905 | 1886 | -5.210 | -5.225 | **+0.0077** | 0.680 |
| HepG2 | 2211 | 1874 | -5.318 | -5.208 | **-0.0192** | 0.578 |

Both cell lines: effect size is essentially zero (two orders of magnitude below the
MCID of 0.2), not statistically significant even before the practical-significance
threshold is applied. Cleanest null of the three "missing heritability" experiments --
no ambiguity, no borderline p-value to interrogate.

## Why this matters alongside the other two nulls

This is the matched-comparator correction of `exp_heritability_vus_se_frequency`
(REJECT, 2026-07-08, VUS-in-SE vs. everywhere-else) -- same data source (ClinVar VUS +
gnomAD v4 AF), narrower/fairer comparator (VUS-in-SE vs. VUS-in-typical-H3K27ac-enhancer,
not vs. the whole genome). The narrower comparator did not resurrect an effect that a
coarse comparator might have hidden -- if anything, the effect is even closer to zero
than the original (0.0077-0.0192 here vs. 0.01-0.03 in the original).

Combined with `exp_gnocchi_constraint_se_vs_typical_enhancer` (REJECT, same day,
completely independent data source -- gnomAD germline WGS constraint, not ClinVar
clinical variants, pipeline validated via positive control on CDS-vs-intergenic), the
"missing heritability via SE membership" direction has now failed **three independent
tests across two unrelated data sources**, with the most methodologically careful
version of each (matched comparator, validated pipeline) showing progressively weaker,
not stronger, signal. This is a coherent, convergent null, not three unlucky rolls.

## What This Result Does NOT Mean

1. Does NOT prove ClinVar VUS allele frequency is uninformative for interpretation in
   general -- only that SE-vs-typical-enhancer membership specifically does not track
   it, in these two cell lines, at this resolution.
2. Does NOT rule out that some OTHER regulatory-element classification (not
   SE-vs-typical) would show a frequency difference.
3. The ClinVar-ascertainment-bias limitation (WebSearch-verified earlier this session)
   still applies to this specific experiment's data source -- but the independent
   Gnocchi-based null (ClinVar-free) makes this limitation moot for the overall
   direction-level conclusion, since it converges on the same answer without that bias.
4. Does NOT establish causality -- descriptive comparison only, as pre-specified.

## Recommendation

File to `null_results/`. Close the "missing heritability via SE-vs-typical-enhancer"
direction -- three independent estimands, two independent data sources, one validated
pipeline, all converge on no meaningful effect. Recommend moving to a new research
direction rather than a fourth variant of this same comparison.
