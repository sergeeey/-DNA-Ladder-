# G12b — Within CTCF peaks: Alu vs non-Alu × HUDEP-2 DNase — CLAIM v1

**Pre-registration date:** 2026-07-24  
**L0 gate:** Descriptive  
**Status:** LOCKED — before any within-CTCF Alu/non-Alu overlap peek  
**Parent:** `G12_common_alu_ctcf_hudep2_dnase_decision_v1.md` (PASS — CTCF∩DHS expected)

---

## 1. Why G12b

G12 PASS showed Alu∩CTCF SNVs overlap HUDEP-2 DNase more than Alu outside CTCF. That is
compatible with a **tautology** (CTCF sites are open). G12b asks the residual question:
**among SNVs inside HUDEP-2 CTCF peaks**, is DHS hit-rate higher for those also in Alu/SVA
than for AF-matched SNVs in CTCF peaks but **outside** Alu/SVA?

If PASS → Alu-associated residual accessibility inside CTCF.  
If REJECT / INCONCLUSIVE → G12 PASS is explained by CTCF occupancy alone.

---

## 2. Estimand

On locked chroms `chr1, chr2, chr6, chr11` (same as G9c), AF ∈ [0.01, 0.50]:

| Arm | Definition |
|-----|------------|
| CASE | SNV in HUDEP-2 CTCF peak **and** Alu/SVA (half-open) |
| CTRL | SNV in HUDEP-2 CTCF peak **and not** in Alu/SVA ±0 bp; AF-decile matched |

HIT = overlap primary DNase `ENCFF626FHU` (same half-open rule as G12).  
Cap 200/200; seed **20260724b**; HTTP not applicable (local peaks).  
Decision: `decide_enrichment` (α=0.01, min_abs_diff=0.05, min_n=30).  
Replication DNase `ENCFF895OQX` only if primary PASS.

chr11 excludes HBB 5.2–5.3 Mb and holdout 64–68 Mb.

---

## 3. Forbidden

- Reusing G9c control arm (those are Alu-nonCTCF, wrong contrast)  
- Changing α / accessions after peek  
- Claiming G12b PASS upgrades eQTL/Hi-C  

---

## 4. Artifacts

- `G12b_ctcf_alu_vs_nonalu_dnase_CLAIM_v1.md`  
- `g12b_ctcf_alu_vs_nonalu_panel_freeze_v1.json` (+ sha256)  
- `g12b_ctcf_alu_vs_nonalu_dnase_v1.json`  
- `G12b_ctcf_alu_vs_nonalu_dnase_decision_v1.md`  
- Scripts: `freeze_g12b_ctcf_alu_vs_nonalu_panel.py`, `run_g12b_ctcf_alu_vs_nonalu_dnase.py`
