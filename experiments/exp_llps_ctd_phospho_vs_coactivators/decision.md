---
experiment: exp_llps_ctd_phospho_vs_coactivators
date: 2026-07-08
verdict: INCONCLUSIVE / window-sensitive — Ser5P does NOT show a stable contrast with BRD4/MED1's robust SE-favoring pattern
---

# Decision — Pol II-Ser5P vs. Coactivators, Promoter/SE Density Ratio

## Result

| Factor | ratio (2kb) | Classification (2kb) | ratio (5kb) | Classification (5kb) | Stable across windows? |
|---|---|---|---|---|---|
| BRD4 | 0.414 | SE-favoring | 0.177 | SE-favoring | **Yes** |
| MED1 | 0.523 | SE-favoring | 0.287 | SE-favoring | **Yes** |
| POLR2A (total) | 1.039 | No clear preference | 0.501 | SE-favoring | No |
| POLR2A-Ser5P | 0.841 | No clear preference | 0.456 | SE-favoring | No |

## Interpretation

The reformulated question asked whether Pol II-Ser5P shows a promoter-favoring density ratio,
contrasting with BRD4/MED1's already-established, window-stable SE-favoring pattern (see
`experiments/exp_llps_promoter_vs_se_chip_evidence/decision.md`). **It does not show a clean
contrast.** At the primary 2kb window, Ser5P lands in the "no clear preference" band (0.841,
between 0.67 and 1.5) -- not promoter-favoring as the well-established initiation-marking role
of Ser5P might suggest, and not matching BRD4/MED1's SE-favoring pattern either. At the 5kb
sensitivity window, Ser5P's ratio drops to 0.456, crossing into "SE-favoring" -- the same
window-shift also happens to total POLR2A (1.039 -> 0.501), but NOT to BRD4/MED1, which stay
robustly SE-favoring at both windows.

This asymmetry is itself the finding: BRD4/MED1's SE-favoring pattern (experiment 1) is robust
to the promoter-window definition; Pol II's pattern (both total and Ser5P-specific) is NOT
robust to it. The most likely explanation is methodological, not biological: Pol II/Ser5P ChIP-
seq signal is known to extend into the early gene body beyond a tight TSS window (consistent
with the established biology cited in claim.md's Novelty Check -- Ser5P persists briefly past
the exact TSS before transitioning to Ser2P), so a fixed-width promoter window is a
poorer-fitting classification boundary for Pol II-associated marks than for BRD4/MED1, which
are more sharply peak-like at regulatory elements.

## What this does NOT mean

1. Does NOT mean Ser5P is not promoter-associated -- the established literature (cited in
   claim.md) is not in question; this experiment's WINDOW-BASED classification method is
   simply not well-suited to cleanly separate Pol II-associated marks by this criterion.
2. Does NOT weaken experiment 1's BRD4/MED1 finding -- that result's robustness to the exact
   same window-sensitivity test (unchanged direction, strengthened effect) is, if anything,
   reinforced by contrast: the method DOES detect real signal when the underlying biology is a
   good fit for it (sharp coactivator peaks), and DOES show its own limits when it isn't (broad
   Pol II occupancy).
3. Does NOT test or confirm the CTD-phosphorylation-switch mechanism (Guo 2019/Linhartova 2024)
   -- this experiment neither supports nor refutes that mechanism; it simply found this
   particular ChIP-seq-based method isn't well-suited to detect it, if present.

## Recommendation

**INCONCLUSIVE per this method** -- not filed as a REJECT of the underlying biology (which
this experiment never had the power to test cleanly), but as a documented methodological
limitation: fixed-width TSS windows are not a robust classification boundary for Pol II-
associated ChIP-seq marks in this density-ratio framework. If revisited, a gene-body-aware
window (e.g. TSS to TSS+1kb for "initiation zone" vs. TSS+1kb to TES for "elongation zone",
rather than a symmetric +-N bp window) would better match the known biology and is a concrete,
specific next step -- not attempted here to keep this experiment's scope matched to reusing
experiment 1's existing region-classification code without modification.
