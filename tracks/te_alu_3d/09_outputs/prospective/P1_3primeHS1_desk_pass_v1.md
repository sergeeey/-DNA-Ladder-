# P1-system desk — 3′HS1 (GSE160422 / eLife 70557)

**Date:** 2026-07-14  
**Role:** architecture positive control in HUDEP-2 (same system as G4a)  
**Verdict:** `PASS_DESK`

## What P1 must show

```text
P1 edit verified
AND CTCF occupancy changes (paper CUT&RUN)
AND contact changes in predicted direction (local dump)
AND assay detects effect reproducibly
```

Expression desirable, not required for technical architecture P1.

## Local dump table (OE KR, 5 kb)

| sample | status | bytes | OE HS1–HS5 | OE HBB–OR52A1 | obs HS1–HS5 |
|--------|--------|------:|------------:|--------------:|------------:|
| WT | OK | 7112676977 | 3.2253135 | 2.211311 | 4.958853825 |
| DEL_B6 | OK | 7090244948 | 1.1058755 | 3.4652506 | 1.5665237333333333 |
| INV_A2 | OK | 6909061208 | 1.87469915 | 1.73445705 | 2.8009687999999997 |
| CAP_WT | DUMP_EMPTY | 2467765796 | — | — | — |
| CAP_DEL | OK | 2487625662 | 0.4024290225 | 0.69494105 | 0.11757254624999999 |
| CAP_INV | OK | 2274698584 | 0.8822062875 | 0.63601045 | 0.2516258675 |

## Ratios (DEL/WT)

- OE HS1–HS5: `0.34287380125993955`
- OE HBB–OR52A1: `1.567057098707509`
- Capture OE HS1–HS5: `None`

## Literature grounding

- Paper verifies CRISPR del/inv, CTCF CUT&RUN loss/gain, Hi-C/Capture changes, HbF phenotype.
- This is **P1-system** (β-globin), not P1-local at C1.
- If local dump PASS_DESK → assay chain trusted in HUDEP-2 Hi-C.
- Planted local P1 near C1 still recommended before over-interpreting C1 architecture magnitude.

## Gate impact

| Gate | Effect of this P1 |
|------|-------------------|
| Architecture freeze | may unlock **provisional** freeze *language* with G4a PASS_DESK |
| Wet-lab GO for C1 edit | still needs G5 editability + G4b plan + endpoints |
| Activity Branch B | remains available |

JSON: `P1_3primeHS1_metrics.json`
