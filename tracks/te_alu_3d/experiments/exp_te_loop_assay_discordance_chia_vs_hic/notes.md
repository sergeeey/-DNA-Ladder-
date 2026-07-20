# Notes — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Source decision:** Deep Research Report v1.0 → `VALIDATE_DESK` for C-A1

## Why C-A1 over higher-scoring C-B1

| Axis | C-A1 | C-B1 |
|------|------|------|
| Final score | **7.06** | **7.47** (higher) |
| L0 purity | Clean descriptive discordance OR | Mixes TE enrichment + AG allele prior |
| Kill-test | ≈2 h MAPQ≥30 sensitivity | Needs AG path + anchor/motif stack |
| Identifiability | I=7.8 | I=6.8 |
| C1 bleed risk | Low (no allele list) | Higher (panel-adjacent priors) |

Recommendation rule was **not** max raw score: among `final_score ≥ 7.0`, maximize
identifiability × kill-speed. Hence C-A1 despite C-B1’s higher headline score (report §1, §5).

## Relation to reusable assets

- **P3 matched-null** (`09_outputs/prospective/P3_matched_null_*`): same covariate-matching
  ethos; do not copy C1 allele panels into this universe.
- **null_results/**: any REJECT / INCONCLUSIVE / BLOCKED_DATA must file with “what this does
  NOT mean,” same format as SE/LLPS closures.
- **ENCODE probe pattern:** metadata-only REST queries (as in `se_llps` fetch scripts);
  no `.hic` commits.
- **Accession freeze:** `ACCESSION_FREEZE_v1.md` — primary `ENCFF511QFN` + `ENCFF693XIL`.
- **Replication freeze:** `ACCESSION_FREEZE_replication_v1.md` — GM12878 `ENCFF913VWM` +
  `ENCFF781ASD` (+ CTCF `ENCFF796WRU`).
- **T4/T5:** umap≥0.3 OR 0.898 (FAIL strengthened); GM12878 OR 1.252 inconclusive —
  `null_results/` deferred.

## Risks (from report risk register)

1. **Wrong accessions** — `ENCSR000BZZ` is ESR1 ChIA-PET (not Pol II); `ENCSR444WCX` invalid.
   Replaced by freeze: `ENCSR880DSH` / `ENCFF511QFN` and `ENCSR545YBD` / `ENCFF693XIL`.
2. **FASTQ-only Pol II ChIA-PET** → `BLOCKED_DATA`; demote to C-K1 (CTCF ChIA-PET) or C-B1.
   *(T0: not triggered — processed bedpe available.)*
3. **Mappability confounding** — TE signal often tracks multi-mapping; MAPQ≥30 is the cheap kill.
4. **Build mismatch** — freeze GRCh38 before intersects.
5. **Scope creep** — no wet-lab, no oligo order, no holdout, no C1 E/P edits.

## Explicit non-actions

- Do not unseal holdout  
- Do not order oligos / submit B0 PO  
- Do not edit `C1_claim_freeze_pack_v1` E/P locks  
- Do not reopen closed SE/LLPS or HBB enrichment claims  
- Do not invent enrichment ORs before analysis  
