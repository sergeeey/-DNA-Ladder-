# G12 — Common Alu∩CTCF × HUDEP-2 DNase accessibility — CLAIM v1

**Pre-registration date:** 2026-07-24  
**L0 gate:** Descriptive  
**Status:** LOCKED — before peak download / overlap peek  
**Related:** G8 DATA_GAP (eQTL/MPRA); G9–G11 eQTL CLOSED; Stage-3/G10 Hi-C CLOSED

---

## 1. Why G12

Blood/LCL eQTL enrichment for common Alu∩CTCF is REJECT. Erythroblast eQTL remains
EGA-blocked. A **new open resource** exists: ENCODE **HUDEP-2 DNase-seq** peaks
(`ENCSR978CYN`, released 2025-09). G12 asks whether Alu∩CTCF common SNVs sit in
open chromatin more often than AF-matched Alu outside CTCF — same panel geography,
**different readout** (accessibility, not expression / contact).

Not tissue fishing on GTEx. Not Hi-C rescue.

---

## 2. Estimand

Among frozen G9c common SNVs, is the fraction overlapping a HUDEP-2 DNase peak
higher for **CASE_CTCF_ALU** than for **CTRL_ALU_NONCTCF**?

HIT = `BED_start < pos ≤ BED_end` (half-open) in primary peak set.  
Allowed language: accessibility-candidate only. Forbidden: regulatory / causal / eQTL.

---

## 3. Locked inputs

| Layer | Value |
|-------|--------|
| Panel | `g9c_common_alu_ctcf_panel_freeze_v1.json` (sha256 verified; n=200/200) |
| Primary DNase | ENCODE `ENCSR978CYN` / **`ENCFF626FHU`** (GRCh38 peaks, bed.gz) |
| Replication | `ENCSR013QDF` / **`ENCFF895OQX`** — **only if** primary PASS |
| Decision | `decide_enrichment` (α=0.01, min_abs_diff=0.05, min_n=30) |

Holdout / HBB geography already excluded in freeze. No Stage-3 / wet GO.

---

## 4. Novelty (desk)

| Source | Finding |
|--------|---------|
| G8 | No open erythroid eQTL/MPRA for rare panel; accessibility not tested |
| eQTL Catalogue | No erythroblast `ge` dataset open (BLUEPRINT myeloid only) |
| ENCODE | HUDEP-2 DNase ENCSR978CYN (+ siblings) released — unused on this track |
| null_results | No Alu∩CTCF × HUDEP-2 DHS filing |

---

## 5. Forbidden

- Changing peak accession after seeing overlaps  
- GTEx tissue add-ons / Hi-C re-runs on closed slots  
- Claiming expression or 3D contact from DHS overlap  

---

## 6. Artifacts

- `G12_common_alu_ctcf_hudep2_dnase_CLAIM_v1.md` (this file)  
- `g12_hudep2_dnase_peaks_ENCFF626FHU.bed.gz` (+ sha256)  
- `g12_common_alu_ctcf_hudep2_dnase_v1.json`  
- `G12_common_alu_ctcf_hudep2_dnase_decision_v1.md`  
- Script: `run_g12_common_alu_hudep2_dnase.py`
