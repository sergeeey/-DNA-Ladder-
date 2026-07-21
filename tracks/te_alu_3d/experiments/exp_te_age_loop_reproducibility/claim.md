---
experiment: exp_te_age_loop_reproducibility
date: 2026-07-21
ladder_tier: Standard
question_type: Descriptive
status: REJECT
candidate_id: C-D1
candidate_alias: C-D1-te-age-loop-reproducibility
source: Deep Research registry — TE divergence/age bin vs cross-assay loop-call reproducibility
decision_gate: FAIL_KILL
null_results: null_results/20260721-te-age-vs-loop-reproducibility.md
---

# Claim: TE divergence/age bin vs cross-assay loop-call reproducibility (K562)

## Status

**REJECT** (`FAIL_KILL`) — Standard tier; desk **CLOSED**.  
Primary Δ_repro **−0.0037**; Alu-only **−0.0043**. Both &lt; 0.05. See `decision.md`.

## EstimandOps L0

**Question type:** Descriptive.

In K562 (GRCh38), among **1 kb midpoint windows** of merged Pol II ChIA-PET and
Hi-C (HiCCUPS) loop anchors that overlap ≥1 RepeatMasker TE (`SINE`/`LINE`/`LTR`),
do **older** milliDiv tertiles show **higher** cross-assay reproducibility than
**younger** tertiles by Δ ≥ **0.10**?

Cross-assay reproducibility for a window:
`repro = 1` if the window overlaps **both** Pol II and Hi-C merged-anchor sets;
`repro = 0` if it overlaps exactly one (assay-exclusive).

Explicitly **not causal**. Explicitly **not** C-A1 AluSz-only discordance OR.
Explicitly **not** wet / holdout / C1 E/P / pathogenicity.

## Novelty (Gate 0)

- C-A1 tested **AluSz** enrichment of discordant anchors (subfamily), not age bins.
- C-F1 tested Mustache↔HiCCUPS Jaccard (BLOCKED_DATA) — different caller pair.
- This estimand stratifies TE-hit anchors by **UCSC rmsk milliDiv** (divergence proxy
  for TE age) and contrasts reproducibility rates across tertiles.

## Frozen claim (pre-results)

> Δ_repro = mean(repro | old tertile) − mean(repro | young tertile) ≥ **0.10**

where young = lowest milliDiv tertile and old = highest milliDiv tertile among
TE-hit windows (tertile cuts frozen on the TE-hit window set before reporting).

**Falsification:** Δ_repro **< 0.05** → **REJECT**.  
Gray 0.05 ≤ Δ < 0.10 → **INCONCLUSIVE**.

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | K562 GRCh38; Pol II ChIA-PET `ENCFF511QFN` + Hi-C HiCCUPS `ENCFF693XIL` |
| Unit | 1 kb midpoint window of merged anchors (C-A1 convention: merge, pad ≥1 kb, mid 1 kb) |
| TE hit | ≥1 bp overlap with rmsk `repClass ∈ {SINE, LINE, LTR}` |
| Age exposure | **min milliDiv** among overlapping TE intervals (youngest hit); tertiles |
| Outcome | Window shared (both assays) vs exclusive (exactly one) |
| Primary | Δ_repro (old − young) |
| SUPPORT | Δ ≥ 0.10 |
| Kill | Δ < 0.05 |
| Optional OR | Fisher OR(exclusive \| young) vs old; report-only alongside Δ |

## Datasets

| Role | Accession / source |
|------|--------------------|
| Pol II ChIA-PET loops | `ENCFF511QFN` (`ENCSR880DSH`) |
| Hi-C HiCCUPS loops | `ENCFF693XIL` (`ENCSR545YBD`) |
| TE + divergence | UCSC hg38 `rmsk.txt.gz` (milliDiv col) |
| Optional umap kill | Hoffman k100 Umap (if download cheap) |

If either primary bedpe or rmsk missing after T0 → **`BLOCKED_DATA`**.

## Forbidden claim language

- Causal TE-age → loop instability
- Equating milliDiv tertiles with a specific geological clock without citation
- Reopening C-A1 / C-H1 / C-L1 closed verdicts
- Wet / holdout / C1 E/P / pathogenicity
