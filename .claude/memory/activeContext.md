# Active Context — DNA Ladder

**Last Updated:** 2026-07-10
**Branch:** master (bootstrap merged from feature/bootstrap, commit 5b97b78)
**Sibling projects:** `Research Library` (D:\Research Library\, literature/citations, git
initialized, 2 commits) and `ARCHCODE` (C:\Users\sboi\ARCHCODE_review\, methodology source,
consult for known bug classes before re-deriving).

## DONE (2026-07-08) — Project bootstrap + first experiment design

Spun off from an ARCHCODE session after the user pasted an external 80-source LLPS/Pol-II-
condensates literature review. Set up:
1. `Research Library` — 15 of the report's "must-read" sources independently re-verified via
   CrossRef (not trusted blind from the pasted report — 2 needed a WebSearch fallback since
   CrossRef bibliographic search missed them despite being real: Boija 2018, Mukherjee 2026,
   Linhartova 2024). Reviewer agent caught 3 real bugs in the verification tooling
   (BibTeX key collisions across topics, silent author-list parsing failure, unguarded
   CrossRef title-list indexing) — all fixed and re-verified, commit c1705a7.
2. `DNA Ladder` (this project) — CLAUDE.md, RESEARCH_DIRECTIONS.md (8-direction backlog),
   null_results/INDEX.md skeleton.
3. First experiment: `experiments/exp_llps_promoter_vs_se_chip_evidence/claim.md` — L0 gate
   (Descriptive) + mandatory Novelty Check run BEFORE any data work. Found the report's
   "Hypothesis A" (promoter-centric > super-enhancer-centric Pol II condensates) is NOT novel
   -- it's literally what Bogdanović 2026 and Pandey 2026 (both verified real via CrossRef)
   already claim, via live-cell imaging this project can't replicate. Reformulated to an
   honest, complementary question: do static ChIP-seq co-occupancy patterns (genomics, not
   imaging) independently support the same model?

**Data availability confirmed (ENCODE REST API, `[VERIFIED-bash]`):** BRD4 (`ENCSR583ACG`),
MED1 (`ENCSR269BSA`), POLR2A (10 experiments; `ENCSR031TFS`/`ENCSR388QZF` untreated baseline
candidates), POLR2A-phosphoS5 (`ENCSR000BKR`, bonus -- directly relevant to the CTD-
phosphorylation-switch mechanism) all exist for K562.

## NOT yet done (pick up here next session)

1. Source or derive a super-enhancer call set for K562 (dbSUPER, or ROSE from ARCHCODE's
   already-cached H3K27ac data -- CHECK GENOME BUILD MATCH FIRST, hg19 vs hg38, before reusing
   anything from ARCHCODE; this exact bug class bit ARCHCODE multiple times this session).
2. Finalize L1 estimand summary measure + MCID (currently "not yet finalized" in claim.md) --
   must be pre-registered BEFORE fetching peak data, not after.
3. Fetch actual ENCODE peak files (bigBed/narrowPeak) for the 4 confirmed accessions.
4. Define promoter-proximal windows via GENCODE TSS annotations (reuse ARCHCODE's
   `fetch_gencode_hg19_stranded.py` pattern if build matches, else re-derive for the right
   build).
5. Compute co-occupancy/enrichment stats (Mann-Whitney U / Cliff's delta / BH correction --
   reuse ARCHCODE's from-scratch implementations, same pattern as
   `ARCHCODE/scripts/synonymous_codon_optimality_analysis.py`).
6. Write decision.md with an honest PROMOTE/REPEAT/REJECT verdict per pre-registered MCID.

**UPDATE 2026-07-08, later same day: experiment COMPLETE.** All 6 "NOT yet done" steps above
finished: sourced dbSUPER K562 super-enhancers (H3K27ac-derived, confirmed independent of
BRD4/MED1 signal via WebSearch), lifted hg19->GRCh38 via a from-scratch UCSC-chain liftover
(`scripts/liftover.py`), fetched real ENCODE BRD4/MED1/POLR2A GRCh38 peaks + GENCODE v47
native GRCh38 TSS, pre-registered summary measure (promoter/SE peak-density ratio) + MCID
before running `scripts/llps_promoter_vs_se_analysis.py`.

