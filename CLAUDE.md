# CLAUDE.md — DNA Ladder

## Purpose

Falsification-first testing of hypotheses about DNA's open questions on real public data.
Sibling project to `Research Library` (`D:\Research Library\`) — cite sources by DOI/ID there,
don't duplicate PDFs here. Sibling-in-spirit to `ARCHCODE` (`C:\Users\sboi\ARCHCODE_review`) —
same methodology, different (broader) domain. Consult ARCHCODE for known bug classes and
reusable code patterns before re-deriving something it already solved (see
`C:\Users\sboi\.claude\projects\C--Users-sboi-ARCHCODE-review\memory\dna-ladder-spinoff-project.md`).

## Prime Directive

Same as ARCHCODE: presumption of falsity for any generated artifact. A claim is valid only
after estimand defined → novelty checked → real data tested → honest verdict recorded,
regardless of whether the result is positive or negative.

## Protocol (identical to ARCHCODE, summarized — see ARCHCODE's CLAUDE.md/rules for full text)

1. **L0 gate** — classify every hypothesis as Descriptive / Predictive / Causal before any data
   work.
2. **Novelty Check (mandatory)** — search `Research Library/sources/`, this repo's own
   `null_results/`, and the literature before designing an experiment. A hypothesis already
   covered by the field's current frontier (e.g. an existing 2025-2026 preprint making the same
   claim) is not novel — reformulate honestly (independent replication / different data source /
   narrower sub-question) or don't run it.
3. **claim.md** (Standard tier: claim.md + controls.md/notes + decision.md) — pre-registered
   before results are seen. Full tier for anything with causal language.
4. **Real data only** — no synthetic/mock data presented as validation. Public sources cited by
   URL/accession, same discipline as ARCHCODE's ClinVar/gnomAD/ENCODE fetches.
5. **null_results/** — every REJECT/INCONCLUSIVE filed with "what this does NOT mean", same
   format as ARCHCODE's `null_results/INDEX.md`.

## Data sources used so far

- ENCODE (ChIP-seq, ATAC-seq) — same portal as ARCHCODE (`www.encodeproject.org`)
- Research Library (`D:\Research Library\sources\`) — literature, cited by DOI

## Folder layout

```
experiments/exp_<slug>/claim.md, decision.md, results.json
null_results/<date>-<slug>.md + INDEX.md
scripts/       — fetch + analysis scripts, real public sources only
data/input/    — fetched raw data (large files NOT committed to git, same as ARCHCODE)
.claude/memory/activeContext.md — session continuity
```
