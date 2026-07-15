# P3 — Matched-null panel ×13

**Date:** 2026-07-15
**Status:** `P3_MATCHED_NULL_COMPLETE`
**Claim (pre-registered):** `P3_matched_null_CLAIM_v1.md`
**Machine:** `P3_matched_null_panel_v1.json`

## Panel-level

- `PANEL_ACTIVITY_CLAIM_WEAKENED`: **False** (activity KILL_HP_DEMOTION count = 1)
- `PANEL_NEGATIVE_BROKEN`: **False**

## Per-candidate

| Variant | Role | Endp | Level | n_ctrl | Score | Eff | Pct | p_perm | Verdict |
|---------|------|------|------:|-------:|------:|----:|----:|-------:|---------|
| `chr11:62753923:A:G` | TEMPLATE_DEV | chip_tf | L3 | 9 | 0.5408 | +0.3737 | 95.0 | 0.101 | **INCONCLUSIVE** |
| `chr11:62753923:A:T` | activity_m3 | chip_tf | L3 | 9 | 0.2552 | +0.0881 | 75.0 | 0.299 | **INCONCLUSIVE** |
| `chr11:72434037:C:T` | activity_m3 | chip_tf | L3 | 9 | 0.2714 | +0.1043 | 85.0 | 0.202 | **INCONCLUSIVE** |
| `chr11:72434037:C:A` | activity_m3 | chip_tf | L3 | 9 | 0.2416 | +0.0745 | 65.0 | 0.407 | **KILL_HP_DEMOTION** |
| `chr11:114036577:G:C` | activity_m3 | chip_tf | L3 | 5 | 0.1661 | +0.0528 | 91.7 | 0.160 | **INCONCLUSIVE** |
| `chr11:75445532:G:A` | architecture_m1 | contact | L3 | 5 | 0.0017 | +0.0006 | 91.7 | 0.164 | **INCONCLUSIVE** |
| `chr11:518575:C:A` | architecture_m1 | contact | L4 | 5 | 0.0018 | -0.0008 | 41.7 | 0.669 | **KILL_HP_DEMOTION** |
| `chr11:119030718:C:T` | architecture_m1 | contact | L4 | 5 | 0.0012 | -0.0015 | 25.0 | 0.835 | **KILL_HP_DEMOTION** |
| `chr11:75445269:C:T` | architecture_m1 | contact | L3 | 5 | 0.0013 | +0.0002 | 58.3 | 0.498 | **KILL_HP_DEMOTION** |
| `chr11:108009167:T:C` | matched_negative | chip_tf | L4 | 20 | 0.1091 | -0.0471 | 16.7 | 0.854 | **PASS_AS_NEGATIVE** |
| `chr11:108009167:T:A` | matched_negative | chip_tf | L4 | 20 | 0.1657 | +0.0095 | 50.0 | 0.527 | **PASS_AS_NEGATIVE** |
| `P1_SYSTEM_3primeHS1` | known_positive | — | — | — | — | — | — | — | **SKIP** |
| `chr11:57568168:C:T` | principled_disagreement | chip_tf | L3 | 9 | 0.1297 | -0.1119 | 15.0 | 0.902 | **KILL_HP_DEMOTION** |

## Plain language

Сравниваем каждый из 13 не с «всем миром», а с похожими Alu/SVA аллелями (семейство/клада, дистанция до CTCF, блок хроматина, тип замены). Если «хит» не выделяется на этом фоне — снимаем high-priority, не лабораторный GO.

## What this does NOT mean

- Not wet-lab proof or kill of biology
- Not permission to reopen holdout or reshape Stage-3
- Pool n=28 limits L1/L2; thin matches force INCONCLUSIVE by design
