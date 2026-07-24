# G11 — Common Alu∩CTCF × GTEx LCL eQTL — CLAIM v1

**Pre-registration date:** 2026-07-24  
**L0 gate:** Descriptive  
**Status:** LOCKED — before any LCL/liver eQTL peek  
**Related:** G9c blood (QTD000356) REJECT closed; this is a **different tissue map**

---

## 1. Why G11

G9c rejected enrichment of common Alu∩CTCF SNVs for **GTEx whole-blood** cis-eQTL
(`QTD000356`). G11 asks the **same enrichment estimand** on an independent
**non-blood** GTEx gene-expression map: **LCL** (EBV-transformed lymphocytes,
`QTD000221`), using the **already frozen** G9c panel (no new variant fishing).

Not α-hacking of blood. Not Stage-3 / wet GO. Cell-type caveat: LCL ≠ HUDEP-2 ≠ blood.

---

## 2. Estimand

Is cis-eQTL hit-rate (p ≤ 5×10⁻⁸) higher for G9c **CASE_CTCF_ALU** SNVs than for
AF-matched **CTRL_ALU_NONCTCF** SNVs in GTEx LCL (`QTD000221`)?

---

## 3. Locked inputs

| Layer | Value |
|-------|--------|
| Panel | `g9c_common_alu_ctcf_panel_freeze_v1.json` (sha256 verified; n=200/200) |
| Primary eQTL | eQTL Catalogue **QTD000221** — GTEx LCL, `quant_method=ge` |
| Replication | **QTD000266** — GTEx liver, **only if** primary PASS |
| HTTP 400 | MISS (same as G9b/G9c) |
| Decision | `decide_enrichment` (α=0.01, min_abs_diff=0.05, min_n=30) |

Forbidden datasets for this claim: QTD000356 (blood), QTD000373 (blood Lepik).

---

## 4. Decision rule

Identical to G9c `decide_enrichment` on primary arm counts after excluding ERROR from
tested denominators (HIT+MISS). If primary `error_rate > 0.10` → INCONCLUSIVE
`api_error_rate` without PASS/REJECT on effect.

Replication QTD000266 runs **only if** primary verdict is PASS.

---

## 5. Forbidden

- Changing α / p-threshold / panel after peek  
- Reopening blood claim with new chroms  
- Stage-3 Hi-C rescue / holdout / wet GO  

---

## 6. Artifacts

- `G11_common_alu_ctcf_lcl_eqtl_CLAIM_v1.md` (this file)  
- `g11_common_alu_ctcf_lcl_eqtl_v1.json`  
- `G11_common_alu_ctcf_lcl_eqtl_decision_v1.md`  
- Script: `run_g11_common_alu_lcl_eqtl.py`
