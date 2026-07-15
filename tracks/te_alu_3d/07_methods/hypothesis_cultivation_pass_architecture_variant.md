# Hypothesis Cultivation Pass — prospective architecture-variant claim

**Date:** 2026-07-13  
**Status:** `IMMATURE_HYPOTHESIS` — not a biological claim; no wet-lab GO  
**Scope:** one future allele-specific perturbation at a pre-defined erythroid chromatin-contact element.  
**Out of scope:** rescuing the Track A enrichment claim, reinterpreting HBB as confirmatory, or calling a predicted score a 3D effect.

---

## 1. Object and boundary

### Raw observation (H0)

Some rare noncoding variants may lie in experimentally observed erythroid contact elements and may alter a sequence feature relevant to a local chromatin-contact mechanism.

This is an observation-to-investigate, **not** evidence that any present HBB/Alu/SVA variant changes a contact, expression, or disease risk.

### Weak hypothesis (H1)

A specific allele `V` at a specific erythroid locus could alter a local enhancer–promoter contact through a defined molecular mechanism.

### Target mature hypothesis (H6)

> In pre-specified erythroid cells, allele `V` changes `M` (the direct molecular feature), which changes the contact between pre-specified elements `E` and `P` by at least the frozen minimum effect; the predicted direction is stated before editing.

`M`, `E`, `P`, cell state, direction, minimum effect, and analysis unit must be filled only after a candidate passes the qualification gates below.

---

## 2. Current evidence state

| Fact / constraint | Status | Consequence |
|---|---|---|
| HBB/HUDEP-2 is a viewed development set | **[VERIFIED]** — `scientific_freeze_v1.md` | It cannot become an independent confirmatory set. |
| Track A PWM v1.1 T and C are not supported | **[VERIFIED]** — `09_outputs/pilot_chr11/permutation_results.json` | Do not use this enrichment result to choose an architecture candidate. |
| PWM v1.1 is exploratory only | **[VERIFIED]** — `score_freeze.yaml` | It cannot independently authorize a wet-lab causal claim. |
| ARCHCODE primary scorer is absent/admission FAIL | **[VERIFIED]** — `archcode_admission_gate.py` output | No prospective ranking from ARCHCODE exists yet. |
| A native erythroid contact will be measurable for a future candidate | **[WEAK]** | Must be demonstrated before a candidate is frozen. |

**Unknown zone:** there is currently no variant that passes the full candidate gate. This pass therefore defines the path from H1 to H6; it does not nominate a candidate.

---

## 3. Mechanism map (growth, not adjudication)

| ID | Competing mechanism | Generative story | Distinguishing prediction | Direct early endpoint | What would demote it |
|---|---|---|---|---|---|
| M1 | `ctcf_anchor` | `V` changes CTCF motif affinity/orientation at an occupied anchor, weakening or redirecting loop extrusion. | Allele-specific CTCF occupancy and anchor contact change have the pre-specified direction. | CTCF CUT&RUN/CUT&Tag or allele-aware ChIP-qPCR. | No occupied anchor or no plausible motif/orientation change. |
| M2 | `cohesin_loading_or_retention` | `V` changes cohesin loading/retention without a primary CTCF motif loss. | RAD21/SMC occupancy changes while CTCF occupancy may remain stable. | RAD21/SMC CUT&Tag plus targeted contact assay. | No cohesin evidence and no sequence/context rationale. |
| M3 | `enhancer_activity` | `V` changes TF binding or accessibility; contact or expression differences are secondary. | Accessibility/activity changes precede or exceed contact change; a reporter may show an autonomous allele effect. | ATAC-seq/CUT&Tag or reporter, paired with contact assay. | No plausible regulatory motif/accessibility context. |
| M4 | `promoter_or_splicing_effect` | `V` changes promoter or RNA processing directly; any contact observation is non-causal. | Expression/splicing changes without the predicted contact mechanism. | RT-qPCR + splice-aware RNA assay; sequence annotation. | Variant is non-promoter/non-splice and direct assay is null. |
| M5 | `editing_or_clone_artifact` | Observed difference arises from edit burden, off-targets, clonal selection, or batch. | Effect does not reproduce across independent edited populations/clones or is seen in matched neutral edits. | Amplicon sequencing, off-target panel, independent edits. | Replication across independently edited samples with matched controls. |

