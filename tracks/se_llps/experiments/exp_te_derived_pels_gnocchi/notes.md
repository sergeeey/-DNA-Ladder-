# Notes — exp_te_derived_pels_gnocchi (C-H1)

## ID remapping

Deep Research registry originally listed **C-H1** as Micro-C vs Hi-C TE recovery. Standing
order 2026-07-20 fills the C-H1 desk with **TE-derived pELS Gnocchi** (this folder). The
Micro-C estimand is started as **C-I1** (registry AluJo NC C-I1 remains a control note
inside C-A1; desk title overridden for queue continuity — see registry note).

## Reuse

- Gnocchi loader / `weighted_mean_z`: `tracks/se_llps/scripts/gnocchi_constraint_se_vs_typical_analysis.py`
- GC / TSS / rmsk / match patterns: C-A2 `exp_sva_f_ccre_state_switching` (dELS → pELS)

## Workflow

1. T0/T1 — download Gnocchi + Registry + rmsk + 2bit + GENCODE
2. Match lock — covariates only → `results/matching_lock.json`
3. Attach Z → `results/primary_result.json`
4. decision.md + null_results if REJECT/INCONCLUSIVE
5. Registry / Changelog / Tasktracker; start C-I1 T0

## Out of scope

Micro-C bedpe; SE H3K27ac peaks; SVA_F-only switching; wet / holdout / C1.
