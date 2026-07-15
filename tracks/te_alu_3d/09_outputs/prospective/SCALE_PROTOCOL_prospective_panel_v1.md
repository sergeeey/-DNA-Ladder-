# Scale protocol v1 — prospective panel (процесс, не доказательство C1)

**Date:** 2026-07-15  
**Status:** `PROTOCOL_DESK_ACTIVE`  
**Purpose:** масштабировать **строгий процесс** отбора и проверки, а не утверждение про C1  
**Role of C1:** **development template** (первый прогон ворот) · не единственное доказательство · не источник post-hoc правил панели

---

## 1. Что масштабируем

```text
вариант
→ контекст клетки
→ замороженный claim
→ проверка WT-контакта
→ editability
→ off-target audit
→ activity-тест
→ 3D-тест
→ PASS / FAIL / INCONCLUSIVE
```

C1 показал, что этот шаблон **исполним на desk**. Он **не** показал architecture-only эффект in cells.

**Forbidden scale error:** подобрать панель так, чтобы «подтвердить C1» или ARCHCODE.

**Allowed scale goal:** проверить, способен ли pipeline отбирать содержательные кандидаты и разделять M3 vs M1.

---

## 2. Целевая структура панели (после Stage 1)

Оптимальный состав **frozen** кандидатов (не desk-пул):

| Класс | n (цель) | Роль |
|-------|---------:|------|
| Activity prior (M3-lean) | 3–5 | локальная последовательность / TF / reporter |
| Architecture prior (M1-lean) | 3–5 | WT contact + anchor logic |
| Matched negative controls | 3 | matched TE/GC/ATAC/distance; ожидание null |
| Known positive control | 1 | известный erythroid architecture break (напр. 3′HS1-class / planted P1) |

Итого типично **~10–14** слотов в frozen panel; desk-screen шире (см. этап 1).

---

## 3. Единые ворота (каждый новый вариант)

| Gate | Требование | Fail → |
|------|------------|--------|
| **G0** | GRCh38; качественный call; не blacklist / segdup / low-map | reject |
| **G1** | релевантный клеточный тип (default: HUDEP-2 erythroid) | reject or defer |
| **G2** | наблюдаемый WT regulatory context **или** контакт в нужном клеточном состоянии | stay computational |
| **G3** | конкретный предполагаемый механизм (M1/M2/M3/…) + конкуренты | stay computational |
| **G4** | score **без** ClinVar / consequence leakage; holdout unused | reject scoring path |
| **G5** | технически редактируем (BE or PE path desk) | activity-only track possible; no allele-edit 3D |
| **G6** | можно подобрать matched controls | reject panel admission |
| **G7** | заранее заданы направление эффекта **или** явный UNKNOWN + MCID | amend before freeze |
| **G8** | claim + координаты (E/P или reporter window) заморожены **до** результата | reject / rework |

Без понятного механизма **или** WT-контекста вариант остаётся `computational_candidate` и **не** входит в frozen confirmatory panel.

Связь с C1-шаблоном: C1 прошёл desk-эквиваленты G0–G8 для development; G7 direction для контакта был UNKNOWN (допустимо при явном MCID); wet G5/G8 execution ещё NO-GO.

---

## 4. Два класса кандидатов (pre-register)

### 4.1 Convergence candidates

```text
ARCHCODE (exploratory OK)
+ motif / activity model
+ наблюдаемые данные (ChIP / contact / ATAC)
+ релевантный cell type
```

Более безопасный набор для калибровки pipeline.

### 4.2 Principled disagreement candidates

```text
ARCHCODE (или architecture prior): положительный
обычные sequence / activity-модели: отрицательные / слабые
но есть явный anchor / contact mechanism (G2)
```

Кандидаты на предполагаемый **3D blind spot**. Требуют **более строгий** эксперимент (обычно stage 3), не автоматический reject.

**Правило:** нельзя отбрасывать вариант **только** потому что AlphaGenome / PWM / другой predictor его не поддержал — если расхождение **заранее зарегистрировано** как disagreement class.

ARCHCODE в этой шкале: **exploratory prior**, не независимая научная валидация (см. archcode admission notes).

---

## 5. Три этапа масштаба (без самообмана)

### Этап 1 — desk-screen (дешёвый)

**Вход:** 20–50 вариантов (non-holdout; enrichment STOPPED как discovery engine).  
**Делать только:**

- QC (G0)  
- cell-type match (G1)  
- WT contact / context (G2)  
- mechanism class (G3)  
- editability (G5)  
- off-target risk proxy  
- независимые baselines (G4 discipline)

**Выход:** 8–12 вариантов → кандидаты в **frozen panel** (ещё не wet).

