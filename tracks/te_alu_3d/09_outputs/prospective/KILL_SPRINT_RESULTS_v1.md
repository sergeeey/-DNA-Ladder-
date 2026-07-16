# Kill-first computational sprint — results v1

**Date:** 2026-07-15  
**Goal:** attempt to **destroy** G4a / C1 allele priority / reporter plan **before wet-lab**  
**Not:** biological proof · not holdout · not E/P shopping

---

## Sprint board

| Pri | Test | Status | Verdict |
|----:|------|--------|---------|
| **1** | G4a multi-sample Contact(E,P) | **DONE** | **`PASS_DESK_ROBUST`** — kills none |
| **2** | C1 301 bp saturation mutagenesis | **DONE** (v1+v2 expand) | **`ALLELE_LEAN_RETAINED`** — kills none; v2: all 60 A→G + random100 (n=255) |
| **3** | Matched-null panel ×13 | **DONE** (+expand) | activity **not** weakened; v2 L2 **RETAIN_HP** C1/C2/C3 |
| **4** | Independent model matrix | **DONE** | **`P4_MATRIX_COMPLETE`** — 5 conv / 3 disagree / 2 unsupported / 2 neg; C1 convergence |
| **5** | Reporter robustness | **DONE** | **`REPORTER_DESK_OK_TECHNICAL`** + **P5 R1 `R1_PASS`** (AG 16/100/500 kb proxy) |
| **6** | PE/OT robustness | **DONE** | **`PE_OT_CONDITIONAL_PASS`** — PD1+PD2 viable; RADIL watch; Primer-BLAST still manual |
| **7** | Target gene ranking | **DONE** | **`P7_RANKED_EXPLORATORY`** — top HNRNPUL2-BSCL2/BSCL2; no TSS in P; RNA absent |
| **8** | Power simulation | **DONE** | Reporter **`P8_ADEQUATE`** (n_tx=6); Capture-C **`P8_UNDERPOWERED`** |
| **9** | Virtual end-to-end | **DONE** | **`P9_GAPS`** — path coherent; backbone / Primer-BLAST / Capture soft |
| **10** | Immutable handoff snapshot | **DONE** | `content_hash` in `P10_immutable_handoff_v1.md` |

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

**Arts:** `C1_saturation_mutagenesis_v1.md`, `P2_SATMUT_EXPAND_CLAIM_v1.md`, `C1_saturation_mutagenesis_v2.md`

| | v1 (top-PWM) | v2 (all A→G + random 100) |
|--|--------------|---------------------------|
| AG scored | 101 / 903 | **255** / 903 |
| A→G covered | 6 | **60 / 60** |
| C1 rank | 1 | **2** (neighbor `62753922:A:G` 0.567 > C1 0.541) |
| pct from top | ~1% | **~0.8%** |
| peers ≥0.9×C1 | 0 | **1** |
| mean other A→G | 0.155 | **0.178** ≪ C1 |
| Kills S1/S2/S3 | none | **none** |
| Overall | ALLELE_LEAN_RETAINED | **ALLELE_LEAN_RETAINED** |

### Plain language
Даже на полном A→G + random фоне C1 остаётся редким выбросом. Соседний A→G на −1 bp чуть выше — локальный кластер, не «средняя A→G» и не толпа peers.

**Caveat:** still not full 903 AG; not wet biology.

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

## Priority 6 — PE/OT robustness

**Arts:** `P6_PE_OT_CLAIM_v1.md`, `P6_PE_OT_robustness_v1.md`

| Check | Result |
|-------|--------|
| PD1 mm≤2 | **0** (MIT69) |
| PD2 backup | **viable** (MIT84, mm≤2=0) |
| ngRNA primary | **prefer** `GTTCTAAGGTTAGGCCGAGG` (mm≤2=0) |
| ngRNA alt | weaker (mm≤2=1) |
| Engine2 UCSC OT verify | **4/4** sites match CRISPOR OT seq |
| RADIL watch | CFD 0.37 (K3 soft) |
| Primers amp-local | OK (OT2 polyA noted) |
| Genome Primer-BLAST | still **manual** before order |
| Verdict | **`PE_OT_CONDITIONAL_PASS`** |

### Plain language
PE-дизайн не fragile на одном guide: PD2 — нормальный backup. Главный риск — **RADIL** и ручной Primer-BLAST до заказа.

---

## Priority 8 — Power simulation

**Arts:** `P8_POWER_CLAIM_v1.md`, `P8_power_simulation_v1.md`

| Assay | Label | Mid-noise power @ n=6 |
|-------|-------|----------------------:|
| Reporter (μ=0.5 MCID) | **`P8_ADEQUATE`** | 0.894 |
| Capture-C (Δ=0.25, ε=0.7) | **`P8_UNDERPOWERED`** | 0.111 |

Recommended reporter n_tx (mid, power≥0.8): **6**. Capture has **no** n_batch ≤6 reaching 0.8 at ε≤0.7.  
MCID false-positive (μ=0, mid, n=6): **0.22** — rule is liberal under null; interpret with care.

