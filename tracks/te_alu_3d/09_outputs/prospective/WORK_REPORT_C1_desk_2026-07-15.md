# Отчёт о проделанной работе — Track A / кандидат C1

**Проект:** DNA_TE_3DGenome_Context (DNA Ladder / rare Alu–SVA vs архитектура)  
**Период:** desk-кампания по C1, итог на **2026-07-15**  
**Режим:** вычислительная подготовка и freeze документов  
**Wet-lab / заказ олиго:** **NO-GO** (без человеческой подписи Phase B0/A1)

---

## 1. Итог одной фразой

Подготовлен полный **desk-пакет** для dual-track проверки кандидата **C1** (`chr11:62753923 A>G`): зафиксированы claim и якоря E–P, подтверждён WT-контакт в HUDEP-2, заморожен протокол Capture-C, спроектирован prime editing (PD1) с genome-wide OT, спроектирован activity-reporter, прогнаны narrow-discovery engines под A+B, оформлены unsigned GO-note, чеклисты и OT-праймеры. Биологический эффект C1 **не доказан**; утверждение «C1 рвёт петлю» **запрещено**.

---

## 2. Цель и рамки

| Вопрос | Статус |
|--------|--------|
| Есть ли у C1 правдоподобный путь редактирования? | Да (PE PD1, desk) |
| Меняет ли C1 активность последовательности (M3)? | Не проверено; Branch B готов |
| Меняет ли C1 контакт E–P (M1)? | Не проверено; G4b протокол готов |
| Можно ли заказывать реактивы / клетки? | **Нет** — нет подписанного GO |

**Holdout:** SEALED.  
**ARCHCODE:** только EXPLORATORY, не независимая валидация.

---

## 3. Что сделано по блокам

### 3.1. Научный freeze кандидата

- Зафиксирован C1: GRCh38 `chr11:62753923 A>G` (hg19 `chr11:62521395`), AluSz.  
- Primary механизм: **M3 activity**; архитектура **условная** (M1 if G4b PASS).  
- Locked anchors (не пересобирать после просмотра данных):  
  - E `chr11:62390000-62395000`  
  - P `chr11:62690000-62695000`  
- Запретный claim до G4b: «C1 нарушает E–P loop в HUDEP-2».  
- Артефакт: `C1_claim_freeze_pack_v1.md`.

### 3.2. Архитектурная ветка A (desk)

| Гейт | Результат |
|------|-----------|
| G4a WT Contact(E,P) HUDEP-2 Hi-C `GSM4873113` | **PASS_DESK** (~3.4× vs same-distance bg; OE~3.2; один .hic) |
| P1-system 3′HS1 (WT vs del/inv) | **PASS_DESK** (DEL/WT OE HS1–HS5 ≈0.34) |
| Данные GSE160422 | GSM4873113–3118 на диске + SHA256 |
| G4b allele ΔContact | **PROTOCOL_DESK_FROZEN** (Capture-C primary; MCID \|ΔContact\|≥25% WT или \|ΔOE\|≥0.5) |
| P1-local CTCF HUDEP-2 | Номинирован P-side peak `chr11:62694751-62695044` |
| G4b в клетках | **NOT TESTED** |

### 3.3. Редактирование (G5 PE)

| Шаг | Результат |
|-----|-----------|
| Classic BE | **FAIL** (окно не подходит) |
| Heuristic PE shortlist | 24 геометрии; top spacer `CGTCCGATAAGCCCTGCCCC` |
| PrimeDesign CLI | **PASS** — PD1 совпал |
| CRISPOR hg38 (PD1) | MIT **69**, CFD **89**; mm 0/0/0/6/115 → **CONDITIONAL_PASS** |
| Watch | **exon:RADIL** (mm3); высокий CFD intron:KDM2B |
| PE3 ngRNA | Prefer `GTTCTAAGGTTAGGCCGAGG` (MIT91, nick −46) |

### 3.4. Activity ветка B (desk)

- Reporter windows REF/ALT: 301 bp / 1 kb / 2 kb FASTA на диске.  
- MCID: \|log2(ALT/REF)\| ≥ 0.5, ≥2 трансфекции.  
- Ближайшие гены к C1 (не claim target): ZBTB3, POLR2G, …  
- Checklist олиго: `BranchB_oligo_checklist_v1.md` (лестница 301→1kb→2kb).

### 3.5. Narrow Discovery Engines (перед A+B)

| Engine | Решение |
|--------|---------|
| **4 Exhaustion** | Alive high-prior: **{M3, M1, M0}**; A/B — дифференцирующие тесты |
| **2 Constraint relaxation** | B без PE; escalation reporter; OT panel обязателен при PE |
| 1 / 3 | Отложены (нет orphan-панели / нет лабораторной аномалии) |

Артефакт: `NDE_C1_exhaustion_A_plus_B_v1.md`.

