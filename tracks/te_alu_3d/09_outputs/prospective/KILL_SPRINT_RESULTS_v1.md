# Kill-first computational sprint — results v1

**Date:** 2026-07-15  
**Goal:** attempt to **destroy** G4a / C1 allele priority / reporter plan **before wet-lab**  
**Not:** biological proof · not holdout · not E/P shopping

---

## Sprint board

| Pri | Test | Status | Verdict |
|----:|------|--------|---------|
| **1** | G4a multi-sample Contact(E,P) | **DONE** | **`PASS_DESK_ROBUST`** — kills none |
| **2** | C1 301 bp saturation mutagenesis | **DONE** (partial AG) | **`ALLELE_LEAN_RETAINED`** — kills none |
| **3** | Matched-null panel ×13 | **DONE** (+expand) | v1/v2: activity **not** weakened; L1/L2 unreachable → **accept L3 ceiling**; C1 extreme@L3 |
| **4** | Independent model matrix | PARTIAL (AG already on panel) | continue |
| **5** | Reporter robustness | **DONE** | **`REPORTER_DESK_OK_TECHNICAL`** + **P5 R1 `R1_PASS`** (AG 16/100/500 kb proxy) |
| **6** | PE/OT robustness | NOT STARTED | PD1 pack exists |
| **7** | Target gene ranking | NOT STARTED | — |
| **8** | Power simulation | NOT STARTED | — |
| **9** | Virtual end-to-end | NOT STARTED | — |
| **10** | Immutable handoff snapshot | NOT STARTED | — |

---

## Priority 1 — G4a multi-sample (most valuable)

**Arts:** `G4a_multisample_kill_test_v1.md`, `G4a_multisample_metrics_v1.json`

Pre-registered kills: K1 only-3113 · K2 KR wiped by VC · K3 missing primary.

| Sample | enrich10 | OE10 | enrich25 | OE25 | Verdict |
|--------|---------:|-----:|---------:|-----:|---------|
| GSM4873113 WT GW | 3.40 | 3.20 | 2.45 | 2.14 | PASS_DESK |
| GSM4873114 DEL GW | 3.01 | 3.33 | 3.43 | 3.23 | PASS_DESK |
| GSM4873115 INV GW | 3.49 | 4.05 | 3.04 | 3.09 | PASS_DESK |
| Capture 3116 WT | — | — | — | — | DUMP_FAIL (bait locus) |
| Capture 3117/3118 | weak/mixed | | | | INCONCLUSIVE_LEAN (not G4a proof) |

**VC (WT 3113):** PASS at 10 kb and 25 kb (enrich ~3.29 / ~2.40).  
**Leave-one-out:** mean enrich of remaining ≈ 3.2–3.4 whether 3113 left out or not.

### Plain language
Контакт E–P **не** артефакт одного файла GSM4873113: он есть и в DEL/INV genome-wide Hi-C, и при VC-нормализации.  
Capture по β-глобину для этого окна не годится — ожидаемо.

**G4a remains PASS_DESK**, upgraded note: **PASS_DESK_ROBUST**.  
Still **not** an allele effect of C1.

---

## Priority 2 — C1 saturation mutagenesis

**Arts:** `C1_saturation_mutagenesis_v1.md`, `.json`

- Window 301 bp: **903** possible single-base alts  
- PWM scored: all  
- AG scored: **101** = C1 + top-100 \|PWM\| (budget)  

Pre-registered: S1 not top5% · S2 ≥20 peers @90% · S3 mean other A→G ≥ C1.

| Metric | Value |
|--------|------:|
| C1 CHIP_TF | 0.541 |
| Rank among AG-set | **1 / 101** (~top 1%) |
| Peers ≥0.9×C1 | **0** |
| Mean other A→G CHIP_TF | 0.155 ≪ C1 |

### Plain language
Среди самых «мотивных» замен в окне C1 A→G пока **локальный выброс**, не средний A→G и не толпа соседей с тем же score.

**Caveat:** AG не на всех 903 (только top-PWM + C1) — это делает тест **строже против C1** (соседи уже сильные по PWM). Полный 903-run — усиление, не отмена.

---

## Priority 5 — Reporter technical + R1 length AG

**Tech arts:** `Stage2_reporter_robustness_v1.md` — edge/GC OK; C1 not near edge.  
**R1 arts:** `P5_R1_CLAIM_v1.md`, `P5_R1_window_length_ag_v1.md`

AG cannot score literal 301/1kb/2kb; used **16 / 100 / 500 kb** ladder.  
Primary: signed mean CHIP_TF. **C1 → `R1_PASS`** (no adjacent sign flips; magnitude shrinks with length, sign stays −).  
C2/C3 stable; N3 one mild flip at tiny magnitude → `N3_OK_OR_MILD`.  
Branch B length-sensitivity **not killed** on this proxy. Oligo order still FORBIDDEN.

---

## Priority 3 — Matched-null panel ×13

**Arts:** `P3_matched_null_CLAIM_v1.md`, `P3_matched_null_panel_v1.md` (n=28),  
`P3_EXPAND_REPORT_v1.md`, `P3_matched_null_panel_v2.md` (n=115 universe)

| | v1 n=28 | v2 n=115 |
|--|---------|----------|
| Activity panel weakened | False | **False** |
| Negatives broken | False | **False** |
| C1 | L3 INCONCLUSIVE (pct95) | **L2 RETAIN_HP** (pct93.8) |
| C2/C3/C3b | L3 | **L2 RETAIN_HP** |

Architecture contact endpoint: mostly demotion. Stage-3 / holdout / wet-lab unchanged.

### Plain language
На тесном пуле C1 был «высок, но formal L3». После расширения matched-null C1/C2/C3 **формально RETAIN_HP** на L2. Это desk-kill-test result, не лаборатория.

---

## What NOT done (still recommended next)

1. ~~Expand matched-null universe~~ **DONE** (L2 unlocked; L1 still sparse)  
2. **P2 full or stratified AG** beyond top-PWM (all A→G in window; random 100)  
3. ~~**P5 R1** AG length ladder~~ **DONE** (`R1_PASS` on 16/100/500 kb proxy)  
4. **P6** second OT engine + Primer-BLAST  
5. **P8** power curves for reporter & Capture-C  
6. **P10** immutable hash-locked analysis release  

---

## Bottom line (honest)

```text
G4a single-hic risk:     WEAKENED (multi-sample + VC pass)
C1 allele-vs-window:     NOT KILLED on partial satmut (rank #1)
Matched-null panel:      v2 L2 RETAIN_HP for C1/C2/C3; panel not weakened
Reporter tech + R1:      OK; AG length proxy R1_PASS (16/100/500 kb)
Wet-lab proof:           STILL ABSENT
Expand to hundreds:      Still DON'T
Holdout / move E/P:      Still DON'T
```

Desk kill-sprint: C1/panel **not destroyed**; Branch B length proxy **survives**.  
Следующий полезный kill-тест: **P2** satmut AG expand или **P6** OT.

