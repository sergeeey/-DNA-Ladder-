---
experiment: exp_llps_promoter_vs_se_chip_evidence
date: 2026-07-08
verdict: "FINAL (2026-07-10): REJECT. Original SE-vs-whole-genome finding was an active-vs-inactive-chromatin artifact. BRD4 fails a matched control in both available cell lines (1.048, 0.809 -- reverses). MED1 splits 1-1 across the only two cell lines ENCODE has (1.788 K562, 0.733 HepG2 -- reverses) with no mechanistic explanation for the split. ENCODE has no further BRD4 or MED1 cell lines to test (both fully exhausted: BRD4 = 2 valid + 1 revoked; MED1 = 2 total, both used). Closed on this data source."
---

# Decision — Promoter vs. Super-Enhancer ChIP-seq Occupancy (BRD4/MED1, K562)

## Result

Primary test (2kb promoter window, pre-registered):

| Factor | n peaks | promoter-only | SE-only | density_promoter/kb | density_SE/kb | ratio | Classification |
|---|---|---|---|---|---|---|---|
| BRD4 | 4489 | 1953 | 933 | 0.0277 | 0.0670 | **0.414** | SE-favoring |
| MED1 | 325 | 74 | 28 | 0.0011 | 0.0020 | **0.523** | SE-favoring |
| POLR2A (baseline) | 25548 | 11900 | 2265 | 0.1689 | 0.1626 | 1.039 | No clear preference |

Pre-registered sensitivity check (5kb promoter window):

| Factor | ratio (2kb) | ratio (5kb) | Direction stable? |
|---|---|---|---|
| BRD4 | 0.414 | 0.177 | Yes -- same direction, stronger |
| MED1 | 0.523 | 0.287 | Yes -- same direction, stronger |
| POLR2A (baseline) | 1.039 | 0.501 | Shifts to SE-favoring at wider window -- expected for a broad-binding baseline, not treated as a primary result |

## Interpretation

