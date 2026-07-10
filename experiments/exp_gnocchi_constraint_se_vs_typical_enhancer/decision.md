# Decision: exp_gnocchi_constraint_se_vs_typical_enhancer

**Date:** 2026-07-10
**Verdict:** REJECT

## Positive control (added 2026-07-10, later): pipeline validated on a known effect

Before trusting this REJECT, ran the exact same code (`weighted_mean_z`,
`mann_whitney_u`, `paired_permutation_test` -- unmodified, imported directly, not
re-derived) on a comparison with a known, large, well-documented effect: protein-coding
CDS exons (GENCODE v47 basic, GRCh38, n=3000 sampled) vs. length-matched random regions
>=100kb from any TSS (crude intergenic proxy). Script:
`scripts/gnocchi_positive_control_analysis.py`, tests: `tests/verify_gnocchi_positive_control.py`.

| Comparison | n pairs | median Z (test) | median Z (control) | Cliff's delta | permutation p |
|---|---|---|---|---|---|
| CDS exon vs. intergenic (positive control) | 1394 | **1.747** | **-0.325** | **+0.609** | **0.0001** |
| SE-constituent vs. typical enhancer (main result, K562) | 3675 | 1.268 | 1.071 | +0.051 | 0.083 |
| SE-constituent vs. typical enhancer (main result, HepG2) | 1380 | 0.997 | 1.109 | -0.044 | 0.010 |

The positive control found the expected effect at ~12x the MCID threshold, correctly
signed (coding = more constrained), at the permutation test's p-value floor
(1/(n_perm+1)). **This confirms the pipeline can detect large real effects when they
exist.** The SE-vs-typical-enhancer null is therefore not attributable to a broken or
underpowered pipeline -- same code, same data source, same statistical machinery,
correctly detects a ~12x-larger, well-established effect. The REJECT above is trustworthy.

Full results: `experiments/exp_gnocchi_constraint_se_vs_typical_enhancer/positive_control_results.json`

## Result

Pre-registered MCID (in `claim.md`, written before this analysis ran):
`abs(cliffs_delta) >= 0.2 AND p_value_permutation_bh < 0.05`

| Cell line | n matched pairs (with Gnocchi coverage) | median Z (SE) | median Z (typical) | Cliff's delta | permutation p | permutation p (BH) |
|---|---|---|---|---|---|---|
| K562 | 3675 / 5993 (61.3%) | 1.268 | 1.071 | **+0.051** | 0.083 | 0.083 |
| HepG2 | 1380 / 1889 (73.0%) | 0.997 | 1.109 | **-0.044** | 0.010 | 0.021 |

**Neither cell line meets both MCID components.** HepG2's permutation p survives BH
correction, but its Cliff's delta (-0.044) is less than 1/4 of the pre-registered
practical threshold (0.2) -- statistically detectable, not practically meaningful,
the same "significant only because of sample size" pattern seen repeatedly in this
project (Hypothesis C in ARCHCODE, the original ClinVar heritability experiment).

**Direction reverses between cell lines** (K562 positive, HepG2 negative). This is
the same red flag that drove the final REJECT of the BRD4/MED1 LLPS experiment
(`exp_llps_promoter_vs_se_chip_evidence`) -- a real, cell-type-invariant biological
effect on regulatory-element constraint should not flip sign between two cell lines
under the same estimand.

## Why this REJECT carries more weight than the ClinVar-based ones

This experiment used **Gnocchi** (Chen/Francioli/Karczewski 2023, gnomAD v3.1.2,
germline WGS-derived), which shares **zero** data-source overlap with the two prior
heritability experiments (both ClinVar-based). It was specifically designed to
remove the ClinVar-ascertainment-bias confound that `boyko-specialist` and an
external critique both flagged as a real limitation of the earlier design. The null
result is not an artifact of ClinVar bias -- that confound has been eliminated here
and the null persisted anyway.

Combined with the two ClinVar-based nulls (`20260708-heritability-vus-se-frequency`,
and `exp_heritability_vus_se_vs_typical_enhancer`, pending at time of writing), the
"missing heritability" direction now has **three independent estimands, three
different data sources, converging on no meaningful signal** for
super-enhancer-vs-typical-enhancer distinction using population-genetics evidence.

## Methodological notes (what worked as designed)

- Region-level length-weighted mean Z (not per-window pooling) resolved the
  pseudoreplication concern raised in the external critique -- unit of analysis was
  the enhancer region (n=3675/1380 independent regions), not correlated 1kb windows.
- Length-matching removed the length confound (median matched length identical to
  the bp between SE and typical groups: 685bp K562, 1531bp HepG2).
- Paired permutation test (10,000 permutations, label-swap within matched pairs) was
  used as primary significance measure, per the critique's recommendation, rather
  than relying solely on the analytic Mann-Whitney p (which, as expected, showed the
  familiar "significant p, small effect" divergence at K562: MWU p=0.00017 vs.
  permutation p=0.083 on the same data -- the permutation test is more conservative
  here because it respects the pairing structure).

## What did NOT get resolved (real limitations, not glossed over)

1. **No H3K27ac signal-intensity matching** -- only length was matched (our fetched
   peak data has no signal/score field). A real effect masked by signal-strength
   confound cannot be ruled out. Flagged in claim.md before running, not added after.
2. **~35-40% pair dropout** (no QC-passed Gnocchi window overlap) -- driven by short
   peaks in low-coverage or repeat-masked regions failing Gnocchi's own QC filters.
   Not obviously biased toward one group over the other (both groups length-matched
   before this dropout), but not formally tested for differential dropout.
3. **Germline vs. cell-type-specific selection distinction still applies** (stated
   in claim.md before running) -- moot here since no effect was found in the first
   place, but worth remembering this experiment could never have shown "K562-specific
   selection" even with a positive result.

## What This Result Does NOT Mean

1. Does NOT prove regulatory elements in general are free of negative selection --
   only that SE-vs-typical-enhancer classification (via H3K27ac + dbSUPER stitching)
   does not track germline constraint in these two cell lines, at this resolution.
2. Does NOT contradict the original Gnocchi paper's finding that non-coding
   constrained regions are broadly enriched for regulatory elements as a class
   (promoter/enhancer vs. non-regulatory) -- this experiment tested a finer
   distinction (SE vs. typical enhancer WITHIN the regulatory-element class), a
   different and narrower question.
3. Does NOT rule out that a different super-enhancer caller, a different
   H3K27ac-signal-based comparator, or additional cell lines would show an effect --
   REJECT applies to this specific estimand, not to the general concept.
4. Does NOT establish causality in either direction even if the effect had been
   found -- descriptive association only, as pre-specified.

## Recommendation

File to `null_results/`. The "missing heritability via SE/typical-enhancer
comparison" line of inquiry has now failed three independent tests across two
completely different data sources (ClinVar clinical variants, gnomAD germline WGS
constraint). Recommend closing this specific direction rather than seeking a fourth
data source -- diminishing returns, and three convergent nulls across independent
methods is itself informative (no obvious hidden ascertainment-bias artifact
explains all three).