**Result: BRD4 ratio=0.414, MED1 ratio=0.523 -- both SE-favoring** (opposite direction from
the reformulated question, i.e. static ChIP-seq occupancy does NOT independently corroborate
the 2026 promoter-centric imaging papers; it favors the classic Sabari/Boija super-enhancer
model instead). Robust to a pre-registered 5kb-window sensitivity check. Agent(reviewer) caught
and fixed one real off-by-one bug in the liftover's reverse-strand branch (immaterial to the
result at kb-scale, re-ran from scratch to confirm) and flagged one evidence gap (dbSUPER's
independence from BRD4/MED1) which was then verified true via WebSearch. Full writeup:
`experiments/exp_llps_promoter_vs_se_chip_evidence/decision.md`.

Not filed to `null_results/` -- this is a completed, informative positive result (real
SE-favoring effect found), not a rejected hypothesis.

## Research backlog (not started)

See `RESEARCH_DIRECTIONS.md` — 7 more candidate directions beyond LLPS (non-coding DNA
function, dark transcriptome, centromeric DNA, transgenerational epigenetics, non-B DNA
structures, missing heritability/regulatory variants). Not prioritized.

## DONE (2026-07-08) — Second experiment: exp_llps_ctd_phospho_vs_coactivators, INCONCLUSIVE

Extended experiment 1's promoter/SE density-ratio method to a 4th factor, Pol II-Ser5P
(`ENCSR000BKR`/`ENCFF053XYZ`, GRCh38, K562). Novelty Check found the base fact ("Ser5P marks
initiation, is promoter-proximal") is decades-old established biology, NOT novel -- reformulated
to a within-project comparative extension: does Ser5P show a promoter-favoring ratio,
contrasting with BRD4/MED1's already-robust SE-favoring pattern?

**Result: INCONCLUSIVE / window-sensitive.** Ser5P ratio = 0.841 (2kb, no clear preference) vs
0.456 (5kb, SE-favoring) -- not stable across window sizes, unlike BRD4/MED1 which stayed
SE-favoring at both. Total POLR2A shows the same window-instability (1.039 -> 0.501). Read as a
methodological finding: fixed-width TSS windows don't cleanly classify broadly-distributed
Pol II-associated marks the way they do sharp coactivator peaks -- and BRD4/MED1's robustness
to the same test is, by contrast, reinforced, not undermined. Full writeup:
`experiments/exp_llps_ctd_phospho_vs_coactivators/decision.md`.

**Process note:** running the shared `llps_promoter_vs_se_analysis.py` script directly with a
4th factor added would have silently overwritten experiment 1's already-decided results.json --
caught this before committing, reverted the shared script to its original 3-factor state, and
wrote a separate `scripts/llps_ctd_phospho_analysis.py` that imports and reuses the shared
functions without mutating the first experiment's frozen output.

## DONE (2026-07-08) — Item A: HepG2 replication (PARTIAL) + Item B: permanent interval-math tests

User asked to do all 3 previously-proposed next steps in order (A: generalize to a 2nd cell
line, B: add tests for the reviewer-flagged interval-math code, C: new research direction).

**A — HepG2 replication:** reused experiment 1's exact method (2kb/5kb promoter windows,
dbSUPER-derived SE calls lifted to GRCh38, same code) on HepG2 BRD4/MED1/POLR2A ChIP-seq.
**MED1 replicates cleanly** (ratio 0.558/0.291, SE-favoring at both windows, consistent with
K562's 0.523). **BRD4 does NOT clear the pre-registered replication criterion at the primary
2kb window** (0.764, "no clear preference" vs K562's 0.414 SE-favoring), though it trends the
same direction and clears SE-favoring at the wider 5kb window. Filed honestly as PARTIAL
REPLICATION, not rounded up to a clean positive. Cross-referenced in both experiments'
decision.md files. Full writeup:
`experiments/exp_llps_promoter_vs_se_hepg2_replication/decision.md`.

**B — permanent tests:** `tests/verify_interval_math.py` (stdlib `unittest`, 20 tests, all
passing) covers `merge_intervals`/`subtract_intervals`/`point_in_intervals` (including the
reviewer's 500-trial fuzz test against a brute-force bitmap reference, now committed instead
of re-derived each session) and a regression test for the confirmed-and-fixed liftover
reverse-strand off-by-one bug.

**C — missing heritability / VUS-in-super-enhancer frequency (2026-07-08, same day):**
G4-seq (non-B DNA) parked (21GB raw data only, impractical). Pivoted to backlog item 8:
does gnomAD population frequency differ between ClinVar VUS inside vs outside super-enhancers
(K562/HepG2, reusing already-fetched SE calls)? L0 gate + Novelty Check done (WebSearch
confirmed the general "population frequency informs interpretation" principle is established,
but this specific SE-stratified genome-wide test was not found in the literature). Data
feasibility confirmed live (ClinVar GRCh38 rows exist, gnomAD v4 GraphQL API reachable) before
building anything.

Fetched 2,254,079 genome-wide ClinVar VUS (GRCh38); 25,726 in K562 SE, 9,537 in HepG2 SE.
Pre-registered (before touching AF data) a subsample cap of 3,000 per group (fixed seed=42)
for gnomAD API tractability. Ran Mann-Whitney U + Cliff's delta on log10(AF), AF=0 (absent
from gnomAD) treated as a real ICE category (floored at log10=-7, not imputed).

**Result: REJECT.** K562-SE vs outside: Cliff's delta=-0.013, p_bh=0.47. HepG2-SE vs outside:
Cliff's delta=-0.032, p_bh=0.14. Neither meets the pre-registered MCID (|delta|>=0.2 AND
p_bh<0.05) -- unlike ARCHCODE's Hypothesis C (significant p but sub-MCID effect), here there
is no signal at all, not even a marginal one. Filed to
`null_results/20260708-heritability-vus-se-frequency.md`. Full writeup:
`experiments/exp_heritability_vus_se_frequency/decision.md`.