The reformulated question (claim.md) asked whether static ChIP-seq co-occupancy of
condensate-associated coactivators independently supports a promoter-centric model (the
direction claimed by Bogdanović 2026 / Pandey 2026's live-cell imaging). **It does not — the
opposite pattern is observed, robustly.** Both BRD4 and MED1 show peak density 2-6x higher in
super-enhancer-only regions than in promoter-only regions, in K562, and this holds (gets
stronger, not weaker) under a 2.5x wider promoter-window sensitivity check.

This is a genuine, well-powered finding in the direction of the CLASSIC coactivator-condensate
model (Sabari et al. 2018, Boija et al. 2018 -- both in `Research Library/sources/llps-transcription/`)
rather than the newer 2026 promoter-centric imaging papers. It is NOT a failure to find
signal -- it is a positive result pointing the other way from what the reformulated hypothesis
anticipated.

## What this does NOT mean

1. Does NOT falsify Bogdanović 2026 / Pandey 2026 -- those are live-cell, single-molecule,
   dynamic measurements; this is population-averaged, static ChIP-seq. A real biological
   process can be genuinely promoter-centric in dynamic/live-cell terms while population-level
   ChIP-seq signal still concentrates more densely at super-enhancers -- these are not
   contradictory claims about the same measurement, they are different measurements
   (pre-registered as a possible outcome in claim.md's "What This Does NOT Mean" #3).
2. Does NOT establish LLPS/phase-separation as the mechanism -- ChIP-seq co-occupancy is
   consistent with LLPS, conventional high-affinity recruitment, or chromatin co-condensation
   alike (see `Research Library/evidence_matrices/llps-pol2-condensates.md`, "LLPS vs non-LLPS"
   table) -- this experiment cannot and does not distinguish between them.
3. Does NOT mean the promoter-only region class is "unimportant" -- BRD4/MED1 do occupy
   promoters at non-trivial density (0.0277/0.0011 peaks/kb respectively); the finding is about
   RELATIVE density between the two region classes, not absence at promoters.
4. Only tests K562, one cell line, one super-enhancer call set (dbSUPER), one promoter-window
   definition family (2kb/5kb). Generalization to other cell types or SE-calling methods is
   untested.

## Verification (2026-07-08, Agent(reviewer) pass before reporting)

Ran an independent logic review of `liftover.py`, `fetch_se_liftover_grch38.py`, and
`llps_promoter_vs_se_analysis.py` before treating this result as trustworthy (per
`audit-verification-gate.md`: no HIGH/MEDIUM claim reaches the user without tool-verified
evidence, and "orthogonal-method finding" is exactly such a claim).

- **Confirmed and fixed:** `liftover.py`'s reverse-strand coordinate formula was off by 1bp
  (`chain.q_size - (q_block_start + offset)` missing a `-1`), verified via a constructed
  synthetic chain. Fixed; the liftover and full analysis were **re-run from scratch** after
  the fix -- results identical to the pre-fix numbers above (BRD4 0.414, MED1 0.523, sensitivity
  0.177/0.287), consistent with the reviewer's assessment that a 1bp shift is immaterial at
  kb-scale SE regions.
- **Confirmed correct (fuzz-tested):** `subtract_intervals` (the trickiest function -- computing
  "promoter-only"/"SE-only" region space) was fuzz-tested against a brute-force bitmap
  reference, 2000 randomized trials, 0 failures (no negative-length intervals, no
  out-of-bounds, no dropped/duplicated bp).
- **Evidence gap closed:** the reviewer flagged that dbSUPER's K562 super-enhancer calls
  needed to be confirmed independent of the BRD4/MED1 signal being tested against them
  (otherwise the "orthogonal method" framing would be partly circular). Verified via
  WebSearch, 2026-07-08: dbSUPER calls super-enhancers from **H3K27ac ChIP-seq** (histone
  mark, MACS peak calling + ROSE stitching/ranking), not from BRD4/MED1/Mediator ChIP-seq.
  The comparison IS genuinely independent -- H3K27ac and BRD4/MED1 are different assays
  measuring different molecules.

## Follow-up (2026-07-08, same day): HepG2 replication

Tested generalization in a second cell line, addressing the single-cell-line limitation noted
below. See `experiments/exp_llps_promoter_vs_se_hepg2_replication/decision.md`: **MED1
replicates cleanly** (SE-favoring in both K562 and HepG2, both windows); **BRD4 replicates the
direction but not the pre-registered magnitude threshold** in HepG2 at the primary window
(0.764 vs 0.414 in K562), though it does clear the threshold at the wider window. Read this
K562 BRD4 finding as robust-in-K562 rather than a fully general BRD4 property until a 3rd cell
line is tested.

## Matched-control follow-up (2026-07-10): original finding substantially weakened

An external methodological review (pasted into the session, formatted as an AI-generated
critique) argued the original comparator ("SE-only" vs "the rest of the genome") was too
weak a test: the genome outside SE/promoters is mostly inactive/heterochromatic DNA where
BRD4/MED1 trivially show near-zero signal, so "SE beats whole genome" could be driven by
"active chromatin beats inactive chromatin" rather than anything specific to super-enhancers.

The critique also raised a specific circularity concern (dbSUPER's SE calls being derived
from MED1 itself). That specific claim was checked and did NOT hold up:
`[VERIFIED-webfetch+websearch, 2026-07-10]` dbSUPER's inclusion criterion is H3K27ac ChIP-seq
for every cell line in the database ("a sample... is contained in the database if
super-enhancers were successfully identified... by H3K27ac ChIP-seq"), not MED1/BRD4 -- the
critique's proposed *mechanism* was wrong. But the underlying *concern* (the comparator is
too weak / not appropriately matched) was directionally right, and BRD4 in particular has a
real, independent reason to correlate with H3K27ac: BRD4's bromodomains directly bind
acetyl-lysine, so BRD4-H3K27ac colocalization is partly expected on biochemical grounds,
independent of any circularity in how regions were labeled.

**Test run:** fetched real ENCODE H3K27ac ChIP-seq peaks (GRCh38, K562 `ENCFF038DDS`, HepG2
`ENCFF012ADZ`) and redefined "typical enhancer" (TE) as H3K27ac-marked space minus
super-enhancer space (same interval-math functions, `scripts/llps_matched_control_analysis.py`).
Re-ran the density comparison as SE vs TE instead of SE vs whole-genome:

| Cell line | Factor | ratio vs whole genome (original) | ratio vs matched H3K27ac typical-enhancer (new) | Survives matched control? |
|---|---|---|---|---|
| K562 | BRD4 | 0.414 (SE-favoring) | **1.048** (no difference) | **No** |
| K562 | MED1 | 0.523 (SE-favoring) | **1.788** (SE-favoring) | **Yes** |
| HepG2 | BRD4 | 0.764 (weak/no pref.) | **0.809** (typical-enhancer-favoring) | **No, reverses** |
| HepG2 | MED1 | 0.558 (SE-favoring) | **0.733** (typical-enhancer-favoring) | **No, reverses** |

(Ratio here is SE-density / typical-enhancer-density; >1 = still SE-favoring after matching,
~1 = no real preference, <1 = reverses to favor typical enhancers.)

**Honest re-interpretation:** the original "BRD4/MED1 favor super-enhancers" headline finding
does NOT hold up as a general, robust result once compared against a fair, activity-matched
control. BRD4 shows no real SE-preference in either cell line once matched -- consistent with
the H3K27ac-binding-mechanism explanation above. MED1 shows a genuine, sizeable SE-preference
in K562 (1.788, the strongest signal in this whole follow-up) but that **reverses** in HepG2
(0.733) -- the opposite of "replication," this is now a real cell-type-dependent
inconsistency for MED1, not a confirmed general property either.

**Revised overall verdict: REPEAT, not PROMOTE.** Most of the original signal was an artifact
of comparing active to inactive chromatin, not a genuine super-enhancer-specific effect. The
one surviving, non-trivial signal (K562 MED1 vs matched typical enhancers) is not itself
replicated in HepG2 and would need a 3rd cell line and a real explanation for the K562/HepG2
divergence before being reported as a finding on its own.

**Process note:** this is the second time this session a positive result was substantially
walked back after surviving its first round of scrutiny but failing a stronger, later test
(see also ARCHCODE's GATA1 "pearl," `ARCHCODE/null_results/20260702-enhancer-proximity-replication.md`)
-- consistent with this project's standing rule that a single-round positive result is
provisional until it survives an adversarial re-check with a genuinely fair comparator, not
just a sensitivity check on the same weak comparator.

## FINAL closure (2026-07-10): data source exhausted, verdict REJECT

Checked whether a 3rd cell line could resolve the K562/HepG2 MED1 split, or give BRD4 another
chance, before closing this out. `[VERIFIED-bash]`, ENCODE REST API, full enumeration (not a
filtered search that could silently miss records):

- **BRD4, all cell lines, all statuses:** 4 experiments total. K562 (`ENCSR583ACG`, released),
  HepG2 (`ENCSR395MHA` + `ENCSR514EOE`, released) -- both already used -- and H1 embryonic stem
  cells (`ENCSR815RMQ`), which is **`status: revoked`** (ENCODE's own audit flags a platform/
  control incompatibility -- not usable, and using it anyway would repeat the exact
  "force a weak data source" mistake already avoided once today with the G4-seq direction).
- **MED1, all cell lines, all statuses:** 2 experiments total, K562 and HepG2 -- both already
  used. No 3rd entry exists at all, valid or otherwise.

**ENCODE has no further data to test either factor.** This is not "we stopped looking" -- it
is a complete enumeration of the only public, curated, standardly-processed source used
throughout this project. Going further would mean GEO (independent studies, non-ENCODE QC
pipeline, not directly comparable without substantial extra validation work) -- out of scope
for closing out this specific experiment.

**Final verdict: REJECT.** The original claim ("BRD4/MED1 ChIP-seq occupancy favors
super-enhancers over comparable active chromatin") is not supported:
- BRD4: fails the matched control in both available cell lines (no preference in K562,
  reverses in HepG2). Consistent non-finding, closed.
- MED1: splits exactly 1-for-1 across the only two cell lines that exist (favors SE in K562,
  reverses in HepG2), with no mechanistic account for the split and no further data to
  adjudicate it. An unresolved, non-replicating split is not evidence for the original claim
  either -- filed as REJECT, not left open-ended.

This experiment (and its HepG2 replication companion) are now closed. Filed to
`null_results/` -- the original claim this experiment's whole chain was built to test did not
survive.

## Caveats / limitations

- **Go/No-Go criterion gap:** claim.md pre-registered a per-factor MCID classification (>=1.5
  promoter-favoring / <=0.67 SE-favoring / between = no preference) but did not pre-register an
  aggregate PROMOTE/REPEAT/REJECT verdict term for the overall experiment, since the L0
  question type is Descriptive, not a strict single hypothesis test. Noted here as an honest
  process gap, not silently patched after seeing results -- the per-factor classification
  itself WAS fully pre-registered and is what's reported above.
- dbSUPER's K562 super-enhancer calls were lifted from hg19 to GRCh38 via this repo's own
  from-scratch UCSC-chain liftOver (`scripts/liftover.py`) -- sanity-checked against a known
  coordinate (NOC2L TSS, matched GENCODE's native GRCh38 annotation to within 10bp) but 4/742
  (0.5%) super-enhancers failed to lift (fell in a chain gap) and were dropped, not imputed.
- Peak calling, cell-line passage, and antibody differences between the BRD4/MED1/POLR2A
  ENCODE experiments are not controlled for (different experiments, different labs' standard
  ENCODE pipeline runs) -- a known source of between-factor noise not addressed here.

## Recommendation (superseded 2026-07-10 -- see "Matched-control follow-up" above)

~~This is a real, reportable, orthogonal-method finding: genomic ChIP-seq occupancy of
BRD4/MED1 in K562 favors super-enhancers over promoters, robust to a promoter-window
sensitivity check.~~ **This conclusion does not survive a matched (H3K27ac-active) control and
should not be cited as-is.**

**Current recommendation:** REPEAT, not PROMOTE. Do not report "BRD4/MED1 favor
super-enhancers" as a standalone finding from this experiment. The one component that survives
a fair comparator (K562 MED1, ratio 1.788 vs matched typical enhancers) is itself
inconsistent between cell lines (reverses to 0.733 in HepG2) and would need a 3rd cell line
plus a mechanistic explanation for the divergence before being reportable on its own. This
experiment's main surviving value is methodological: it demonstrates why "vs whole genome" is
too weak a comparator for ChIP-seq enrichment claims, and the matched-control code
(`scripts/llps_matched_control_analysis.py`) is reusable for future experiments in this
project.
