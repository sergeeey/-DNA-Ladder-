# Pilot Redesign v2 — Track A Freeze Card

**Status:** FROZEN for next dual-track run  
**Date:** 2026-07-13  
**Track:** A — TE-associated 3D genome vulnerability  
**Out of scope:** Track B (second-site rescue), MWPM, stabilizer / quantum interpretation  

**Governing rule:** No confirmatory enrichment claim until this document is satisfied and score freeze is signed.

---

## 0. Current operational status (accepted)

```text
Track: A — TE-associated 3D genome vulnerability
Object: rare SNVs inside annotated Alu/SVA (not TE MEIs)
HBB/HUDEP-2: DEVELOPMENT set (labels viewed)
T: NOT SUPPORTED
C: EXPLORATORY SIGNAL, UNRESOLVED
Scientific freeze: v1 FROZEN (primary estimand = T)
Confirmatory claim: STOPPED
Scorer validated: NO
MWPM / Track B: not tested
```

See also: `scientific_freeze_v1.md`, `holdout_plan.md`, `scorer_benchmark_spec.md`.

### Interpretation of the negative run

> Current Track A implementation did not find a sufficient signal on a small exploratory ClinVar sample.
> This kills the **current pilot claim / configuration**, not the entire Track A hypothesis, and it is **not** a test of MWPM.

```text
current pilot claim:     killed
general Track A:         unresolved
Track B / MWPM:          not tested
```

### State machine

```text
INTAKE             PASS
ROUTED             PASS
FROZEN             PARTIAL → this document completes freeze for design; score binary still open
ATOMIZED           PASS
PRIOR_ART_CHECKED  PASS
BUILT              PASS locally
FALSIFIED          PASS for current pilot configuration
TEST_DESIGNED      PASS exploratory / PARTIAL confirmatory
TESTED             PASS exploratory
RECOMPOSED         IN PROGRESS (this document)
VERIFIED           local PASS / external PARTIAL
REGISTERED         PASS
STOPPED            PASS for current enrichment claim
```

---

## 1. KC0 — Cell-type / locus congruence

### Requirement

A locus may enter **confirmatory** analysis only if:

1. The target regulatory program is active in the selected cell type.
2. A relevant CTCF / cohesin / 3D dataset exists for that cell type.
3. Primary 3D context for scoring matches the cell type used for CTCF peaks / Hi-C.

### Fail action

- Exclude locus from confirmatory analysis.
- Exploratory output allowed only with explicit `cell_type_mismatch: true` flag.

### Operational rules (chr11)

| Locus / program | 3D context | Confirmatory? |
|-----------------|------------|---------------|
| HBB / β-globin LCR | GM12878 | **No** — exploratory only |
| HBB / β-globin LCR | Erythroid (e.g. HUDEP-2, primary erythroblasts, erythroid Hi-C) | Potentially yes |
| B-cell-active chr11 locus | GM12878 | Potentially yes |
| Silent locus in chosen cell type | any | No confirmatory |

### Implementation hooks

- `config.yaml → three_d_context.kc0_locus_table`
- `kill_criteria.md → KC0`
- Report template section: KC0 pass/fail per locus

---

## 2. Two estimands (must both be reported)

### Estimand T — Total TE effect

**Question:** Do TE variants differ in architecture disruption after controlling **technical / pre-exposure** factors only?

**Controls allowed in C_technical:**

- variant length / type
- GC
- mappability
- blacklist / segdup / gnomAD discordance QC (hard exclude, not match)
- chromosome / window
- distance-to-TSS (optional technical/regulatory density proxy — document choice)

**Must NOT control:** distance-to-CTCF (treated as on the causal path for total effect).

```text
Δ_total = E[S | TE, C_technical] − E[S | nonTE, C_technical]
```

### Estimand C — CTCF-conditional sequence effect

**Question:** Do TE variants differ from others at the **same CTCF-distance context**?

**Additionally control:** distance-to-CTCF (log bins), optionally chromHMM / compartment.

```text
Δ_conditional = E[S | TE, C_technical, D_CTCF] − E[S | nonTE, C_technical, D_CTCF]
```

### Reporting rules

| Rule | Enforcement |
|------|-------------|
| Publish T and C in separate tables | required |
| Loss of C does **not** auto-kill T | required |
| Loss of T with residual C → investigate mediation / collider | exploratory note only |
| Primary confirmatory claim must name which estimand | required |
| Mixing T and C into one “the effect” narrative | **forbidden** |

### Relation to KC2

KC2 (v1.2) is redefined:

- For **Estimand T:** sequential adjustment over C_technical only; adding D_CTCF is a mediation sensitivity, not a kill of T.
- For **Estimand C:** sequential adjustment including D_CTCF; if signal dies, C is killed (not automatically T).

---

## 3. Control hierarchy

| Level | Pool | Question answered | Role at N≈14 |
|-------|------|-------------------|--------------|
| **A** | Matched non-TE | TE vs rest of genome? | Primary inferential (when N allows) |
| **B** | Same TE family (Alu↔Alu, SVA↔SVA), non-candidate sites | Functional-site vs ordinary family member? | Diagnostic |
| **C** | Same subfamily + approximate evolutionary age | Beyond lineage/composition? | Diagnostic |
| **D** | Same locus / TAD (where feasible) | Local chromatin environment? | Diagnostic |

### Matching variables by estimand

