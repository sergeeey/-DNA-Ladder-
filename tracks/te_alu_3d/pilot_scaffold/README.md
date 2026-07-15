# Chr11 Pilot Scaffold — Kill-First

Toy-test для проверки **механики** гипотезы TE×3D disruption, не для биологического вывода.

## Принцип

> Сначала убить гипотезу, потом искать сигнал.

**Design freeze:** [`../07_methods/pilot_redesign_v2.md`](../07_methods/pilot_redesign_v2.md)  
**Kill criteria:** v1.2 · **Score freeze:** [`score_freeze.yaml`](score_freeze.yaml)

Порядок строгий:

0. **KC0** — cell-type / locus congruence (HBB+GM12878 → exploratory only)  
1. **QC gates 1–4** — blacklist, mappability, segdup, gnomAD discordance  
2. **TE filter** — только Alu + SVA (chr11)  
3. **Matched controls** — hierarchy A–D; estimands **T** (no CTCF match) vs **C** (CTCF match)  
4. **Block permutation** — within matched set (global shuffle = software control only)  
5. **Kill criteria** — KC0–KC6; enrichment blocked until gates pass  
6. **Output split** — confirmatory ≠ exploratory; LSSIM fallback → exploratory  

Enrichment summary **запрещён**, если permutation / direction / freeze gate не пройдены.

### Интерпретация текущего real run

```text
current pilot claim: killed (N=14 ClinVar)
Track A hypothesis:  unresolved
Track B / MWPM:      not tested
```


## Scope

| Параметр | Значение |
|----------|----------|
| Хромосома | chr11 only |
| Сборка | GRCh38/hg38 |
| 3D context | GM12878 (preferred) |
| TE | SVA + Alu first |
| gnomAD | **chr11 slice only** — no bulk download |

## Быстрый старт (dry-run)

Без скачивания данных — проверка pipeline mechanics:

```bash
cd pilot_scaffold
python run_pilot.py --dry-run --n-perm 500
```

Или по модулям:

```bash
python qc_filters.py --dry-run
python build_matched_controls.py --dry-run
python compute_disruption_scores.py --dry-run
python permutation_test.py --dry-run
```

## Real run (chr11 ClinVar)

```bash
# 1) Fetch chr11 slices (no bulk gnomAD)
python fetch_chr11_inputs.py

# 2) Kill-first pilot (full chr11; set genomic_window in config for HBB)
python run_pilot.py --n-perm 2000
```

Артефакты → `../09_outputs/pilot_chr11/`

**Ожидаемо:** enrichment summary `BLOCKED_*` пока permutation/KC1 не пройдены.  

## Порядок модулей

```
inputs (chr11) → qc_filters → build_matched_controls → compute_disruption_scores → permutation_test → report
```

| Модуль | Gate | Kill-first роль |
|--------|------|-----------------|
| `qc_filters.py` | 1–4, TE | Отсев confounders до scoring |
| `build_matched_controls.py` | 5 | Balance table; SMD audit |
| `compute_disruption_scores.py` | — | Scores only, no interpretation |
| `permutation_test.py` | 6 | **Primary gate** — KC1/KC4 flags |

## Output split (gate 7)

```
09_outputs/pilot_chr11/
  confirmatory/     # dual-track gnomAD + passes QC
  exploratory/      # ClinVar-only, ascertainment suspect
  qc_dropout_report.json
  control_manifest.csv
  permutation_results.json
  kill_criteria_status.json
  enrichment_summary.csv   # ONLY if permutation gate passes
```

## Kill criteria (из `00_research_question/kill_criteria.md`)

| ID | Триггер в scaffold |
|----|-------------------|
| KC1 | `median_delta < 0.05` после matching → STOP |
| KC2 | Sequential covariates — manual in report |
| KC3 | ClinVar-only → exploratory track only |
| KC4 | >50% dropout по QC → FIX or STOP |
| KC6 | ≥2 orthogonal lines — post-pilot |

## ARCHCODE integration

`compute_disruption_scores.py` вызывает внешний binary если `config.yaml → scoring.archcode.binary_path` задан.  
Иначе — LSSIM stub (явно помечен как fallback, не confirmatory evidence).

## Зависимости

- Python ≥3.10  
- `pyyaml`  
- Опционально: `pyBigWig` (mappability), `pysam` (VCF), `bcftools`/`tabix` (fetch)

## Что этот pilot НЕ делает

- Не доказывает TE pathogenicity  
- Не заменяет CRISPR / expression validation  
- Не смешивает confirmatory corpus с exploratory  
- Не интерпретирует perm_p < 0.05 как биологию без KC6  

## Ссылки

- `../07_methods/matched_control_spec.md`  
- `../07_methods/toy_test_chr_pilot.md`  
- `../00_research_question/kill_criteria.md` v1.1  
- `../08_negative_evidence/` — alternative explanations A1–A8  
