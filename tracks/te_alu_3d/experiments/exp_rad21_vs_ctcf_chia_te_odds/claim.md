---
experiment: exp_rad21_vs_ctcf_chia_te_odds
date: 2026-07-21
ladder_tier: Standard
question_type: Descriptive
status: BLOCKED_DATA
candidate_id: C-G1
candidate_alias: C-G1-rad21-vs-ctcf-chia-te-odds
source: Standing order post C-F1 BLOCKED_DATA — T0 only
decision_gate: BLOCKED_DATA
---

# Claim: RAD21 vs CTCF ChIA-PET TE-anchor odds (K562)

## Status

**BLOCKED_DATA** — Standard tier; desk **CLOSED** at T0.  
CTCF ChIA-PET GRCh38 loops available (`ENCFF118PBQ`); **no** released K562 RAD21
ChIA-PET GRCh38 processed loop bedpe (fastq-only or hg19 archived TSV).  
OR **not computed**. See `decision.md`.

## EstimandOps L0

**Question type:** Descriptive.

In K562, among processed ChIA-PET loop anchors from **RAD21** vs **CTCF**, do TE
(primary AluSz) odds differ with **OR ≥ 1.3** (RAD21 vs CTCF)?

Explicitly **not causal**. Explicitly **not** C-A1 Pol II discordance.

## Frozen claim (pre-results)

> Fisher OR(AluSz | RAD21 anchors) / OR context vs CTCF anchors ≥ **1.3**
> (or absolute TE-anchor OR contrast ≥ 1.3 — freeze exact form in ACCESSION_FREEZE
> before scoring).

**Falsification:** after umap ≥ 0.3, OR **< 1.1** → **REJECT**.

## Datasets — T0

| Role | Probe target |
|------|----------------|
| CTCF ChIA loops | `ENCSR597AKG` → `ENCFF118PBQ` (preferred GRCh38 bedpe) |
| RAD21 ChIA loops | `ENCSR338WUS` / `ENCSR000FDB` GRCh38 bedpe |
| TE | UCSC hg38 rmsk |

If RAD21 GRCh38 processed loops missing → **`BLOCKED_DATA`**.

## Forbidden

Wet / holdout / C1; lifting hg19 archived loops without a new claim freeze; pathogenicity.
