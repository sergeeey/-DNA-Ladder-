---
experiment: exp_llps_promoter_vs_se_hepg2_replication
date: 2026-07-08
verdict: PARTIAL REPLICATION — MED1 replicates cleanly, BRD4 does not clear the primary-window MCID threshold (trends correctly, clears it at wider window)
---

# Decision — HepG2 Replication of Promoter/SE Density Ratio

## Result

| Factor | K562 ratio (2kb) | HepG2 ratio (2kb) | HepG2 classification (2kb) | HepG2 ratio (5kb) | HepG2 classification (5kb) |
|---|---|---|---|---|---|
| BRD4 | 0.414 (SE-favoring) | **0.764** | No clear preference | 0.342 | SE-favoring |
| MED1 | 0.523 (SE-favoring) | **0.558** | SE-favoring | 0.291 | SE-favoring |
| POLR2A | 1.039 (no preference) | 0.991 | No clear preference | 0.542 | SE-favoring |

Pre-registered replication criterion (claim.md): "replicates" requires BOTH BRD4 and MED1
SE-favoring (<=0.67) at the primary 2kb window AND direction unchanged at 5kb.

## Interpretation

**MED1 replicates cleanly**: SE-favoring at both windows in HepG2 (0.558, 0.291), consistent
with K562 (0.523). **BRD4 does not meet the pre-registered replication criterion at the
primary window**: 0.764 in HepG2 falls in the "no clear preference" band, versus 0.414
(SE-favoring) in K562 — a real, honest miss against the criterion set before running this.
BRD4 does cross into SE-favoring at the wider 5kb window (0.342) and its ratio is still below
1.0 (leaning SE-ward) even at 2kb, so the *direction* is consistent but the *effect size* is
weaker and window-dependent in HepG2 in a way it was not in K562.

This is reported as **PARTIAL replication**, not full and not failed. Per this project's own
discipline (do not round an ambiguous result up to a clean positive), BRD4's K562 finding
should now be read as "robust in K562, weaker and less window-stable in HepG2" rather than
"a general BRD4 property" -- exactly the kind of nuance the first experiment's own
"generalization untested" caveat anticipated.

## What this does NOT mean

1. Does NOT mean the K562 BRD4 finding was wrong -- both cell lines show peaks trending toward
   SE over promoter density; HepG2 just doesn't clear the same strict, pre-registered threshold
   at the tighter window.
2. Does NOT establish a mechanistic reason for the K562/HepG2 difference -- could be biological
   (different chromatin landscapes, different roles for BRD4 in erythroleukemia vs.
   hepatocellular carcinoma biology) or technical (different antibody lots, different ENCODE
   processing batches/labs for the two cell lines' experiments) -- not distinguished here.
3. MED1's clean replication does NOT mean MED1 and BRD4 necessarily share an identical
   mechanism -- they are measured by separate ChIP-seq experiments and could diverge for
   independent reasons.

## Recommendation

**PARTIAL REPLICATION.** Update the overall project finding: the SE-favoring promoter/SE
density pattern for coactivator ChIP-seq occupancy generalizes cleanly for MED1 across two
cell lines (K562, HepG2), but for BRD4 is directionally consistent while being weaker and more
window-sensitive outside K562. Worth a 3rd cell line before drawing a general conclusion about
BRD4 specifically; MED1's two-line replication is already reasonably strong standalone
evidence for that factor.
