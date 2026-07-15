# Stage-1 desk-screen — результаты

**Date:** 2026-07-15  
**Status:** `STAGE1_DESK_COMPLETE_CURATED`  
**Protocol:** `SCALE_PROTOCOL_prospective_panel_v1.md`  
**Machine arts:** `stage1_desk_screen_v1.json`, `stage1_desk_screen_v1.tsv`

---

## Итог

```text
desk pool:     28 rare Alu/SVA SNV (chr11, non-holdout)
AG overlay:    12 prior R4 scores (API key ABSENT this run)
frozen panel:  13 slots (incl. P1 system positive + C1 template)
Stage-3 rule:  LOCKED before any reporter readout
holdout:       SEALED / untouched
wet-lab:       still NO-GO
```

Масштабирован **процесс**, не claim про C1. C1 = `TEMPLATE_DEV`, исключён из Stage-3 слотов.

---

## Что сделано автоматически

1. CTCF×Alu/SVA пики вне HBB + HO (64–68 Mb) → gnomAD r4 rare SNV (AF≤0.001, dist≤250).  
2. Overlay предыдущих AlphaGenome R4 scores (12 аллелей).  
3. Локальный CTCF-PWM (UCSC windows) + crude PE/BE editability.  
4. Ворота G0–G8; исправлен баг `dist_ctcf=0 → fail G2`.  
5. Курированная frozen-панель + **LOCKED** Stage-3 advancement.

Скрипты: `run_stage1_desk_screen.py`, `curate_stage1_panel_v1.py`.

---

## Frozen panel (n=13)

| Role | Variant | Mechanism | Note |
|------|---------|-----------|------|
| TEMPLATE_DEV | `chr11:62753923:A:G` **C1** | M3 | desk template; not Stage-3 auto-winner |
| activity_m3 | `chr11:62753923:A:T` **C2** | M3 | same-site amplitude |
| activity_m3 | `chr11:72434037:C:T` **C3** | M3 | motif competitor |
| activity_m3 | `chr11:72434037:C:A` | M3 | AG CHIP_TF lean |
| activity_m3 | `chr11:114036577:G:C` | M3 | AG CHIP_TF lean |
| architecture_m1 | `chr11:75445532:G:A` | M1 motif/anchor | allele contact untested |
| architecture_m1 | `chr11:518575:C:A` | M1 motif/anchor | |
| architecture_m1 | `chr11:119030718:C:T` | M1 motif/anchor | |
| architecture_m1 | `chr11:75445269:C:T` | M1 motif/anchor | |
| matched_negative | `chr11:108009167:T:C` **N3** | M0 lean | G6 KEEP |
| matched_negative | `chr11:108009167:T:A` | companion | same locus |
| known_positive | `P1_SYSTEM_3primeHS1` | M1 control | PASS_DESK historical |
| principled_disagreement | `chr11:57568168:C:T` | contact vs activity tension | pre-registered class |

**Excluded from architecture-strong:** N1/N2 (`35821778`, `35822097`) — G6 GC/ATAC DROP.

---

## Stage-3 advancement — LOCKED

```yaml
architecture_strong_1: chr11:75445532:G:A
architecture_strong_2: chr11:518575:C:A
convergence_1:         chr11:72434037:C:T   # C3, not C1
disagreement_1:        chr11:57568168:C:T
negative_1:            chr11:108009167:T:C  # N3
assignment_locked:     true
locked_date:           2026-07-15
C1_template:           excluded from Stage-3 slots
```

Подстановки только по fail-conditions протокола (не по «красоте» reporter).

---

## Рекомендуемый Stage-2 (reporter) — ещё без заказа

Приоритет REF/ALT reporter (6–8):

1. C1, C2, C3  
2. `114036577:G:C`  
3. `75445532:G:A` (arch)  
4. `518575:C:A` (arch)  
5. N3 `108009167:T:C` (ожидание near-null)  
6. disagreement `57568168:C:T`

Заказ олиго — только после signed GO (panel или C1 B0).

---

## Caveats (честные)

| Issue | Impact |
|-------|--------|
| ~~Нет AG key~~ → восстановлен в gitignored `.env` | **28/28 SCORED** (16 doscore OK); Stage-3 не перетасован |
| PWM часто \|Δ\|≈4.09 | ordinal exploratory; не единственный критерий Stage-3 |
| G2 = наличие CTCF peak | **не** allele ΔContact; G4b ещё впереди |
| PE desk = heuristic NGG | полный OT только у C1 PD1 |
| Все 28 после fix G2 = panel-candidate eligible | в frozen взяты только курированные 13 |

---

## Novelty path (панель)

После Stage-2/3 смотреть сценарии A–D из scale protocol (architecture-only / mixed / activity-driven / null) — **не** интерпретировать одиночный C1 как класс.

---

## Next

1. (Опционально) прогнать AG на 16 новых аллелей при появлении ключа.  
2. Desk: минимальные reporter windows для Stage-2 shortlist.  
3. Не начинать PE/Capture-C вне LOCKED Stage-3 слотов.  
4. Holdout по-прежнему SEALED.

## Linked

- `SCALE_PROTOCOL_prospective_panel_v1.md`  
- `prospective_panel_registry_v1.yaml`  
- `WORK_REPORT_C1_desk_2026-07-15.md`  
- `ag_cultivation_r4_scores.tsv`  