These mechanisms are mutually competing only where they make different early predictions. M1–M4 may also be mixed; M5 is an alternative explanation that must be controlled before biological interpretation.

---

## 4. Cultivation ladder: H1 → H6

| Transition | Required output | Promotion rule | Not a kill rule |
|---|---|---|---|
| H1 → H2 | One explicit mechanism class (`M1`–`M4`) | A concrete sequence-to-molecule story exists. | A weak score alone does not promote. |
| H2 → H3 | At least two competing mechanisms, including M5 | Each has a different expected observation. | Lack of a final assay result is not failure yet. |
| H3 → H4 | Directional discriminating predictions | Pre-specify which result favors M1 vs M2/M3/M4. | Do not select a prediction after seeing data. |
| H4 → H5 | Independent projections | Motif/occupancy, native WT contact, cell-state relevance, and editability are assessed independently. | Agreement among score variants of the same model family is not independent support. |
| H5 → H6 | Frozen candidate dossier | Candidate passes G1–G9 and all endpoints/controls/statistical units are written before outcome data. | Failing any mandatory gate is `NO_GO`, not proof that all architecture mechanisms are false. |

---

## 5. Candidate qualification gates (must all pass)

| Gate | Requirement | Evidence artifact before freeze |
|---|---|---|
| G1 | Ranking uses no ClinVar label, consequence-derived severity, VEP severity, old pearl status, or wet-lab outcome. | Immutable code/config hash and leakage audit. |
| G2 | Candidate adds information beyond motif-only and distance-only baselines. | Baseline comparison on a leakage-free candidate universe. |
| G3 | One mechanism class (`M1`–`M4`) and direct molecular endpoint are selected. | Candidate rationale. |
| G4 | The relevant wild-type contact exists in the intended erythroid cell state. | Public or newly generated contact evidence with provenance. |
| G5 | Allele-specific edit is feasible; guide/off-target and confounding activity/splice risks are assessed. | Editing design sheet. |
| G6 | One positive and matched neutral controls are feasible. | Frozen 3 candidate + 3 negative + 1 positive panel, or an explicitly smaller feasibility panel. |
| G7 | Contact and expression directions, minimum effects, and primary endpoint are frozen. | Frozen claim and PASS/FAIL registry. |
| G8 | Biological replicate, edit/differentiation batch, and statistical unit are defined; reads/cells are not independent replicates. | Power/analysis note. |
| G9 | Candidate identities cannot be replaced after outcome data are viewed. | Dated immutable manifest. |

**Decision rule:** failing G1–G6 is `NO_GO_FOR_WET_LAB`; it is not a claim that a general architecture mechanism is absent.

---

## 6. Pre-registered future test (only after H6)

```text
reference allele
  → allele-specific edit (validated)
  → direct mechanism assay selected by M1–M4
  → targeted native contact assay
  → expression assay
  → optional reporter as discriminator, not proof of architecture
  → independent replication
  → rescue only for candidates with a replicated primary signal
```

Interpretation is constrained:

- Contact change without expression change: a possible structural result, **not** pathogenicity.
- Reporter null: compatible with absence of a strong autonomous activity effect, **not** proof of architecture.
- Expression change without the predicted direct/contact change: favors a non-architecture mechanism.
- No reproducible effect after validated editing: reject that candidate's frozen mechanism claim.

---

## 7. Next operation

Build `ARCHCODE-PROSPECTIVE` (or an independently validated non-PWM primary scorer) with a leakage audit and motif/distance baselines. Only then is candidate cultivation permitted. External baselines follow `competitor_baseline_ensemble.md` (Arm A convergence / Arm B principled disagreement). The sealed Track A holdout remains unavailable for scoring until its existing unblinding conditions are met.
