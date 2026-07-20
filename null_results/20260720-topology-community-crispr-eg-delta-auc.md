# Null result — CRE-community topology ΔAUC over dist+activity+SE (CRISPR E–G)

**Date:** 2026-07-20  
**Track:** `se_llps`  
**Experiment:** `tracks/se_llps/experiments/exp_topology_community_crispr_eg/`  
**Candidate:** C-B1  
**Verdict:** **REJECT** (`FAIL_KILL`)

## Pre-registered claim (redesigned after rE2G audit)

On frozen K562 CRISPR E–G pairs (chromosome holdout chr20–22), CRE-community topology
features (enhancer/promoter loop degree, shared loop-graph community size, min loop-span
rank) add **ΔAUC ≥ 0.05** over baseline
`log10_distance + cCRE ELS (pELS/dELS) + dbSUPER SE membership`.

**Kill:** ΔAUC < 0.02 → FAIL_KILL / REJECT.  
Explicitly **not** a claim that any 3D contact feature is novel (rE2G already has
contact/loops; audit `SURVIVES_WITH_REDESIGN`).

## Result summary

| Arm | Value |
|-----|-------|
| AUC baseline | 0.8806 |
| AUC + topology | 0.8733 |
| **ΔAUC** | **−0.0073** |
| Distance-alone AUC | 0.8796 (positive control PASS) |
| LOCV mean ΔAUC | +0.0003 |
| Shuffle-label null mean ΔAUC | +0.0093 |

Label column: **`Regulated`** (TRUE = positive). n_test=265 (20 positives) on chr20–22.

Topology signal was sparse (`frac_shared_community_gt0` ≈ 1.3%; mean enhancer loop degree
≈ 0.30). Incremental features did not clear the kill threshold.

## What this does NOT mean

1. Does **NOT** mean Hi-C loops / 3D contact are uninformative for E–G prediction in
   general — ENCODE-rE2G already uses contact and Extended loop features successfully.
2. Does **NOT** mean CRE communities are biologically irrelevant; only that these cheap
   loop-graph community features add no desk-worthy ΔAUC over distance+ELS+SE on this
   frozen benchmark split.
3. Does **NOT** authorize causal language (communities drive targeting).
4. Does **NOT** reopen closed SE→LLPS / VUS / Gnocchi / R-loop / G4 claims.
5. Does **NOT** license wet-lab GO, holdout unblind, or C1 E/P edits.
6. Does **NOT** promote the parked TE registry candidate `C-B1-TE-AluY-AG`.

## Recommendation

Close C-B1 topology desk as REJECT. Treat further “add graph topology over a strong
distance baseline” variants as low priority unless a clearly different estimand is
preregistered.
