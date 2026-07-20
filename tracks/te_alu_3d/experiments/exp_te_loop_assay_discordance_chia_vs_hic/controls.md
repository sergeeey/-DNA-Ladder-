# Controls — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Status:** PREREGISTERED_DESK (2026-07-20)  
**Parent claim:** `claim.md`

## Positive control gate — CTCF

**Purpose:** Sanity check that the loop-call intersection pipeline recovers an expected
architecture-associated class, not a test of the primary TE claim.

- Define CTCF-associated anchors using frozen K562 CTCF peaks: **`ENCFF769AUF`**
  (`ENCSR000AKO`, conservative IDR, GRCh38, preferred_default).
- T2 implementation: intersect unique Hi-C anchors (`ENCFF693XIL`) with CTCF peaks; compare
  to chromosome-preserving shuffle of CTCF; Fisher OR gate **≥ 2.0** → PASS
  (result: **PASS**, OR ≈ 5.12 — see `results/positive_control_ctcf_gate.json`).
- Failure mode: if CTCF gate OR < 2.0, treat primary TE OR estimates as **pipeline-suspect**
  (`BLOCKED_PIPELINE`) before claiming biology.

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

## Checklist before primary TE OR (T3)

| Item | Status |
|------|--------|
| Primary bedpe downloaded + md5 | DONE |
| CTCF positive gate OR ≥ 2.0 | DONE (PASS, OR 5.12) |
| RMSK pinned | DONE (UCSC hg38 md5 recorded) |
| Matched-null covariates implemented | PENDING |
| MAPQ/mappability track pinned | PENDING |
| Subfamily list frozen with n minima | PENDING |
| AluJo negative/contrast rule acknowledged | PRE-REGISTERED |

Do **not** finalize primary AluSz / subfamily OR until this checklist is complete.

