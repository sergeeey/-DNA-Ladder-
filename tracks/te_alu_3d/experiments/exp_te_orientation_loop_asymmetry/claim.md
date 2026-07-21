---
experiment: exp_te_orientation_loop_asymmetry
date: 2026-07-21
ladder_tier: Standard
question_type: Descriptive
status: REJECT
candidate_id: C-J1
candidate_alias: C-J1-te-orientation-loop-asymmetry
source: Deep Research registry — TE insertion orientation vs loop-anchor asymmetry
decision_gate: FAIL_KILL
null_results: null_results/20260721-te-orientation-loop-asymmetry.md
---

# Claim: TE insertion orientation vs loop-anchor asymmetry (K562 Hi-C)

## Status

**REJECT** (`FAIL_KILL`) — Standard tier; desk **CLOSED**.  
Primary |Δ_orient| **0.0064**; Alu-only **0.0196**. Both &lt; 0.05. See `decision.md`.

## EstimandOps L0

**Question type:** Descriptive.

In K562 (GRCh38), among **Hi-C HiCCUPS loop anchors** that overlap ≥1 RepeatMasker
TE (`SINE`/`LINE`/`LTR`), does **TE insertion strand** (+/−) differ systematically
between the **left** (genomically 5′) and **right** (3′) anchors of the same loop
calls by |Δ_orient| ≥ **0.10**?

Where:
- Each loop is kept as a **bedpe pair** (left = cols 0–2, right = cols 3–5).
- Anchor unit = 1 kb midpoint window after pad ≥1 kb (C-A1/C-D1 convention).
- TE strand at a TE-hit window = strand of the overlapping TE with **largest bp
  overlap** (ties → earliest genoStart).
- `p_left` = fraction of TE-hit **left** anchors with strand `+`.
- `p_right` = fraction of TE-hit **right** anchors with strand `+`.
- **Δ_orient** = `p_left − p_right`.

Explicitly **not causal**. Explicitly **not** CTCF motif orientation / convergent
CTCF (that is C-B1-TE-AluY-AG parked). Explicitly **not** wet / holdout / C1 E/P.

## Novelty (Gate 0)

- C-A1 / C-D1 / C-L1 ignore TE **strand** relative to left/right loop geometry.
- C-B1 (parked) uses convergent CTCF+RAD21 + AG — different exposure.
- This estimand tests **insertion-orientation asymmetry** across the two ends of
  the same Hi-C loop calls.

## Frozen claim (pre-results)

> |Δ_orient| = |p_left(+) − p_right(+)| ≥ **0.10** among TE-hit left vs right
> 1 kb Hi-C loop-anchor windows (K562; `ENCFF693XIL`).

**Falsification:** |Δ_orient| **< 0.05** → **REJECT**.  
Gray 0.05 ≤ |Δ| < 0.10 → **INCONCLUSIVE**.

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | K562 GRCh38 Hi-C HiCCUPS loops `ENCFF693XIL` (`ENCSR545YBD`) |
| Unit | Per-loop left and right 1 kb midpoint windows (pad ≥1 kb) |
| TE hit | ≥1 bp overlap with rmsk `repClass ∈ {SINE, LINE, LTR}` |
| Orientation | rmsk strand of max-overlap TE at TE-hit windows |
| Arms | Left-anchor TE-hits vs right-anchor TE-hits (pooled across loops) |
| Primary | \|Δ_orient\| = \|p(+ \| left) − p(+ \| right)\| |
| SUPPORT | \|Δ\| ≥ 0.10 |
| Kill | \|Δ\| < 0.05 |
| CI | Chromosome block bootstrap 95% CI on Δ (seed `20260721`) |

## Sensitivity (pre-registered)

1. **Alu-only** (repFamily contains `Alu`) — same |Δ|; SKIP if either arm n < 200.
2. **Both-TE loops** (exploratory, not primary kill): among loops with TE on **both**
   anchors, fraction of opposite-strand TE pairs vs 0.5 (report |f_opp − 0.5|).

## Datasets

| Role | Accession / source |
|------|--------------------|
| Hi-C HiCCUPS loops | `ENCFF693XIL` (`ENCSR545YBD`) |
| TE + strand | UCSC hg38 `rmsk.txt.gz` |

If bedpe or rmsk missing after T0 → **`BLOCKED_DATA`**.

## Forbidden claim language

- Causal TE-orientation → loop extrusion / CTCF convergence
- Equating rmsk strand with CTCF motif orientation
- Reopening C-A1 / C-D1 / C-E1 / C-L1 / C-H1 closed verdicts
- Inventing remaps to other Deep Research IDs
- Wet / holdout / C1 E/P / pathogenicity
