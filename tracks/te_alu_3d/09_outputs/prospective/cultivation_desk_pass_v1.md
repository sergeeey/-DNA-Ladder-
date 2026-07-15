# Cultivation desk-pass v1 — architecture locus shortlist (no alleles frozen)

**Date:** 2026-07-13  
**Maturity:** H1 → **H3** (competing mechanisms). Desk G4 locus anchors **PARTIAL** (2026-07-14). **Not H6.** No wet-lab GO.  
**Forbidden:** scoring `data/holdout/`, using HBB T/C to pick alleles, claiming 3D disruption.  
**Desk artifacts:** `G4_contact_desk_pass_v1.md` · `07_methods/unblind_protocol_draft_v1.md`

---

## 1. Raw observation (H0) — restated

Erythroid CTCF-dense non-HBB windows on chr11 are pre-registered as holdout geography. They are plausible places where an allele *could* sit in an architectural element. This is not evidence that any allele does.

---

## 2. Weak hypothesis (H1)

A rare SNV in an Alu/SVA overlapping an occupied HUDEP-2 CTCF context in a non-HBB erythroid window could alter a local enhancer–promoter contact via a defined mechanism.

---

## 3. Locus geography shortlist (desk only)

These IDs are **windows**, not variants. Taken from sealed holdout manifest rationale (public CTCF-density), without reading holdout variant files for ranking.

| Locus ID | Window | Why shortlisted | Allele V | Status |
|----------|--------|-----------------|----------|--------|
| L-HO_A | chr11:65–66 Mb | top HUDEP-2 CTCF density (non-HBB) | **UNKNOWN** | geography only |
| L-HO_B | chr11:67–68 Mb | second dense bin | **UNKNOWN** | geography only |
| L-HO_C | chr11:64–65 Mb | panel diversity | **UNKNOWN** | geography only |

**Excluded:** HBB 5.2–5.3 Mb (development, labels viewed).

---

## 4. Mechanism candidates (H2→H3)

For any future allele in L-HO_* preferred default class is **M1** (CTCF anchor), with mandatory competitors:

| ID | Mechanism | Why live here | Discriminator later |
|----|-----------|---------------|---------------------|
| M1 | CTCF motif/orientation at occupied peak | Windows chosen for CTCF density | Allele-specific CTCF occupancy |
| M2 | Cohesin without CTCF motif loss | Possible in dense cohesin/CTCF neighborhoods | RAD21 Δ with stable CTCF |
| M3 | Enhancer activity | Dense regulatory landscape | Activity model / reporter |
| M4 | Promoter/splice | Must rule out | Splice/promoter annotation |
| M5 | Edit artifact | Always | Independent edits + neutrals |

**Preferred cultivation target class:** M1, with M3 and M5 as required competitors before freeze.

---

## 5. What is still UNKNOWN (blocks H4–H6)

| Item | Status |
|------|--------|
| Concrete variant V | UNKNOWN — needs leakage-free primary ranking |
| Elements E and P | UNKNOWN — anchors PARTIAL (`G4_contact_desk_pass_v1`); named E–P still gap |
| Direction / min effect | UNKNOWN — G7 empty |
| Beat motif/distance (G2) | IMMATURE — no primary |
| AlphaGenome / Arm A/B instance | BLOCKED — no credentials / no scores |
| G5 editability | UNKNOWN — no allele |
| G9 immutable freeze | EMPTY_SHELL |

---

## 6. Promotion decision

```text
H3: PASS (mechanisms competing, locus geography named)
H4: NOT YET (no discriminating predictions tied to a real allele)
H5: NOT YET
H6: NOT YET → wet-lab GO = STOPPED
```

**NO_GO_FOR_WET_LAB** remains in force: confirmatory primary UNAVAILABLE (`second_scorer_admission`).

---

## 7. Next operation when unblocked

1. Admit ARCHCODE or AlphaGenome (`second_scorer_admission_gate.py` → AVAILABLE)  
2. Build leakage-free universe on **non-holdout** erythroid panels OR unblind protocol for holdout  
3. Rank without ClinVar labels; require G2 beat baselines  
4. Pick ≤3 alleles in one L-HO_* window; fill G3–G9; classify Arm A/B  
5. Only then freeze G9
