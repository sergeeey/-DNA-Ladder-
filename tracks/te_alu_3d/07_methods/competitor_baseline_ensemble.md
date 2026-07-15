# Competitor baseline ensemble — ARCHCODE positioning (2026)

**Date:** 2026-07-13  
**Status:** `GOVERNING` — required before wet-lab GO; adapters not yet run  
**Refs:** `archcode_prospective_framework.md`, `hypothesis_cultivation_pass_architecture_variant.md`

---

## Verdict on the landscape brief

| Item | Score | Note |
|------|------:|------|
| Strategic repositioning (not “best ClinVar AUC”) | 9/10 | Aligns with kill-first + prospective freeze |
| Mandatory AlphaGenome as modern baseline | 9/10 | Sequence-to-contact/variant effects are now table stakes |
| enhancer3D / UniChrom / Hi-Compass / looplook roles | 8/10 | Useful if roles stay narrow |
| “Lab only if all models agree” | **reject** | Would erase ARCHCODE’s blind-spot value |
| Corrected Arm A / Arm B design | **adopt** | Convergence vs principled disagreement |

**Adopted rule:** model disagreement is allowed as **Arm B** only when mechanism, WT contact, and controls are strong. “ARCHCODE alone + no mechanism” remains REJECT.

---

## Niche (frozen)

ARCHCODE’s contribution is **not** maximal pathogenicity AUC. The niche is:

> A falsification pipeline that combines independent models and emits only a small number of pre-registered wet-lab candidates.

This becomes a scientific contribution only after one prospectively frozen experiment with independent contact/expression measurement.

---

## Competitor roles (do not conflate)

| Project | Role for us | Is allele-specific SNV scorer? | Required mode before use |
|---------|-------------|-------------------------------:|--------------------------|
| **AlphaGenome** | Mandatory sequence→function/contact baseline | Yes (variant scorers) | Official API/research code; record model version |
| **enhancer3D** | Structural context: is E–P geometry stable? | **No** | Locus-level ensemble/distance lookup only |
| **UniChrom** | Contact-map / interaction probability comparator | Only if Δ-allele mode validated | Pre-register WT vs mutant input protocol |
| **Hi-Compass** | Cell-type contact-map comparator | Only if allele delta propagates to inputs/outputs | Prove SNV sensitivity; else context-only |
| **looplook** | Downstream target-gene assignment | No | After predicted altered contact |
| **Chorus** | Orchestration of sequence-to-function models | Meta-layer | Isolated env runs; provenance per oracle |
| **activity models** (e.g. multimodal VEM / Enformer-finetune) | Activity-axis discriminator | Often yes | Exclude pure enhancer-activity mechanism |
| **ENCODE-Toolkit** | Data access / provenance infrastructure | No | Never cite as biological evidence |

---

## Independence matrix (mandatory)

Agreement among correlated nets ≠ independent evidence. Before treating multiple DL positives as “convergence”, fill:

```yaml
model:
  name: null
  version: null
  training_datasets: []
  cell_types: []
  hic_or_contact_overlap_with_others: UNKNOWN
  input_modalities: []
  label_overlap_with_others: UNKNOWN
  dependence_flag: UNKNOWN   # independent | partially_dependent | redundant
```

If three models share ENCODE/4DN training overlap and the same cell-type bias, report **inconclusive**, not triple confirmation.

---

## Two arms (adopted)

```text
Arm A — convergence
  ARCHCODE + ≥1 adapted external model + observed WT contact/cell context
  → safer primary wet-lab candidates

Arm B — principled disagreement
  ARCHCODE positive; sequence models negative/null
  BUT: explicit anchor mechanism, observed WT contact, allele path, matched controls
  → high-risk blind-spot candidates (higher evidentiary bar)
```

### Decision table

| Result | Status |
|--------|--------|
| Several methods + observed data agree | Arm A primary candidate |
| Only ARCHCODE, but mechanism + WT contact strong | Arm B high-risk candidate |
| Only ARCHCODE and no direct mechanism | REJECT |
| All models positive but no cell-type context | HOLD |
| Models agree mainly via shared training overlap | INCONCLUSIVE |

**Rejected rule:** “Never send a candidate if only ARCHCODE supports it.”  
**Kept rule:** “Never send ARCHCODE-only without mechanism + WT contact + controls.”

---

## Corrected consensus pipeline

```text
Variant
  → QC + cell-type gate + observed WT contact
  → ARCHCODE leakage-free prediction (when admitted)
  → transparent motif/distance baselines
  → AlphaGenome variant/contact outputs
  → UniChrom or Hi-Compass ONLY if allele-delta mode validated
  → enhancer3D structural context (locus stability)
  → looplook target assignment
  → activity-axis model
  → classify: convergence | principled_disagreement | unsupported | inconclusive
  → matched prospective wet-lab panel
```

---

## What is implemented now vs later

| Now (this repo) | Later (when binaries/APIs available) |
|-----------------|--------------------------------------|
| Role contract + Arm A/B decision table | AlphaGenome adapter run |
| Independence-matrix template | UniChrom/Hi-Compass Δ-allele validation |
| Classification sheet template | looplook target assignment on frozen contacts |
| Wire into G2+/G6 candidate freeze | Actual Chorus multi-oracle batch |

Do **not** install or score holdout with these tools until existing unblind gates pass.
