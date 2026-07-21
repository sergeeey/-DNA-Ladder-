# Notes — exp_te_age_loop_reproducibility (C-D1)

## Why this fruit

Registry `next_fruit_recommend: C-D1` after C-F1/C-G1 BLOCKED_DATA (2026-07-21 wave).
Title in current registry: **TE divergence/age bin vs cross-assay loop-call reproducibility**
(not the historical ClinVar “orthogonal convergence” phrasing).

## L0

Descriptive only. milliDiv is a divergence proxy, not a causal age mechanism claim.

## Relation to C-A1

C-A1 asked whether **AluSz** is enriched on discordant anchors (OR). C-D1 asks whether
**younger vs older** TE-hit anchors differ in shared-call rate. Different exposure,
related assay pair (reuse frozen K562 bedpe).

## Data plan

Reuse C-A1 frozen accessions; download into this experiment's `data/input/` (gitignored).
rmsk required for milliDiv.

## Stop rules

- Missing bedpe or rmsk → BLOCKED_DATA
- Δ < 0.05 → REJECT + null_results
- 0.05 ≤ Δ < 0.10 → INCONCLUSIVE
- Δ ≥ 0.10 → SUPPORT (desk; no wet)

## Forbidden

Holdout unblind; C1 E/P; wet GO; fake data.
