# RDR Router v1 — Track A / DNA Ladder

**Status:** `OPERATIONAL`  
**Date:** 2026-07-14  
**Scope:** executable routing only — not a new scientific theory  
**Refs:** `scientific_freeze_v1.md`, `holdout_plan.md`, `hypothesis_registry_v1.md`,  
`archcode_prospective_framework.md`, `second_scorer_type_spec.md`

**Explicitly out of scope:** GED, EVSI formulas, Surgery Policy, Catalog of Singularities,  
extra Gate/Layer nouns.

---

## Passport (frozen for this project)

```text
stakes:           high
novelty:          high
cost_of_error:    high
reversibility:    hard (lab / publication / holdout unblind)
mode:             high-risk + exploratory desk
```

Confirmatory and wet-lab paths stay blocked until guards below pass.

---

## Seven core objects (only these are mandatory)

| # | Object | Where it lives |
|---|--------|----------------|
| 1 | Environment Passport | this file |
| 2 | Frozen Claim | `scientific_freeze_v1.md` |
| 3 | Competing Hypotheses | registry + M1–M5 / Arm A·B |
| 4 | Differentiating Test | G1–G9 / admission gates |
| 5 | Evidence Artifact | path + hash under `09_outputs/` |
| 6 | Decision | PASS / FAIL / IMMATURE / BLOCKED / STOPPED |
| 7 | Registry Entry | `00_research_question/hypothesis_registry_v1.md` |

---

## Strategy Router (six rules)

Evaluate top-down; first match wins.

```text
R1  IF task = HBB enrichment re-run OR post-hoc estimand switch
    THEN REJECT → Decision=STOPPED
    (T/C already NOT_SUPPORTED; no more p-fishing)

R2  IF task = promote PWM / new p-value cosmetics without new primary
    THEN REJECT → Decision=BLOCKED

R3  IF admitted primary missing (ARCHCODE OR validated 2nd type e.g. AlphaGenome)
    THEN ALLOW only: desk / stubs / docs / sealed-holdout fetch
    FORBID: holdout scoring, shortlist freeze, wet-lab GO

R4  IF primary admitted AND leakage audit PASS
    THEN ALLOW: shortlist ≤3 alleles + freeze G3–G9
    FORBID: lab until G1–G9 Decision=PASS

R5  IF G1–G9 PASS on a frozen candidate
    THEN ALLOW: unblind protocol draft → human gate → optional wet-lab dossier
    ELSE: Decision=NO-GO (not “almost”)

R6  IF architecture claim lacks WT contact AND mechanism (H1–H4 immature)
    THEN Decision=IMMATURE — cultivate; do not Kill whole Track A idea
    Kill Loop remains for leakage / confounded / overclaim only
```

---

## Evidence levels

```text
E0  idea
E1  observation
E2  matched association          ← HBB T/C closed here (NOT_SUPPORTED)
E3  untouched holdout prep       ← fetch COMPLETE; scoring FORBIDDEN until gates
E4  independent replication      ← second code/analyst/dataset (I1–I3)
E5  causal intervention          ← edit → occupancy → contact (lab)
```

**Productivity rule:** do not spend calendar days on work above the currently open ceiling.  
**Open now:** ≤ E2 desk / E3 prep. **Closed:** E4–E5 until primary + freezes.

---

## Independence types (do not treat as interchangeable)

```text
I1  other code / model
I2  other analyst
I3  other dataset          ← sealed holdout
I4  other measurement      ← activity vs architecture
I5  physical experiment    ← BLOCKED until G1–G9
```

Lean ≠ Python ≠ Human. Record which Ix a check actually provides.

---

## Stopping matrix (instead of EVSI)

| Condition | Action |
|-----------|--------|
| HBB enrichment again | **STOP** |
| No admitted primary | desk / stubs only |
| ARCHCODE or AlphaGenome becomes AVAILABLE | GO admission gates |
| Candidate without WT contact / mechanism | IMMATURE / NO-GO lab |
| Any of G1–G6 FAIL | NO-GO |
| Only cosmetic robustness left | **STOP** branch |
| Cannot distinguish hypothesis vs alternative | redesign test (not more scores) |
| Result failed MCID / pre-registered endpoint | close & register null |

---

## Executable state line

```text
INTAKE → ROUTED → (desk | admission) → CLAIM_FROZEN → TEST_FROZEN
       → DATA_SEALED → EXECUTED → AUDITED → DECIDED → REGISTERED → STOPPED
```

Current project pin:

```text
ROUTED: high-risk
CLAIM: CURRENT CLAIM STOPPED (enrichment)
PRIMARY ADMISSION: FAIL / UNAVAILABLE
HOLDOUT: DATA_SEALED (unblind_authorized=false)
CULTIVATION: IMMATURE (≤ H3 desk)
WET-LAB: STOPPED
```

---

## Default weekly queue (productivity)

1. Unlock **R4**: supply ARCHCODE binary **or** AlphaGenome credentials → admission.  
2. While waiting: desk G4 (public E–P/contact for L-HO_*) + unblind protocol **draft only**.  
3. Never score sealed holdout. Never re-open HBB enrichment.

---

## Decision vocabulary (machine-readable)

Use only:

```text
PASS | FAIL | IMMATURE | BLOCKED | STOPPED | NO-GO | ALLOW | REJECT
```

Every registry row must end with one of these + evidence level (E0–E5) + independence tags (I*).