### Этап 2 — activity screen

Для frozen panel (или её activity-слота):

```text
REF vs ALT reporter
```

Разделяет:

- сильные локальные activity-effects  
- reporter-null  
- технически нестабильные конструкции  

**Reporter-null ≠ architecture PASS.**  
C1 Branch B = шаблон этапа 2.

### Этап 3 — глубокий 3D-тест

PE + Capture-C / MCC **только** для **2–4** заранее выбранных вариантов, если:

- есть наблюдаемый WT-контакт  
- высокий architecture prior  
- нет очевидного activity-only объяснения *или* disagreement заранее зарегистрирован  
- приемлемый OT-профиль  

C1 G4b / PE pack = шаблон этапа 3 для **одного** слота.

---

## 6. Pre-registered advancement rule (анти-shopping)

**Запрещено:** после reporter выбрать «самые красивые» и назвать их исходной confirmatory 3D-панелью.

**Заморозить до Stage 2 results** (записать в registry до первого reporter readout):

```text
В 3D-фазу (Stage 3) переходят фиксированные слоты:
  - два strongest architecture candidates   (pre-ranked by Stage-1 architecture scorecard)
  - один convergence candidate
  - один disagreement candidate
  - один negative control
```

Подстановки:

- допустимы только по **заранее** написанным fail-conditions (нередактируем; assay blind; OT fail);  
- запрещены по величине reporter effect или «интересности» post-hoc.

Реестр слотов: `prospective_panel_registry_v1.yaml`.

---

## 7. Сценарии научной новизны (панель, не одиночный C1)

| Сценарий | Паттерн | Интерпретация |
|----------|---------|---------------|
| **A** Architecture-only class | несколько: reporter− / contact+ / expression± | отдельный класс пространственных вариантов |
| **B** Mixed | reporter+ / contact+ | activity и architecture не взаимоисключающи |
| **C** Activity-driven | почти все effects = reporter | ослабляет сильную ARCHCODE-версию; даёт границу |
| **D** Null panel | никто не проходит MCID | architecture-only редки **или** pipeline их не ловит |

Любой сценарий — научный результат при pre-registration.

---

## 8. Что это даёт (и чего ещё нет)

**Метод (цель шкалы):**

- проверять некодирующие варианты;  
- разделять activity и 3D;  
- не путать score с патогенностью;  
- приоритизировать VUS для лабы;  
- регистрировать отрицательные исходы.

**Клиническая польза — только после:**

```text
несколько вариантов
→ независимые клеточные эксперименты
→ воспроизводимость
→ связь с экспрессией
→ связь с фенотипом
```

До этого язык остаётся: pipeline / candidacy / mechanism class — не pathogenicity.

---

## 9. Рекомендуемый численный масштаб (v1)

```text
20–30 desk-кандидатов          (Stage 1)
→ 8–12 frozen candidates
→ 6–8 reporter tests           (Stage 2)
→ 2–4 PE / Capture-C tests     (Stage 3, pre-registered slots)
→ 1 независимый holdout set    (SEALED until protocol GO; confirmatory only)
```

**C1** занимает слот: `TEMPLATE_DEV` / optional later Stage-3 architecture slot **only if** pre-registered (не автоматически «лучший»).

---

## 10. Hard stops

```text
- Holdout SEALED until explicit unblind protocol GO
- No ClinVar / consequence leakage into ranking (G4)
- No E/P or claim shopping after seeing allele results (G8)
- No promoting ARCHCODE to independent validation
- No calling panel results "pathogenic" / clinical actionability
- Enrichment track remains STOPPED as discovery engine
- Wet GO still per-phase signed notes (B0 / A1 / A2 template from C1)
```

---

## 11. Immediate next desk work (после принятия этого протокола)

1. Заполнить `prospective_panel_registry_v1.yaml`: слоты + pre-registered Stage-3 rule.  
2. Собрать desk-пул 20–30 (non-holdout) с одинаковыми G0–G3 карточками.  
3. Не заказывать oligos до отдельного panel GO (C1 B0 signature остаётся независимым решением).  
4. Держать C1 pack как template reference, не как единственный prior для всех правил.

---

## Linked

- `C1_claim_freeze_pack_v1.md` — template instance  
- `NDE_C1_exhaustion_A_plus_B_v1.md` — mechanism map for one locus  
- `GO_note_draft_C1_B_first_v1.md` — phase pattern for wet authorization  
- `WORK_REPORT_C1_desk_2026-07-15.md`  
- `prospective_panel_registry_v1.yaml`  
- `templates/G3_candidate_rationale.md`, `templates/G7_frozen_claim_registry.md`  
