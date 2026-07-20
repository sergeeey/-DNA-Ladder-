# Controls — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Status:** PREREGISTERED_DESK (2026-07-20)  
**Parent claim:** `claim.md`

## Positive control gate — CTCF

**Purpose:** Sanity check that the loop-call intersection pipeline recovers an expected
architecture-associated class, not a test of the primary TE claim.

- Define CTCF-associated anchors using a public K562 CTCF peak set (ENCODE accession
  **VERIFY** at T0; assembly-matched to loop freeze).
- Expectation: CTCF-overlapping anchors should be enriched among **shared** (ChIA-PET ∩ Hi-C)
  loops relative to genomic background at a coarse level.
- Failure mode: if CTCF gate shows no recoverable shared-loop enrichment, treat primary TE
  OR estimates as **pipeline-suspect** (INCONCLUSIVE / debug) before claiming biology.

This gate does **not** authorize CTCF-causal language or C1 E/P edits.

## Negative control — AluJo

**Purpose:** Guard against a generic “any Alu” story driven by old/inactive AluJ elements.

- AluJo (and related AluJ subfamilies if collapsed) are tracked as a **negative / contrast**
  class unless explicitly promoted into the primary pre-registered subfamily list at T0 with
  written justification.
- Default expectation under the “younger / more polymorphic TE” narrative: AluJo should
  **not** be the sole driver of a headline OR≥1.3 claim.
- If AluJo alone meets MCID while AluY/AluS/SVA do not, report as contrast result; do **not**
  silently rebrand the claim post hoc.

## Matched-null covariates

Match discordant anchors to null anchors on:

| Covariate | Rule |
|-----------|------|
| Mappability | Same decile (Umap / ENCODE track; assembly-matched) |
| GC content | Same bin (window-matched) |
| Anchor length / window size | Same bin |
| Chromosome | Prefer same chr; if impossible, match chr-size class and record |

Reuse the **P3 matched-null discipline** (covariate-first, no post-hoc universe expansion
after seeing TE ORs). Exact matching script is post-T0; this file freezes the covariate list.

## Sensitivity list (pre-registered)

1. **MAPQ≥30** (or equivalent high-quality / high-mappability filter) — primary kill-test  
2. Independent replicate processed loop file / second ENCODE experiment  
3. Drop anchors overlapping ENCODE blacklist / segdup  
4. Restrict to autosomes  
5. Alternate discordance definition (ChIA-only vs Hi-C-only analyzed separately)  
6. Window size sensitivity (± pre-registered pad around anchor midpoint)

If (1)+(2) drive all subfamily ORs below 1.1 → **REJECT** per `claim.md`.
