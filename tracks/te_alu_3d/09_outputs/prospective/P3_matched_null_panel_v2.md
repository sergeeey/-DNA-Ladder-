# P3 — Matched-null panel ×13

**Date:** 2026-07-15
**Status:** `P3_MATCHED_NULL_COMPLETE`
**Claim (pre-registered):** `P3_matched_null_CLAIM_v1.md`
**Machine:** `P3_matched_null_panel_v2.json`

## Panel-level

- `PANEL_ACTIVITY_CLAIM_WEAKENED`: **False** (activity KILL_HP_DEMOTION count = 0)
- `PANEL_NEGATIVE_BROKEN`: **False**

## Per-candidate

| Variant | Role | Endp | Level | n_ctrl | Score | Eff | Pct | p_perm | Verdict |
|---------|------|------|------:|-------:|------:|----:|----:|-------:|---------|
| `chr11:62753923:A:G` | TEMPLATE_DEV | chip_tf | L2 | 7 | 0.5408 | +0.4121 | 93.8 | 0.123 | **RETAIN_HP** |
| `chr11:62753923:A:T` | activity_m3 | chip_tf | L2 | 7 | 0.2552 | +0.1265 | 93.8 | 0.120 | **RETAIN_HP** |
| `chr11:72434037:C:T` | activity_m3 | chip_tf | L2 | 13 | 0.2714 | +0.1379 | 96.4 | 0.070 | **RETAIN_HP** |
| `chr11:72434037:C:A` | activity_m3 | chip_tf | L2 | 13 | 0.2416 | +0.1081 | 96.4 | 0.073 | **RETAIN_HP** |
| `chr11:114036577:G:C` | activity_m3 | chip_tf | L2 | 8 | 0.1661 | +0.0633 | 83.3 | 0.229 | **INCONCLUSIVE** |
| `chr11:75445532:G:A` | architecture_m1 | contact | L2 | 6 | 0.0017 | +0.0003 | 64.3 | 0.432 | **KILL_HP_DEMOTION** |
| `chr11:518575:C:A` | architecture_m1 | contact | L4 | 29 | 0.0018 | +0.0003 | 55.0 | 0.470 | **KILL_HP_DEMOTION** |
| `chr11:119030718:C:T` | architecture_m1 | contact | L4 | 29 | 0.0012 | -0.0006 | 18.3 | 0.831 | **KILL_HP_DEMOTION** |
| `chr11:75445269:C:T` | architecture_m1 | contact | L2 | 6 | 0.0013 | -0.0004 | 35.7 | 0.715 | **KILL_HP_DEMOTION** |
| `chr11:108009167:T:C` | matched_negative | chip_tf | L4 | 81 | 0.1091 | -0.0284 | 22.6 | 0.775 | **PASS_AS_NEGATIVE** |
| `chr11:108009167:T:A` | matched_negative | chip_tf | L4 | 81 | 0.1657 | +0.0282 | 60.4 | 0.398 | **INCONCLUSIVE** |
| `P1_SYSTEM_3primeHS1` | known_positive | — | — | — | — | — | — | — | **SKIP** |
| `chr11:57568168:C:T` | principled_disagreement | chip_tf | L2 | 10 | 0.1297 | +0.0040 | 50.0 | 0.555 | **KILL_HP_DEMOTION** |

## Plain language

Сравниваем каждый из 13 не с «всем миром», а с похожими Alu/SVA аллелями (семейство/клада, дистанция до CTCF, блок хроматина, тип замены). Если «хит» не выделяется на этом фоне — снимаем high-priority, не лабораторный GO.

## What this does NOT mean

- Not wet-lab proof or kill of biology
- Not permission to reopen holdout or reshape Stage-3
- Pool n=28 limits L1/L2; thin matches force INCONCLUSIVE by design
- **v2 update:** universe n=115 unlocked L2 for C1/C2/C3 → see `P3_EXPAND_REPORT_v1.md`
