# P4 — Independent model matrix v1

**Date:** 2026-07-16
**Status:** `P4_INDEPENDENT_MODEL_COMPLETE`
**Claim:** `P4_INDEPENDENT_MODEL_CLAIM_v1.md`
**Label:** **`P4_MATRIX_COMPLETE`**
**Alleles:** 12 (P1 system control excluded — not an SNV row)

## Class counts

| Class | n |
|-------|--:|
| `convergence` | 5 |
| `negative_consistent` | 2 |
| `principled_disagreement` | 3 |
| `unsupported` | 2 |

## Matrix

| ID | Variant | Role | P4 class | Motif | Dist | AG CHIP | AG contact | WT contact |
|----|---------|------|----------|------:|-----:|--------:|-----------:|------------|
| C1 | `chr11:62753923:A:G` | development_template | **convergence** | 0.065 | 1.000 | 0.541 | 0.0049 | PASS_DESK_ROBUST |
| C2 | `chr11:62753923:A:T` | activity_m3 | **convergence** | 0.065 | 1.000 | 0.255 | 0.0021 | NOT_MEASURED_FOR_THIS_ALLELE |
| C3 | `chr11:72434037:C:T` | activity_m3 | **convergence** | 0.870 | 1.000 | 0.271 | 0.0016 | NOT_MEASURED_FOR_THIS_ALLELE |
| C3b | `chr11:72434037:C:A` | activity_m3 | **convergence** | 0.870 | 1.000 | 0.242 | 0.0015 | NOT_MEASURED_FOR_THIS_ALLELE |
| A114 | `chr11:114036577:G:C` | activity_m3 | **principled_disagreement** | 0.870 | 1.000 | 0.166 | 0.0016 | NOT_MEASURED_FOR_THIS_ALLELE |
| A754 | `chr11:75445532:G:A` | architecture_m1 | **principled_disagreement** | 0.870 | 1.000 | 0.135 | 0.0017 | NOT_MEASURED_FOR_THIS_ALLELE |
| A518 | `chr11:518575:C:A` | architecture_m1 | **convergence** | 0.870 | 0.500 | 0.215 | 0.0018 | NOT_MEASURED_FOR_THIS_ALLELE |
| A119 | `chr11:119030718:C:T` | architecture_m1 | **unsupported** | 0.065 | 0.500 | 0.145 | 0.0012 | NOT_MEASURED_FOR_THIS_ALLELE |
| A754b | `chr11:75445269:C:T` | architecture_m1 | **unsupported** | 0.065 | 1.000 | 0.113 | 0.0013 | NOT_MEASURED_FOR_THIS_ALLELE |
| N3 | `chr11:108009167:T:C` | matched_negative | **negative_consistent** | 0.065 | 1.000 | 0.109 | 0.0010 | NOT_MEASURED_FOR_THIS_ALLELE |
| N3b | `chr11:108009167:T:A` | matched_negative | **negative_consistent** | 0.065 | 1.000 | 0.166 | 0.0010 | NOT_MEASURED_FOR_THIS_ALLELE |
| W1 | `chr11:57568168:C:T` | principled_disagreement | **principled_disagreement** | 0.870 | 1.000 | 0.130 | 0.0012 | NOT_MEASURED_FOR_THIS_ALLELE |

## Independence honesty

| Pair | Note |
|------|------|
| AG CHIP vs AG contact | **same model family** — not independent evidence |
| Motif vs distance | share CTCF peak layer — partially dependent |
| ARCHCODE | **UNAVAILABLE** — exploratory prior lean only |
| G4a WT Hi-C | independent observational for **C1 E–P only** |

## C1 reading

C1: high AG activity + low motif + WT contact PASS → typically **convergence** via activity+WT rule (not motif convergence).

## Plain language

Таблица «кто с кем согласен» по frozen-панели. Согласие моделей ≠ лаборатория. ARCHCODE здесь не валидатор.

## What this does NOT mean

- Not wet GO / not Stage-3 reshuffle
- Not ARCHCODE validation
- Not allele-specific contact proof (except C1 WT contact desk)

Full dump: `P4_independent_model_matrix_v1.json`