| Variable | Estimand T | Estimand C |
|----------|------------|------------|
| length / type | yes | yes |
| GC | yes | yes |
| mappability | yes | yes |
| distance-to-TSS | optional | optional |
| distance-to-CTCF | **no** | **yes** |
| chromHMM | optional | preferred |
| TE family (Control B) | for B analysis | for B analysis |

### Open calibration (before confirmatory)

- [ ] Subfamily / age annotation source (Dfam / RepeatMasker repName → age proxy)
- [ ] TAD definition for Control D (cell-type matched Hi-C)
- [ ] Minimum n for promoting B–D from diagnostic → inferential

---

## 4. Block permutation (primary null)

### Primary

```text
shuffle labels within matched set
OR
shuffle within strata:
  TE class × subfamily × mappability_bin × GC_bin
  × [CTCF_bin if Estimand C]
  × [locus/TAD block if Control D available]
```

- `n_perm` = 10,000 for confirmatory endpoint
- Exchangeability must respect matching structure

### Software negative control only

Global label shuffle across the chromosome — **not** the primary statistical test.

### Implementation

- `config.yaml → qc_gates.gate_6_permutation.mode: block_matched`
- `permutation_test.py` must accept matched-set IDs from `control_manifest.csv`

---

## 5. KC1 — Standardized effect (report + gated threshold)

### Effect-size report (always)

\[
\Delta_{\mathrm{MAD}}
=
\frac{
\operatorname{median}(S_T) - \operatorname{median}(S_C)
}{
1.4826\,\operatorname{MAD}(S_C)
}
\]

Also report raw median Δ for continuity with v1.1 logs.

### Absolute 0.05 threshold

**Deprecated** as biological PASS/FAIL gate until recalibrated.

### Confirmatory PASS threshold for Δ_MAD

**Not chosen post-hoc after real run.** Must come from one of:

1. Benchmark loci with known architecture disruption
2. Synthetic perturbations with pre-specified magnitude
3. Pilot-independent calibration set (labels frozen)

Until calibration:

```text
Δ_MAD → effect-size report only
KC1 biological PASS gate → SUSPENDED
KC1 operational STOP for enrichment claim still requires:
  - permutation gate fail OR
  - Δ_MAD ≤ 0 (direction wrong) OR
  - n below preregistered minimum
```

### Interim exploratory gate (software / direction)

| Condition | Action |
|-----------|--------|
| perm_p ≥ α (block permutation) | BLOCK enrichment claim |
| median(S_T) ≤ median(S_C) | KC1 direction FAIL → STOP claim |
| n_test < preregistered min | STOP / underpowered |
| Δ_MAD reported | always, both estimands |

---

## 6. Score freeze card

Template: `pilot_scaffold/score_freeze.yaml`  
**Rule:** Outcome labels for confirmatory run remain hidden until freeze fields below are filled and dated.

### Required fields

```yaml
score_freeze:
  primary_model:
    name: ARCHCODE
    version: null          # FILL before confirmatory
    binary_hash: null
    config_hash: null
    input_schema_version: null
  preprocessing:
    genome_build: GRCh38
    normalization: null
    missing_data_policy: null
    duplicate_variant_policy: null
    multi_allelic_policy: null
  aggregation:
    primary_score: archcode_disruption
    direction_of_effect: higher_is_more_disruptive
    locus_aggregation_rule: null
  fallback:
    allowed: true
    model: LSSIM
    trigger_conditions: [primary_binary_unavailable]
    confirmatory_status_if_used: exploratory   # NEVER auto-keep confirmatory
  thresholds:
    kc1_effect_threshold: null   # fill only after calibration
    source_of_threshold: null
    frozen_at: null
  labels:
    outcome_labels_hidden_until_freeze: true
  frozen_by: null
  frozen_date: null
```

### Critical rule

> Using fallback after primary scorer failure **automatically downgrades** the analysis to exploratory. Confirmatory status is not retained.

---

## 7. Governing boundary (Track A vs B)

```text
Track A (this project):
  TE variant → architecture disruption → functional relevance

Track B (separate):
  primary disruption → second-site rescue → decoder comparison

MWPM:
  testable only after rescue-trajectory data exist
```

Current negative run’s correct function: **stop enrichment claim until redesign**, without elevating a weak signal into confirmation of a larger theory.

---

## 8. Next dual-track run — entry checklist

- [x] KC0 table filled for every confirmatory locus *(config.yaml rules; HBB+GM12878 exploratory)*
- [x] Estimands T and C coded as separate pipelines *(run_pilot.py v2)*
- [x] Control A primary; B diagnostic tables emitted *(C/D age/TAD still open)*
- [x] Block permutation wired to matched sets
- [ ] `score_freeze.yaml` completed (hashes + date)
- [ ] gnomAD chr11 / window slice present (dual-track KC3)
- [ ] CTCF/TSS placeholders replaced with cell-type-matched ENCODE/GENCODE
- [ ] KC1 Δ_MAD calibration source documented OR gate remains report-only
- [x] Enrichment summary still gated on permutation + direction + freeze

---

## 9. Document control

| Version | Date | Change |
|---------|------|--------|
| v2.0 | 2026-07-13 | Freeze: KC0, dual estimand, controls A–D, block perm, KC1 MAD, score freeze |

**Supersedes for design decisions:** ad-hoc rules in pilot_scaffold README that conflict with this file.  
**Does not erase:** real-run logs under `09_outputs/pilot_chr11/` (historical killed claim).
