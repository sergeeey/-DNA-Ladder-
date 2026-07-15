# Second scorer type — admission path (ARCHCODE absent)

**Date:** 2026-07-13  
**Status:** `SPEC_FROZEN` / AlphaGenome path **AVAILABLE** (smoke PASS 2026-07-14);  
ARCHCODE still absent. `score_freeze.status` remains `EXPLORATORY_FROZEN`  
until planted/benchmark + unblind — smoke ≠ wet-lab GO.

---

## Rule

A **second scorer type** may become confirmatory primary only if all hold:

1. Not a retune of `ctcf_pwm_delta_v1.1` (different modality or independent model family)  
2. Passes `scorer_benchmark_spec.md` on planted controls **or** an external validated allele-delta protocol  
3. Leakage audit PASS (no ClinVar/VEP/pearl in ranking features)  
4. HBB development set not used for threshold tuning  
5. Recorded in `score_freeze.yaml` with version/hash/schema  

---

## Ranked candidate types

| Priority | Type ID | Modality | Admission status now |
|----------|---------|----------|----------------------|
| 1 | `archcode_disruption` | Physics / loop-extrusion | **FAIL** — binary absent |
| 2 | `alphagenome_variant_contact` | Sequence→tracks/contacts | **AVAILABLE** — live smoke PASS; not CONFIRMATORY_FROZEN |
| 3 | `unichrom_or_hicompass_allele_delta` | Contact Δ (WT vs mut) | **IMMATURE** — needs Δ-mode validation |
| — | `ctcf_pwm_delta_v1.1` | Motif PWM | Exploratory only — **forbidden as confirmatory primary** |

---

## Interim policy

```text
primary confirmatory freeze: EXPLORATORY_FROZEN (not yet CONFIRMATORY_FROZEN)
alternate primary path: alphagenome_variant_contact AVAILABLE
active exploratory: ctcf_pwm_delta_v1.1
G2 beat-baselines test: NOT RUN (no allele panel scored yet)
wet-lab GO: STOPPED
holdout: SEALED
```

Do **not** invent a PWM-derived composite and call it a new primary. That would violate the second-scorer rule and recreate leakage of “complexity = validity.”

---

## Admission command (when binary/API ready)

```text
# ARCHCODE
# 1) place binary, set score_freeze.primary_model.*
# 2) python archcode_admission_gate.py

# AlphaGenome (preferred second type while ARCHCODE missing)
# 1) set env ALPHAGENOME_API_KEY or local checkpoint
# 2) python adapters/alphagenome_adapter.py --smoke
# 3) python second_scorer_admission_gate.py --type alphagenome_variant_contact
```

---

## Output artifacts

- This spec  
- `pilot_scaffold/second_scorer_admission_gate.py`  
- `09_outputs/pilot_chr11/second_scorer_admission.json`  
- `pilot_scaffold/adapters/alphagenome_adapter.py` (live smoke)
