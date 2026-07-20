# Decision — exp_topology_community_crispr_eg (C-B1)

**Date:** 2026-07-20  
**Status:** `PENDING_KILL_TEST` (T0 **PASS_FREEZE**)

## Verdict (current)

Desk experiment **opened** under Standard tier. Prereg + T0 freeze + rE2G audit complete.
No predictive ΔAUC results yet.

| Gate | Status |
|------|--------|
| L0 Predictive classification | DONE |
| claim / controls / notes prereg | DONE |
| Novelty vs closed SE nulls + C-A1 | DONE (see claim.md) |
| ENCODE-rE2G adversarial feature audit | DONE → **SURVIVES_WITH_REDESIGN** |
| T0 ENCODE / public accession probe | **PASS_FREEZE** (`data/t0_accession_probe.json`) |
| Accession freeze | **DONE** (`ACCESSION_FREEZE_v1.md`) |
| Chromosome-holdout ΔAUC kill-test | **NOT STARTED** (next session) |

## Pre-registered decision rules (unchanged until results)

- **SUPPORT** if holdout ΔAUC ≥ 0.05 (topology+SE vs SE-only)
- **REJECT** if holdout ΔAUC < 0.02
- **INCONCLUSIVE** if 0.02 ≤ ΔAUC < 0.05
- **BLOCKED_DATA** if CRISPR labels, Hi-C loops, or cCRE nodes cannot be frozen in processed form
- **KILLED_BY_FRONTIER** only if audit shows the exact community estimand is already settled
  (audit currently: **SURVIVES_WITH_REDESIGN**, not killed)

## What this decision does NOT authorize

- Full ML fit in the same commit as first prereg without freeze
- Reopening SE→G4/R-loop/Gnocchi/VUS/LLPS claims
- Starting TE AluY+AG (registry C-B1-TE) analysis
- Holdout unblind / wet GO / C1 E/P edits

## Next action

After merge: implement community features on frozen accessions → chromosome-holdout kill-test
→ update this file + optional `null_results/` if REJECT/INCONCLUSIVE.
