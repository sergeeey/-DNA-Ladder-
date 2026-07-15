# Scientific Freeze v1 — Track A

**Date:** 2026-07-13  
**Status:** FROZEN  
**Refs:** `pilot_redesign_v2.md`, `pilot_scaffold/score_freeze.yaml`

---

## Accepted verdict (HBB / HUDEP-2 exploratory real-data run)

```text
T (total TE effect):           NOT SUPPORTED
C (CTCF-conditional):          NOT SUPPORTED   # v1.1; supersedes earlier UNRESOLVED
Confirmatory claim:            STOPPED
MWPM / stabilizer / Track B:   NOT TESTED
```

**Object of analysis (precise):** rare **SNVs inside annotated Alu/SVA**, not polymorphic TE insertion/deletion events. Do not conflate these classes.

**Endpoint language until 3D validation:**

```text
ALLOWED:  predicted CTCF motif disruption (PWM / future validated scorer)
FORBIDDEN: 3D genome disruption (as confirmed claim)
```

---

## Frozen claim hierarchy

```yaml
scientific_freeze:
  status: FROZEN
  frozen_at: "2026-07-13"

  primary_claim: >
    Rare SNVs inside Alu/SVA show higher predicted CTCF-motif disruption
    than matched non-TE controls after QC, under a pre-registered estimand.

  primary_estimand: total_te_effect          # T — PRIMARY
  secondary_estimand: ctcf_conditional       # C — SECONDARY / diagnostic

  multiplicity_policy:
    family_wise: primary_only_at_alpha
    secondary_reporting: effect_size_and_perm_p_without_claim
    post_hoc_switch_of_primary: forbidden

  primary_endpoint:
    metric: delta_MAD
    direction: TE_gt_control
    test: block_permutation_within_matched_sets
    alpha: 0.05
    biological_gate: suspended_until_scorer_calibration

  primary_control: A_nonTE
  diagnostic_controls: [B_same_family, C_same_subfamily]
  # D_same_TAD: deferred until cell-type Hi-C

  permutation_scheme: block_matched
  software_negative_control: global_shuffle

  cluster_unit:
    primary: TE_instance          # RepeatMasker interval id
    secondary: [CTCF_peak, local_genomic_block_10kb]
    note: N_variants ≠ N_independent; report effective N

  minimum_effect_of_interest:
    delta_MAD: null               # set only after independent calibration
    until_then: direction_and_perm_gate_only

  stop_rules:
    - perm_p_primary >= alpha → STOP enrichment claim
    - median_delta <= 0 → STOP claim (direction fail)
    - scorer_benchmark_fail → STOP biological run
    - confirmatory_on_development_set → FORBIDDEN
    - PWM_or_unvalidated_ARCHCODE → exploratory_only

  variant_class_scope:
    included: SNV_indel_inside_annotated_Alu_SVA
    excluded_from_current_claim: polymorphic_TE_insertion_deletion
```

---

## Dataset roles (after HBB peek)

| Set | Role | Labels |
|-----|------|--------|
| **HBB / HUDEP-2** | **exploratory development + calibration** | Already viewed — not confirmatory |
| Future erythroid holdout | **confirmatory** | Hidden until scientific + score freeze signed |
| GM12878 + HBB | exploratory mismatch only (KC0) | never confirmatory |

Re-running ARCHCODE on the same 1278 HBB variants improves the analysis but is **not** an independent confirmatory test unless ARCHCODE was externally fixed pre-peek and protocol was frozen (holdout still preferred).

---

## ARCHCODE admission gate (before confirmatory)

```text
binary exists
+ version/hash fixed
+ provenance documented (training data, genome build, schema)
+ independent benchmark PASS (see scorer_benchmark_spec.md)
+ HBB labels not used for tuning
+ scientific_freeze primary_estimand unchanged
→ then status may become FROZEN confirmatory
```

Unvalidated ARCHCODE is **not** preferred over transparent PWM solely because it is more complex.

---

## State machine (accepted)

```text
BUILT                    PASS
REAL DATA INGESTED       PASS
KC0 CELL CONTEXT         PASS
EXPLORATORY SCORE FROZEN PASS
SCIENTIFIC FREEZE        PASS (this document)
TOTAL ESTIMAND           FAIL TO REJECT NULL
CONDITIONAL ESTIMAND     NOT SUPPORTED (v1.1)
SCORER VALIDATED         PASS (ctcf_pwm_delta_v1.1, planted-motif bench; exploratory only)
CONFIRMATORY FROZEN      NO
3D MECHANISM TESTED      NO
TRACK A CONFIRMED        NO
CURRENT CLAIM STOPPED    YES
```

---

## Next operations (ordered)

1. Scorer benchmark (pos/neg controls) — gate before any new biological run  
2. Matching / effective-N diagnostics on HBB development set  
3. Written DAG role of `distance_to_CTCF` (see `dag_distance_to_ctcf.md`)  
4. Pre-register erythroid holdout (non-HBB)  
5. Optional second scorer type (binding/regulatory) — still one primary  
6. Only after sequence-level PASS → CTCF binding / Hi-C / expression layers  

Track B / MWPM remains out of scope until rescue trajectories exist.