**Note:** the 372MB genome-wide ClinVar VUS fetch (`data/input/clinvar_vus_grch38_se_classified.json`)
is NOT committed (too large, same discipline as ARCHCODE's large raw fetches) -- reproducible
via `scripts/fetch_clinvar_vus_grch38.py`. The much smaller gnomAD AF cache (~320KB) IS
committed for reproducibility.

## MAJOR REVISION (2026-07-10) — exp_llps_promoter_vs_se_chip_evidence weakened after matched-control follow-up

An external methodological critique (pasted into the session) argued the original "SE vs whole
genome" comparator was too weak (whole genome includes inactive DNA where BRD4/MED1 trivially
show near-zero signal). Checked the critique's specific circularity claim (dbSUPER SE calls
derived from MED1) -- did NOT hold up, `[VERIFIED-webfetch+websearch]` dbSUPER uses H3K27ac for
every cell line, not MED1/BRD4. But the general concern was directionally right.

Fetched real ENCODE H3K27ac peaks (K562 `ENCFF038DDS`, HepG2 `ENCFF012ADZ`) and re-ran the
density comparison as SE vs "typical enhancer" (H3K27ac-marked, not-super) instead of vs whole
genome (`scripts/llps_matched_control_analysis.py`). Result: **BRD4 shows no real SE-preference
in either cell line once matched** (K562 ratio 1.048, HepG2 0.809 -- reverses); **MED1 survives
in K562 (1.788) but reverses in HepG2 (0.733)**. The original "SE-favoring, robust across cell
lines" headline does not hold up. Revised verdict for
`experiments/exp_llps_promoter_vs_se_chip_evidence`: **REPEAT, not PROMOTE** -- both `claim.md`
and `decision.md` updated in place with the full honest timeline preserved (original result not
deleted, marked superseded), matching this project's standing rule (see ARCHCODE's GATA1 pearl
precedent) that a positive result is provisional until it survives a genuinely fair comparator,
not just a sensitivity check on the same weak one. `exp_llps_promoter_vs_se_hepg2_replication`'s
decision.md cross-referenced with the same caveat (its own "vs whole genome" framing wasn't
re-tested with a matched control).

