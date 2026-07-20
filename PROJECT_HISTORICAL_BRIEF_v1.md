# DNA Ladder — Historical and Scientific Status Brief

```yaml
snapshot_date: 2026-07-20
repository: https://github.com/sergeeey/-DNA-Ladder-
commit: 16a5217cfbc53a867100cc151962ba1b6dcbe345
branch: master
release_or_tag: null
report_version: "1.1"
scope: desk work only
wet_lab_authorization: NO-GO
```

**Статус на дату:** desk-фаза; wet-lab **NO-GO** (GO B0 не подписан)

**Кодировка:** UTF-8  
**Документ:** historical / scientific status brief (revision 1.1 after external review ~9/10 → publication-ready auditability)

---

## 1. Миссия

DNA Ladder — falsification-first тестирование гипотез об открытых вопросах ДНК на **реальных публичных данных**. Любой артефакт считается ложным, пока не пройдены: определение estimand → novelty check → тест на реальных данных → честный вердикт (REJECT / INCONCLUSIVE / CLOSED / PASS_DESK — без подмены знака).

Сиблинги:

| Проект | Роль |
|---|---|
| **ARCHCODE** (`ARCHCODE_review`) | Та же методология, другой (более узкий) домен; источник паттернов, bug classes и протокола |
| **Research Library** (`D:\Research Library\`) | Литература по DOI/ID; PDF сюда не дублируются |

Протокол (кратко, идентичен ARCHCODE): L0-классификация (Descriptive / Predictive / Causal) → novelty check (`null_results/` + литература) → pre-registered `claim.md` → только публичные данные → честные filing в `null_results/` при REJECT/INCONCLUSIVE.

---

## 2. Monorepo tracks

Репозиторий — monorepo (variant B): исследовательские программы в `tracks/<name>/`, общая governance и отрицательные результаты — в корне.

| Трек | Путь | Фокус |
|---|---|---|
| **SE / LLPS** | `tracks/se_llps/` | Super-enhancers, LLPS-коактиваторы, G4 / R-loop / constraint; в основном REJECT |
| **TE / Alu–3D** | `tracks/te_alu_3d/` | Редкие Alu/SVA SNV vs 3D-контакты и активность; C1 desk-template + scale protocol |
| **null_results** | `null_results/` | Общий индекс REJECT / INCONCLUSIVE / CLOSED по всем трекам |

Крупные бинарники (`.hic`, sealed holdout dumps, juicer jars) **не** коммитятся.

---

## 3. Claim status (на 2026-07-20)

| Claim | Status |
|---|---|
| SE membership объясняет выбранные estimands | REJECTED in tested scope |
| Rare TE variants enriched for disruption at HBB | NOT SUPPORTED |
| WT E–P contact exists in HUDEP-2-related Hi-C dataset | PASS_DESK |
| C1 allele lean retained after satmut desk | ALLELE_LEAN_RETAINED (desk only) |
| Capture-C powered as primary readout | P8_UNDERPOWERED (not primary) |
| C1 changes activity (wet / reporter) | NOT TESTED |
| C1 changes E–P contact (allele effect) | NOT TESTED |
| C1 is pathogenic | NOT CLAIMED |

Desk-тесты не дали достаточного основания отвергнуть C1 как development template, но не подтвердили биологический эффект. C1 сохранил право на дальнейшую проверку после desk kill-sprint; wet-lab и патогенность не заявлены.

---

## 4. Словарь статусов / glossary

| Код | Операционное значение | Evidence |
|---|---|---|
| PASS_DESK_ROBUST | Multi-sample G4a contact check passed desk pre-registered kills | `tracks/te_alu_3d/09_outputs/prospective/KILL_SPRINT_RESULTS_v1.md` (P1) |
| ALLELE_LEAN_RETAINED | Saturation mutagenesis did not displace C1 allele priority | … P2 |
| RETAIN_HP | Matched-null panel: C1/C2/C3 retained at L2 | … P3 |
| P4_MATRIX_COMPLETE | Independent model matrix finished; C1 convergence noted | … P4 |
| R1_PASS | Reporter AG context-length ladder technical pass | … P5 |
| PE_OT_CONDITIONAL_PASS | PE/OT desk viable with RADIL watch | … P6 |
| P7_RANKED_EXPLORATORY | Target gene ranking exploratory only | … P7 |
| P8_ADEQUATE / P8_UNDERPOWERED | Reporter powered at n_tx=6; Capture not | … P8 |
| P9_GAPS | Virtual E2E coherent; soft gaps only; 0 hard blocks | … P9 |
| PRIMER_DESK_PASS / PRIMER_BLAT_DESK_PASS | OT primer panel isPCR+BLAT | `OT_amplicon_primer_panel_desk_v1.md` + primer arts |
| UNSIGNED_DRAFT / NO-GO | `date_signed` null → oligos forbidden | `GO_note_draft_C1_B_first_v1.md` |

```text
PASS_DESK ≠ wet-lab PASS
contact exists ≠ variant changes contact
candidate ≠ pathogenic variant
```

---

## 5. Хронология

| Дата | Событие |
|---|---|
| **2026-07-08** | Bootstrap: CLAUDE.md, RESEARCH_DIRECTIONS.md, `null_results/INDEX.md`; старт SE/LLPS (BRD4/MED1 ChIP; ClinVar VUS frequency) |
| **2026-07-10** | Кластер SE REJECT + **META CLOSED** (missing heritability): matched controls, Gnocchi, VUS, R-loop, G4, continuous-rank check |
| **2026-07-13** | TE: HBB enrichment **STOPPED** / Package A; holdout **SEALED** (`sealed_at: 2026-07-13`) |
| **2026-07-14** | RDR Router v1; ARCHCODE-PROSPECTIVE (FRAMEWORK_ONLY); путь культивации C1 |
| **2026-07-15** | C1 claim freeze (`chr11:62753923 A>G`, AluSz); NDE A+B; **kill-sprint P1–P10** |
| **2026-07-16** | Primer desk **PASS** (+ BLAT); **B0 ready pack UNSIGNED** (READY_FOR_SIGNATURE); PO draft; A1 later; A2 Capture HELD; P10 locked |
| **2026-07-20** | **Пауза:** desk готов к B0; человеческая подпись и wet-lab не открыты |

---

## 6. SE / LLPS — таблица вердиктов

| Направление | Вердикт | Ключевые числа / заметка |
|---|---|---|
| **LLPS** (BRD4/MED1 SE vs active chromatin) | **REJECT** | Matched H3K27ac: BRD4 ratio → ~1.05 (K562) / reverses (HepG2); MED1 splits; ENCODE исчерпан |
| **ClinVar VUS** (SE vs outside / vs typical) | **REJECT** | δ ≈ −0.01…−0.03 (outside); δ ≈ +0.008 / −0.019 (matched typical) |
| **Gnocchi constraint** | **REJECT** | K562 δ=+0.051; HepG2 δ=−0.044; знак плавает, ниже MCID 0.2 |
| **R-loop** (DRIP-seq) | **REJECT** | δ=−0.042 (направление против гипотезы) |
| **G4** (BG4 ChIP) | **REJECT** | δ=−0.047 (K562) / −0.024 (HepG2) |
| **Continuous SE-size** | **REJECT-with-signal** | ρ_max = **0.163** (MCID 0.2); сигнал реален, но ниже порога |
| **META missing heritability** | **CLOSED** | Validated negative; +ve ctrl CDS vs intergenic **δ ≈ 0.61** (pipeline жив) |

Итог SE-трека: направление «SE membership объясняет missing heritability / LLPS-специфику» закрыто как честный отрицательный результат, не как сбой пайплайна.

---

## 7. TE kill-sprint P1–P10 (2026-07-15)

Цель: **falsify / снять** desk-приоритет G4a / C1 / reporter **до** wet-lab. Не биологическое доказательство, не holdout, не E/P shopping.

| Pri | Тест | Вердикт |
|----:|------|---------|
| **P1** | G4a multi-sample Contact(E,P) | **PASS_DESK_ROBUST** |
| **P2** | C1 301 bp saturation mutagenesis | **ALLELE_LEAN_RETAINED** |
| **P3** | Matched-null panel | **RETAIN_HP** (C1/C2/C3) |
| **P4** | Independent model matrix | **P4_MATRIX_COMPLETE** |
| **P5** | Reporter robustness + R1 | **R1_PASS** (reporter desk OK) |
| **P6** | PE/OT robustness | **PE_OT_CONDITIONAL_PASS** |
| **P7** | Target gene ranking | **P7_RANKED_EXPLORATORY** |
| **P8** | Power simulation | Reporter **ADEQUATE** / Capture **UNDERPOWERED** |
| **P9** | Virtual end-to-end | **P9_GAPS** |
| **P10** | Immutable handoff | **locked** (`content_hash` frozen) |

Bottom line: C1 сохранил право на дальнейшую проверку после desk kill-sprint; Desk-тесты не дали достаточного основания отвергнуть C1, но не подтвердили биологический эффект. PE условный; Capture не primary; E2E только soft gaps; target gene exploratory.

**C1 (заморожен):** `chr11:62753923 A>G` (AluSz) — development template, не wet-proof. Запрещённый claim: «C1 нарушает enhancer–promoter loop в HUDEP-2».

---

## 8. Что остаётся (на 2026-07-20)

| Пункт | Статус |
|---|---|
| Человеческая **подпись B0** | Требуется; без `date_signed` → NO-GO |
| **PO** (B0_PO_draft) | Draft; не сабмитить до подписи B0 |
| **A1** (PE) | Отдельный pack, READY_FOR_SIGNATURE_LATER · NO-GO |
| **A2** (Capture) | HELD · ORDER FORBIDDEN · не primary |
| **Holdout** | **SEALED** · unblind BLOCKED |
| **Wet-lab / oligos** | **NO-GO** / **FORBIDDEN** до человеческой GO-подписи |

B0 после подписи авторизует только reporter-only минимум (B-min REF/ALT 301 bp, backbone, empty control) — не A1 PE, не A2 Capture, не OT oligos, не holdout unblind.

---

## 9. Gems (переиспользуемые артефакты)

| Gem | Зачем |
|---|---|
| **RDR Router** | Strategy router / stop-matrix; confirmatory и wet блокированы до guards |
| **NDE A+B** | Narrow Discovery Engines (exhaustion + constraint relaxation) для C1; alive {M3, M1, M0} |
| **ARCHCODE-PROSPECTIVE** | FRAMEWORK_ONLY — без primary scorer / nomination / wet GO |
| **holdout_guard** | Код отказывается скорить sealed holdout |
| **kill-sprint** | Desk falsify-before-wet протокол P1–P10 |
| **P10** | Immutable SHA-256 handoff snapshot |
| **B0 pack** | Reporter-only ready pack, ожидающий человеческую подпись |
| **null_results** | Общая память отрицательных / закрытых направлений |
| **E/P freeze** | Заморозка якорей E/P; запрет shopping после данных |

---

## 10. Locks (не снимать без явного протокола)

| Lock | Состояние |
|---|---|
| **Holdout** | **SEALED** (`unblind_authorized: false`) |
| **Stage-3** | **LOCKED** (C1 template excluded from Stage-3 slots) |
| **E/P** | **LOCKED** (якоря C1 зафиксированы; bait windows не двигать post-data) |
| **Oligos** | **FORBIDDEN** при `date_signed: null` |
| **Capture** | **не primary** (P8 UNDERPOWERED; A2 HELD) |

---

## 11. Сводка одним абзацем

DNA Ladder стартовал 2026-07-08 как falsification-first спин-офф ARCHCODE с опорой на Research Library: гипотезы о ДНК допускаются только через L0, novelty, preregistered claim и реальные публичные данные. Трек SE/LLPS за два дня (до 2026-07-10) сошёлся в кластер REJECT (LLPS, VUS, Gnocchi, R-loop, G4) плюс continuous REJECT-with-signal (ρ_max=0.163) и META CLOSED с положительным контролем δ≈0.61 — направление missing heritability закрыто как validated negative. Трек TE/Alu–3D прошёл HBB STOPPED / Package A и sealed holdout к prospective-каркасу и кандидату C1 (`chr11:62753923 A>G`): desk kill-sprint P1–P10 не дал достаточного основания отвергнуть C1 как development template и не подтвердил биологический эффект (C1 сохранил право на дальнейшую проверку; P1 PASS_DESK_ROBUST … P10 locked), primer desk PASS, B0 ready pack собран UNSIGNED; на 2026-07-20 проект на паузе — ждут человеческую подпись B0, PO не сабмитят, A1/A2 отдельно, holdout SEALED, wet NO-GO, Capture не primary.

---

*Конец PROJECT_HISTORICAL_BRIEF_v1 · report_version 1.1 · snapshot 2026-07-20 · revision after external review (~9/10 → publication-ready: hash pin, claim table, status glossary, careful C1 language)*