### Plain language
Репортёрный план на 6 трансфекций desk-adequate для MCID. Capture-C при реалистичной edit efficiency **недомощен** — не обещать 3D-контакт как powered primary.

---

## Priority 10 — Immutable handoff

**Arts:** `P10_immutable_handoff_v1.md` / `.json`  
SHA-256 catalog of kill-sprint arts; locks (holdout SEALED, wet NO-GO, Stage-3 LOCKED) frozen in snapshot.

---

## What NOT done (still recommended next)

1. ~~Expand matched-null universe~~ **DONE** (L2 unlocked; L1 still sparse)  
2. ~~**P2 full or stratified AG**~~ **DONE** (all A→G + random 100; lean retained)  
3. ~~**P5 R1** AG length ladder~~ **DONE** (`R1_PASS` on 16/100/500 kb proxy)  
4. ~~**P6** second OT engine + Primer-BLAST~~ **DONE** desk (`PE_OT_CONDITIONAL_PASS`; genomewide Primer-BLAST still manual)  
5. ~~**P8** power curves~~ **DONE** (reporter ADEQUATE; Capture UNDERPOWERED)  
6. ~~**P10** immutable snapshot~~ **DONE** (rehashed after P9)  
7. ~~**P9** virtual end-to-end~~ **DONE** (`P9_GAPS`)  
8. Optional: remaining ~648 AG subst if budget allows (not required after v2)  
9. Genomewide Primer-BLAST (manual) before any oligo order  
10. Optional: local Cas-OFFinder when hg38 dump available

---

## Bottom line (honest)

```text
G4a single-hic risk:     WEAKENED (multi-sample + VC pass)
C1 allele-vs-window:     NOT KILLED (v2 satmut: rank#2/255, lean retained)
Matched-null panel:      v2 L2 RETAIN_HP for C1/C2/C3; panel not weakened
Reporter tech + R1:      OK; AG length proxy R1_PASS (16/100/500 kb)
PE/OT desk:              PE_OT_CONDITIONAL_PASS (RADIL watch; Primer-BLAST manual)
Reporter power (desk):   P8_ADEQUATE at n_tx=6
Capture-C power (desk):  P8_UNDERPOWERED (ε≤0.7)
Virtual E2E:             P9_GAPS (0 hard blocks)
Target gene (desk):      P7_RANKED_EXPLORATORY (BSCL2-axis; RNA absent)
Model matrix (desk):     P4_MATRIX_COMPLETE (5/3/2/2; C1 convergence)
Immutable snapshot:      P10 locked (incl. P9)
Wet-lab proof:           STILL ABSENT
Expand to hundreds:      Still DON'T
Holdout / move E/P:      Still DON'T
```

## Priority 4 — Independent model matrix

**Arts:** `P4_INDEPENDENT_MODEL_CLAIM_v1.md`, `P4_independent_model_matrix_v1.md`, `P4_G2b_independence_notes_v1.md`

| Class | n |
|-------|--:|
| convergence | 5 (incl. C1 via activity+WT) |
| principled_disagreement | 3 |
| unsupported | 2 |
| negative_consistent | 2 |

ARCHCODE: UNAVAILABLE (exploratory prior only). AG CHIP+contact = same family — not two votes.

### Plain language
Панель разложена по согласию моделей. C1 — convergence не из‑за motif, а activity+WT Hi-C. Это desk-карта, не лаборатория.

---

## Priority 7 — Target gene ranking

**Arts:** `P7_TARGET_GENE_CLAIM_v1.md`, `P7_target_gene_ranking_v1.md`

| | |
|--|--|
| Label | **`P7_RANKED_EXPLORATORY`** |
| TSS inside locked P | **0** (P not moved) |
| Top | HNRNPUL2-BSCL2 (6) · BSCL2 (5) · TAF6L (4) |
| Prior desk | LRRN4CL rank~17; ZBTB3/POLR2G ~9–10 (cis-activity nearer C1, weaker P geometry) |
| HUDEP-2 RNA | **UNAVAILABLE** |

### Plain language
Есть ранжированный список, не «один правильный ген». BSCL2 / read-through — геометрия к locked P; без HUDEP-2 RNA нельзя назначать expression target. P не двигаем.

---

## Priority 9 — Virtual end-to-end

**Arts:** `P9_VIRTUAL_E2E_CLAIM_v1.md`, `P9_virtual_e2e_v1.md`

| | |
|--|--|
| Label | **`P9_GAPS`** |
| Hard blocks | **0** |
| Soft gaps | backbone TBD · Primer-BLAST manual · Capture `P8_UNDERPOWERED` |
| Locks | holdout SEALED · Stage-3 LOCKED · GO UNSIGNED · ORDER FORBIDDEN |

### Plain language
B0→A1→A2 на desk **сходится**. Редизайн не нужен. До human GO — backbone, Primer-BLAST, и не продавать Capture как powered primary.

---

Desk kill-sprint: C1/panel **not destroyed**; PE **conditional**; Capture **not powered**; E2E **gaps only**; target gene **exploratory**; model matrix **complete**.  
Следующий шаг: Primer-BLAST manual · или human GO (blocked).

