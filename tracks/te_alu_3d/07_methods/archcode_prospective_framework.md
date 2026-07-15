# ARCHCODE-PROSPECTIVE — leakage-free framework

**Date:** 2026-07-13  
**Status:** `FRAMEWORK_ONLY` — no primary scorer, no candidate nomination, no wet-lab GO  
**Refs:** `hypothesis_cultivation_pass_architecture_variant.md`, `pilot_scaffold/prospective_config.yaml`, `competitor_baseline_ensemble.md`

---

## Purpose

Provide a reproducible **candidate-qualification skeleton** that:

1. Builds a leakage-free variant universe  
2. Computes transparent **motif-only** and **distance-only** baselines  
3. Audits forbidden inputs (G1) and prepares G2 comparison artifacts  
4. Supplies empty freeze templates for G3–G9  

This does **not**:

- validate ARCHCODE  
- reopen Track A enrichment (T/C remain NOT SUPPORTED on HBB)  
- score sealed holdout windows  
- nominate a biological candidate  

---

## Allowed vs forbidden inputs

| Class | Allowed | Forbidden |
|-------|---------|-----------|
| Variant source | gnomAD-like rare AF tables (chrom/pos/ref/alt/af) | ClinVar P/LP as ranking labels |
| Annotation | TE overlap, CTCF peak distance, GC, editability desk fields | consequence / VEP severity / pearl status |
| Locus | non-HBB erythroid windows | HBB development window chr11:5.2–5.3 Mb |
| Paths | `data/` slices outside `holdout/` | any path under `holdout/` while sealed |
| Outcomes | none (pre-outcome) | wet-lab results, holdout labels, HBB enrichment outcomes |

---

## Pipeline

```text
allowed TSV
  → leakage_audit (G1)
  → build_prospective_universe
  → motif_only + distance_only baselines (G2 prep)
  → competitor ensemble contract (G2b/G2c templates; AlphaGenome mandatory when runnable)
  → empty G3–G9 freeze templates
  → STOP until leakage-free primary scorer OR independent second scorer admitted
```

External models (AlphaGenome, UniChrom/Hi-Compass if allele-delta validated, enhancer3D context,
looplook targets, activity-axis) are classified under Arm A (convergence) or Arm B
(principled disagreement). See `competitor_baseline_ensemble.md`. ARCHCODE-only without
mechanism remains REJECT; ARCHCODE-only with strong mechanism + WT contact may be Arm B.
---

## Gate readiness under this framework

| Gate | Framework provides | Remaining UNKNOWN |
|------|--------------------|-------------------|
| G1 | `leakage_audit.py` + config/code hashes | PASS only if input clean |
| G2 | baseline TSV/JSON comparison | whether a future scorer beats baselines |
| G2b/G2c | independence matrix + Arm A/B classification templates | actual AlphaGenome/other runs |
| G3–G9 | empty templates | concrete V / E / P / M |

**Decision rule:** fail G1 → do not proceed. Framework completion ≠ wet-lab GO.

---

## Explicit UNKNOWN

- No variant currently passes G1–G9 as a frozen candidate  
- ARCHCODE binary absent → admission FAIL  
- Holdout remains SEALED (`unblind_authorized: false`)  
- Motif/distance baselines are **comparators**, not architecture proof  

---

## Outputs

```text
09_outputs/prospective/
  leakage_audit.json
  universe.tsv
  universe_provenance.json
  baseline_scores.tsv
  baseline_comparison.json
  templates/   # G2b/G2c ensemble + G3–G9 empty shells
```

---

## Relation to Track A

Track A enrichment claim remains **STOPPED**. This framework is a separate Growth Loop path toward a future allele-specific architecture test. Do not use HBB T/C results to choose candidates.