### 3.6. Пакет готовности к лабе (без авторизации)

| Документ | Назначение | Статус |
|----------|------------|--------|
| `GO_note_draft_C1_B_first_v1.md` | B0 → A1 → A2 | **UNSIGNED** = NO-GO |
| `BranchB_oligo_checklist_v1.md` | список для будущего PO | заказ запрещён |
| `CaptureC_bait_quote_sheet_v1.md` | смета baits E/P | quote only |
| `OT_amplicon_primer_panel_desk_v1.md` | C1, RADIL, KDM2B, RPAP2, UPF3A | desk; нужен Primer-BLAST |
| `HANDOFF_PLAIN_LANGUAGE.md` | объяснение без жаргона | готово |

### 3.7. TSS у locked P (desk)

- TSS внутри locked P: **нет**.  
- Ближайший TSS: **LRRN4CL** `chr11:62689530`.  
- Перекрытие тела гена с P: **BSCL2** / HNRNPUL2-BSCL2.  
- Нельзя назначать target gene C1 без HUDEP-2 RNA.

---

## 4. Машинный статус (текущий)

```text
architecture freeze:     PROVISIONAL_OPEN_LANGUAGE_ONLY
G4a / P1-system / G4b:   PASS_DESK / PASS_DESK / PROTOCOL_FROZEN (not in cells)
PE PD1 + ngRNA OT:       CONDITIONAL_PASS
Branch B design:         READY
NDE A+B:                 DONE — alive {M3, M1, M0}
GO-note:                 DRAFT UNSIGNED
wet-lab GO:              NO-GO
oligo / transfection:    FORBIDDEN
holdout:                 SEALED
```

---

## 5. Ключевые артефакты (навигация)

```text
09_outputs/prospective/
  C1_claim_freeze_pack_v1.md
  G4a_gsm4873113_desk_pass_v1.md
  P1_3primeHS1_desk_pass_v1.md
  G4b_protocol_freeze_v1.md
  G4b_bait_windows_locked.yaml
  G5_PE_shortlist_C1_desk_v1.md
  G5_PE_validation_external_C1_v1.md
  G5_PE_OT_CRISPOR_PD1_v1.md
  BranchB_reporter_design_v1.md
  BranchB_oligo_checklist_v1.md
  NDE_C1_exhaustion_A_plus_B_v1.md
  GO_note_draft_C1_B_first_v1.md
  CaptureC_bait_quote_sheet_v1.md
  OT_amplicon_primer_panel_desk_v1.md
  ot_amplicon_primers_desk_v1.json
  HANDOFF_PLAIN_LANGUAGE.md
  PAUSE_PIN_2026-07-14.md
  WORK_REPORT_C1_desk_2026-07-15.md   ← этот файл
```

Данные: `D:\DNK - 2\data\HUDEP2_GSE160422\`  
Инструменты: JDK/juicer_tools, PrimeDesign CLI, `design_ot_amplicon_primers_v1.py`.

---

## 6. Чего сознательно не делали

- Не заказывали олиго, не трансфецировали, не запускали Capture-C в клетках.  
- Не unblind’или holdout.  
- Не пересобирали E/P после данных.  
- Не выдавали ARCHCODE за независимую 3D-валидацию.  
- Не утверждали off-target в RADIL — только **кандидат на проверку**.

---

## 7. Риски и ограничения

| Риск | Комментарий |
|------|-------------|
| G4a без репликата Hi-C | PASS_DESK, не финальная биологическая уверенность |
| Alu-контекст PE | Повышенный OT-риск; mm≤2 нет, mm3–4 есть |
| KDM2B OT-ампликон | polyA внутри — возможен плохой PCR |
| Locked P без TSS | P может быть в теле BSCL2; ген-мишень не назначен |
| Раздельность A и B | Reporter ≠ петля; петля ≠ activity |

---

## 8. Что дальше (решения человека)

1. **Подписать Phase B0** → можно планировать заказ reporter (после freeze backbone).  
2. **Остаться NO-GO** → кандидат сохранён как desk-пакет.  
3. При будущем A1: Primer-BLAST OT-панели → отдельная подпись A1 → только потом PE.  
4. Capture-C: сначала quote sheet вендору, синтез — только после A1 edit PASS + A2 GO.

---

## 9. Вердикт

**Desk-работа по C1 для веток A+B завершена до естественного стопа:** всё, что можно честно сделать на компьютере без wet-lab и без вскрытия holdout, оформлено и заморожено.  
**Научный прогресс:** от «кандидат с AG M3-lean» до «исполняемый dual-track план с MCID, edit-path, OT-watchlist и differentiating matrix».  
**Не достигнуто (по дизайну):** доказательство эффекта C1 in cells.

---

*Отчёт составлен 2026-07-15. Источники статусов: PAUSE_PIN, Changelog, Tasktracker, claim freeze, NDE, GO-note.*
