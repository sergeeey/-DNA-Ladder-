# G9c — Multi-chromosome common Alu/SVA ∩ CTCF × blood eQTL — CLAIM v1

**Pre-registration date:** 2026-07-23  
**L0 gate:** Descriptive  
**Status:** LOCKED — before TE fetch / freeze / eQTL peek  
**Supersedes decision path of:** none (G9/G9b remain closed INCONCLUSIVE)  
**Related:** `G9b_common_alu_ctcf_blood_eqtl_decision_v1.md`

---

## 1. Why G9c

G9b on chr11 alone was INCONCLUSIVE (wrong-direction lean, Fisher p=0.015 > α=0.01).
G9c asks the **same estimand** on a **pre-declared multi-chromosome** panel to gain power
and reduce chr11-specific sampling noise. Not an α change and not a reanalysis of G9b rows.

---

## 2. Estimand

Among common SNVs (non-holdout geography on chr11 only), is GTEx whole-blood cis-eQTL
hit-rate higher for SNVs in **Alu/SVA ∩ HUDEP-2 CTCF peak** than for AF-matched
**Alu/SVA outside CTCF±250 bp**?

Cell-type caveat unchanged: whole blood ≠ HUDEP-2.

---

## 3. Locked chromosomes

**Primary panel chromosomes (complete list):** `chr1`, `chr2`, `chr6`, `chr11`

Sources:

| Layer | Path / source |
|-------|----------------|
| CTCF | `pilot_scaffold/data/ctcf_HUDEP2_peaks_raw.bed` filtered to locked chroms |
| TE | UCSC hg38 `rmsk` filtered to Alu* / SVA* on locked chroms →  
       `pilot_scaffold/data/repeatmasker_{chr}_alu_sva.bed` (+ combined) |
| Variants | gnomAD v4 GraphQL (same as G9b) |
| eQTL | QTD000356 primary; QTD000373 replication if PASS |

chr11 excludes HBB `5.2–5.3 Mb` and holdout `64–68 Mb` (unchanged).  
Other chroms: no holdout intervals.

---

## 4. Panel rules (same family as G9b)

| Knob | Value |
|------|-------|
| AF | **[0.01, 0.50]** |
| Case | Alu/SVA ∩ CTCF peak (half-open) |
| Control | Alu/SVA outside CTCF±250 bp; AF-decile matched |
| Cap | 200 case / 200 ctrl (sort by chrom, pos, ref, alt) |
| Seed | **20260723c** |
| HTTP 400 | **MISS** |
| min_n | 30 |
| α | 0.01 |
| Primary / replic | QTD000356 / QTD000373 if PASS |

Decision rule identical to G9b (`decide_enrichment`).

If freeze yields n_case<30 or n_ctrl<30 → INCONCLUSIVE `underpowered_freeze` without eQTL.

---

## 5. Forbidden

- Changing α or p-threshold after results  
- Adding chromosomes after freeze  
- Reopening Stage-3 Hi-C / holdout / wet GO  
- Rewriting G9/G9b verdicts

---

## 6. Artifacts

- `g9c_common_alu_ctcf_panel_freeze_v1.json` (+ sha256)  
- `g9c_common_alu_ctcf_blood_eqtl_v1.json`  
- `G9c_common_alu_ctcf_blood_eqtl_decision_v1.md`  
- Scripts: `fetch_g9c_rmsk_alu_sva.py`, `freeze_g9c_common_alu_ctcf_panel.py`,  
  `run_g9c_common_alu_blood_eqtl.py`
