# P3 expand — null-universe growth for L1/L2

**Date:** 2026-07-15  
**Goal:** enable pre-registered L1/L2 matched sets (≥5 controls) for frozen panel  
**Claim thresholds:** unchanged (`P3_matched_null_CLAIM_v1.md`)

## What ran

| Step | Result |
|------|--------|
| Broad gnomAD expand + AG | +40 SCORED (`expand_p3_null_universe.py`, budget 40) |
| L2-targeted neighborhood AG | further SCORED near frozen clades/blocks (`expand_p3_l2_targeted.py`) |
| Universe size | **28 → 115** SCORED (`p3_expanded_universe_v1.json`) |
| Re-test | `P3_matched_null_panel_v2.md` |

## Outcome vs goal

**L2 unlocked** for several frozen slots (L1 still rare / often 0).

| Rule | v1 (n=28) | v2 (n=115) |
|------|-----------|------------|
| C1 match level | L3 → INCONCLUSIVE | **L2 → RETAIN_HP** (pct 93.8, effect +0.41) |
| C2 / C3 / C3b | L3 | **L2 → RETAIN_HP** |
| A114 | L3 | L2 → INCONCLUSIVE (pct 83.3 < 90) |
| Architecture slots | mostly demotion | still mostly **KILL_HP_DEMOTION** |
| Negatives | PASS | N3 T>C **PASS**; companion T>A **INCONCLUSIVE** (pct 60) |
| `PANEL_ACTIVITY_CLAIM_WEAKENED` | False | **False** |
| `PANEL_NEGATIVE_BROKEN` | False | **False** |

## Plain language

После расширения фона C1/C2/C3 формально проходят pre-registered high-priority matched-null на L2. Это **не** wet-lab proof и **не** повод открывать holdout / Stage-3. Architecture-lean слоты на contact-фоне по-прежнему слабые.

## Arts

- `p3_expanded_universe_v1.json`
- `P3_matched_null_panel_v1.md` (baseline n=28)
- `P3_matched_null_panel_v2.md` / `.json` (expanded)
- `P3_EXPAND_REPORT_v1.md`
- scripts: `expand_p3_null_universe.py`, `expand_p3_l2_targeted.py`