## FINAL CLOSURE (2026-07-10) — exp_llps_promoter_vs_se_chip_evidence: REJECT, data exhausted

User asked to check BRD4/MED1 in a 3rd cell line before finalizing. `[VERIFIED-bash]` full
ENCODE enumeration (not a filtered search): BRD4 has only 4 experiments total across ALL cell
lines/statuses -- K562 and HepG2 (both already used) plus one H1-hESC entry
(`ENCSR815RMQ`) that is `status: revoked` (ENCODE's own audit: platform/control
incompatibility) -- not usable. MED1 has only 2 experiments total, period -- K562 and HepG2,
both already used. No 3rd cell line exists for either factor; this is a complete data-source
enumeration, not a stopped search.

**Final verdict: REJECT.** BRD4 fails the matched control in both available cell lines
(no preference in K562, reverses in HepG2). MED1 splits exactly 1-for-1 (favors SE in K562,
reverses in HepG2) with no mechanistic explanation and no further ENCODE data to adjudicate --
an unresolved split does not count as supporting evidence either. `claim.md`/`decision.md`
updated with a "FINAL closure" section; filed to
`null_results/20260710-llps-promoter-vs-se-chip-evidence.md`. HepG2 replication experiment's
`claim.md` marked superseded (its parent claim no longer stands).

**This closes out the entire exp_llps_promoter_vs_se_chip_evidence thread** (original result,
HepG2 replication, matched-control follow-up, 3rd-cell-line check) -- net result across all of
today's LLPS work: 0 confirmed positive findings once matched controls were applied, 1
inconclusive (Ser5P), 3 REJECT (this one, its two sub-checks folded in, plus the missing-
heritability VUS test). Ready to move to a new direction.

## DONE (2026-07-10, later) — Gnocchi constraint replication of missing-heritability direction, REJECT

