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

No results exist yet. This experiment is design-stage only as of 2026-07-08.

## Research backlog (not started)

See `RESEARCH_DIRECTIONS.md` — 7 more candidate directions beyond LLPS (non-coding DNA
function, dark transcriptome, centromeric DNA, transgenerational epigenetics, non-B DNA
structures, missing heritability/regulatory variants). Not prioritized.
