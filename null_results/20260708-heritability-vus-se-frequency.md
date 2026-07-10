---
experiment: exp_heritability_vus_se_frequency
date: 2026-07-08
verdict: REJECT — no detectable effect, neither statistically significant nor practically meaningful
---

# Decision — ClinVar VUS Population Frequency: In vs. Outside Super-Enhancers

## Result

| Comparison | n (SE) | n (outside) | median log10(AF) SE | median log10(AF) outside | Cliff's delta | p (BH) |
|---|---|---|---|---|---|---|
| K562 SE vs outside | 1905 | 1943 | -5.210 | -5.182 | **-0.013** | 0.471 |
| HepG2 SE vs outside | 2211 | 1943 | -5.318 | -5.182 | **-0.032** | 0.142 |

Pre-registered MCID (claim.md, before this analysis ran): `|Cliff's delta| >= 0.2 AND
p_value_bh < 0.05`. **Neither comparison meets the p-value threshold, and both effect sizes
are an order of magnitude below the MCID** (0.013 and 0.032, versus a 0.2 threshold).

## Interpretation

No detectable difference in gnomAD population allele frequency between ClinVar VUS located
inside a super-enhancer (K562 or HepG2) and VUS located elsewhere in the genome. The direction
is consistent with the motivating hypothesis in both comparisons (SE-located VUS trend very
slightly rarer), but the effect is negligible and not statistically distinguishable from noise
even before applying the practical-significance bar.

This is a clean REJECT, not an ambiguous "significant but small" result like ARCHCODE's
Hypothesis C (synonymous codon optimality, `p<1e-6` but sub-MCID effect) -- here neither
criterion is met, at a comparable sample size (n~1900-2200 per group vs n~825-4988 there).
Genuinely no signal detected by this method, not just an underpowered one.

## What this does NOT mean

1. Does NOT mean regulatory variants are irrelevant to missing heritability -- only that THIS
   coarse test (any-super-enhancer-membership, K562/HepG2 dbSUPER calls, genome-wide VUS,
   population-frequency comparison) finds no signal.
2. Does NOT mean no individual VUS in a super-enhancer is functionally important -- a
   population-level null does not rule out specific, individually-important variants (the same
   logic ARCHCODE's BCL11A gnomAD follow-up used to flag a single candidate,
   `ARCHCODE/experiments/exp_bcl11a_enhancer_vus/decision.md`, even though this project's
   genome-wide test found nothing at the population level).
3. Does NOT test finer-grained regulatory annotation (specific enhancer-gene links, TF
   footprints, chromatin state beyond "in some super-enhancer or not") -- a coarser
   classification than e.g. ARCHCODE's enhancer-proximity work at named loci.
4. Only two cell lines' super-enhancer calls (K562, HepG2) -- a variant regulatory in a
   different, untested cell type would not be captured as "in-SE" here regardless of its true
   function.
5. AF=0 (absent from gnomAD) was treated as a real ICE category, floored at log10(AF)=-7, not
   imputed -- a different floor choice could shift results at the margin, though the effect
   sizes found are far too small for this to plausibly change the REJECT verdict.

## Recommendation

**REJECT.** Filed to `null_results/`. The "coarse SE-membership as a missing-heritability
proxy" approach does not work as tested. If this direction is revisited, a finer-grained
regulatory annotation (specific promoter-enhancer contact maps, not just SE membership) or a
trait-specific analysis (rather than pooling all ClinVar VUS regardless of associated
condition) would be needed -- both substantially larger undertakings than this experiment's
scope.