Ran `boyko-specialist` a second time this session, targeted at replacing ClinVar as the
data source for the "missing heritability" direction (ClinVar carries real, WebSearch-verified
ascertainment/gene-panel/submission bias). Found Gnocchi -- Chen/Francioli/Karczewski 2023,
*Nature*, DOI 10.1038/s41586-023-06045-0 -- a genome-wide GRCh38 germline mutational-constraint
map built from 76,156 gnomAD v3.1.2 genomes, zero ClinVar dependency. Located and downloaded the
real public data (`gs://gnomad-nc-constraint-v31-paper/download_files/`, 1,984,900 QC-passed
1kb-window Z-scores, row count cross-verified against the paper's own README).

User pasted an external methodological critique of the naive "intersect windows + Mann-Whitney"
design before it was built -- it correctly flagged (1) unresolved novelty vs. the original
paper's own analyses, (2) K562/HepG2 are cancer lines so a positive result can't be read as
"cell-type-specific selection" (Gnocchi is germline), (3) pooling correlated adjacent 1kb windows
pseudoreplicates. Addressed all three in the design: Gate-0 novelty check (inconclusive --
[UNKNOWN], not confirmed either way, paywalled supplementary not searchable), limitation stated
in claim.md before running (not after), and region-level length-weighted-mean Z per enhancer
(not per-window) as the unit of analysis, with a paired-permutation test (10k perms) as the
primary significance measure instead of relying on Mann-Whitney's independence assumption.

**Result: REJECT.** Cliff's delta +0.051 (K562) vs -0.044 (HepG2) -- sign flips between cell
lines, same red flag that killed BRD4/MED1 earlier today, both far below the pre-registered
MCID (0.2). Wrote 17 unit tests for the new region-aggregation/matching logic after a
commit-test-gate hook correctly caught that the first commit shipped untested new numerical
code -- all pass, confirms the weighted-mean and permutation-test math is doing what it claims.
Filed to `null_results/20260710-gnocchi-constraint-se-vs-typical-enhancer.md`. This is the
**third independent null** on SE-vs-typical-enhancer across two unrelated data sources (ClinVar,
gnomAD constraint) -- recommend closing this direction rather than seeking a fourth data source.

## DONE (2026-07-10, later still) — Positive control + heritability v2 completion: direction formally closed

User asked to run a positive control before trusting the Gnocchi REJECT (own idea, matching
this session's falsification-first discipline). Reused the exact `weighted_mean_z` /
`mann_whitney_u` / `paired_permutation_test` code, unmodified, on CDS exons (GENCODE v47
basic, GRCh38) vs. length-matched regions >=100kb from any TSS. Result: Cliff's delta
**+0.609** (~12x the MCID), p at the permutation floor, correctly signed -- confirms the
pipeline detects large real effects, so the SE-vs-typical null is trustworthy, not a
broken-pipeline artifact. 6 new unit tests for the sampling logic (`far_from_any_tss`), all
pass. Added as a section to `exp_gnocchi_constraint_se_vs_typical_enhancer/decision.md`.

Shortly after, the long-running `exp_heritability_vus_se_vs_typical_enhancer` background job
(ClinVar VUS-in-SE vs VUS-in-typical-enhancer, matched control, started earlier this session)
completed: Cliff's delta +0.008 (K562) / -0.019 (HepG2) -- essentially zero, the cleanest null
of the three. Filed to `null_results/20260710-heritability-vus-se-vs-typical-enhancer.md`.

**Missing-heritability direction now formally closed**: 3 estimands (ClinVar-vs-everywhere,
ClinVar-vs-matched-typical, Gnocchi-constraint-vs-matched-typical), 2 independent data
sources, 1 validated pipeline, all converge on no meaningful SE-specific effect. All 43 unit
tests across the 3 test files pass. Next direction not yet chosen -- candidate from earlier
discussion: non-B DNA (G-quadruplex/R-loop) using processed datasets instead of the 21GB raw
FASTQ that parked this direction on 2026-07-08.

## DONE (2026-07-10, later still) — R-loop direction opened and closed same day: exp_rloop_se_vs_typical_enhancer, REJECT

User confirmed the missing-heritability meta-conclusion framing (positive biological
hypotheses failed, but the pipeline validity + convergent-null finding is itself the
real result) and asked to pursue R-loop next via `boyko-specialist`. Re-search (not
first search) found RLBase (Miller/Chedin/Bishop 2023, NAR, PMID 36039757) -- falsifies
the 2026-07-08 premise that only 21GB raw data existed, but only for R-loops, not G4
(G4 processed-file search stayed [UNKNOWN]). Verified directly via public S3 JSON API
(`s3://rlbase-data/`): 75 K562 R-loop samples, small `hg38 broadPeak` files (76KB-11MB).

User said "го" -- resolved GSM1720619 (canonical Sanz/Chedin 2016 K562 DRIP-seq) to
SRX1070682 via NCBI eutils, downloaded the real processed peak file (44,753 peaks),
built `scripts/rloop_se_vs_typical_analysis.py` reusing the already-tested SE/typical
classification, length-matching, and permutation-test code from the Gnocchi experiment
-- new logic was only `overlap_fraction`.

**Result: REJECT.** Cliff's delta -0.042 (wrong-for-hypothesis direction -- typical
enhancers show marginally MORE R-loop overlap than SE), permutation p at the test floor
but driven by n=5993 pairs, not effect size -- same significant-by-sample-size pattern
as several nulls this session. Literature suggested SE might show more R-loop/RNA
signal; this matched-comparator test does not reproduce that direction.

**Caught a real latent bug before trusting the result**: wrote 10 unit tests for
`overlap_fraction` first, one deliberately tested double-counting from overlapping
input peaks -- failed (1.2 instead of clamped 1.0). Real R-loop data happened to have
non-overlapping peaks already (result was numerically unaffected), but fixed properly
via `merge_intervals` reuse (already-tested code from the LLPS experiment) plus a
defensive clamp, not just patched to pass the test. All 53 tests across 4 test files
pass. R-loop direction opened and closed in the same session -- consistent with this
session's pattern that "obvious" SE-associated claims do not survive matched controls.

## Auto-commit log
- [2026-07-10 17:52] `bd5d40e`: docs: activeContext narrative for R-loop direction (opened and closed same day)
- [2026-07-10 17:45] `8a61059`: feat: exp_rloop_se_vs_typical_enhancer -- REJECT, opens and closes R-loop direction same day
- [2026-07-10 17:36] `2494764`: docs: auto-log sync
- [2026-07-10 17:36] `8dd395f`: docs: sync activeContext + commit small reference data files
- [2026-07-10 17:30] `39caa00`: docs: auto-log sync
- [2026-07-10 17:30] `6b4fa28`: docs: meta-conclusion for missing-heritability direction closure
- [2026-07-10 17:18] `e6aa1c2`: docs: activeContext narrative for positive control + heritability v2 closure
- [2026-07-10 17:02] `299c913`: feat: exp_heritability_vus_se_vs_typical_enhancer -- REJECT, third convergent null closes direction
- [2026-07-10 16:57] `6784f5c`: docs: auto-log sync
- [2026-07-10 16:56] `5903d30`: test: positive control validates Gnocchi pipeline on known coding-vs-intergenic effect
- [2026-07-10 16:47] `cfcb981`: docs: auto-log sync 2
- [2026-07-10 16:46] `46cecde`: docs: auto-log sync
- [2026-07-10 16:46] `1f427ac`: docs: activeContext narrative for Gnocchi constraint replication (REJECT)
- [2026-07-10 16:44] `9c459db`: fix: remove unused import in gnocchi test file
- [2026-07-10 16:44] `7ce502c`: test: add unit tests for gnocchi_constraint_se_vs_typical_analysis core logic
- [2026-07-10 16:43] `0d7dccd`: feat: exp_gnocchi_constraint_se_vs_typical_enhancer -- REJECT, ClinVar-free replication confirms null
- [2026-07-10 10:14] `5a9db09`: fix: finalize exp_llps_promoter_vs_se_chip_evidence вЂ” REJECT, ENCODE data exhausted
- [2026-07-10 10:02] `4e14bf4`: docs: auto-log sync
- [2026-07-10 10:01] `1cd7197`: fix: matched-control follow-up substantially weakens exp_llps_promoter_vs_se_chip_evidence
- [2026-07-10 09:19] `47e249d`: docs: auto-log sync after item C commit
- [2026-07-10 09:18] `96caf60`: feat: exp_heritability_vus_se_frequency (Item C) вЂ” REJECT, no detectable effect
- [2026-07-08 17:30] `c8c3cb6`: docs: check G4-seq data feasibility for non-B DNA direction, park it (21GB raw only)
- [2026-07-08 17:28] `66c45e2`: docs: auto-log sync 2
- [2026-07-08 17:28] `89668b0`: docs: auto-log sync
- [2026-07-08 17:27] `df68a42`: feat: HepG2 replication (PARTIAL) + permanent interval-math test suite
- [2026-07-08 17:21] `cb58ec8`: docs: final auto-log sync
- [2026-07-08 17:20] `3beebbe`: docs: auto-log update 4
- [2026-07-08 17:20] `dda0641`: docs: auto-log update 3
- [2026-07-08 17:19] `9848c6d`: docs: auto-log update 2
- [2026-07-08 17:18] `42464c2`: docs: auto-log update
- [2026-07-08 17:18] `b766250`: feat: exp_llps_ctd_phospho_vs_coactivators вЂ” second experiment, INCONCLUSIVE (window-sensitive)
- [2026-07-08 16:45] `e9161f6`: docs: auto-log update
- [2026-07-08 16:44] `dc14778`: fix: reviewer-caught off-by-one in liftover reverse-strand coordinate math + close evidence gap
- [2026-07-08 16:34] `1fcd403`: feat: exp_llps_promoter_vs_se_chip_evidence вЂ” first DNA Ladder result, SE-favoring
