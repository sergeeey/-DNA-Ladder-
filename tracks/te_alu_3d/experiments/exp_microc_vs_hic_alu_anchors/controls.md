# Controls — exp_microc_vs_hic_alu_anchors (C-I1)

**Status:** PREREGISTERED (2026-07-20) — T0 before downloads  
**Parent:** `claim.md`

## Matching / gates (if T0 PASS)

| Control | Rule |
|---------|------|
| Cell match | Micro-C and Hi-C same biosample |
| CTCF positive gate | OR(CTCF∩anchor) ≥ 2.0 on both assays (same as C-A1 spirit) |
| AluJo contrast | Exploratory negative / FP calibration (not primary) |
| umap ≥ 0.3 | Kill-test sensitivity; OR < 1.1 → REJECT |
| Primary TE | AluSz exact `repName` |

## Checklist

- [x] claim.md before OR
- [ ] T0 Micro-C bedpe probe
- [ ] ACCESSION_FREEZE if PASS
- [ ] OR after freeze
