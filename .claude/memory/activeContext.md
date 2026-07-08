# Active Context — DNA Ladder

**Last Updated:** 2026-07-08
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

**C (new research direction) — not started yet, next up.**

## Auto-commit log
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
