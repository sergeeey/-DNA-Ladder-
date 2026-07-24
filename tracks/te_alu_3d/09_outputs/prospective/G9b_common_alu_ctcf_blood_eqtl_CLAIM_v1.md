# G9b — Common Alu/SVA × CTCF blood eQTL (power + API-miss fix) — CLAIM v1

**Pre-registration date:** 2026-07-23  
**L0 gate:** Descriptive  
**Status:** LOCKED — before new freeze and before any G9b eQTL peek  
**Supersedes decision path of:** G9 (does **not** rewrite G9 artifacts; G9 stays INCONCLUSIVE)  
**Related:** `G9_common_alu_ctcf_blood_eqtl_decision_v1.md`

---

## 1. Why G9b (locked rationale)

G9 closed INCONCLUSIVE because:

1. HTTP 400 from eQTL Catalogue counted as ERROR → error_rate 21.7% > 10% gate  
2. Panel n=23 < min_n=30  

G9b changes **only** these two pre-declared design knobs. Same estimand family.

---

## 2. Estimand

Same as G9: among common SNVs on chr11 (non-holdout), is GTEx whole-blood cis-eQTL
hit-rate higher for SNVs in **Alu/SVA ∩ HUDEP-2 CTCF peak** than for AF-matched
**Alu/SVA outside CTCF±250 bp**?

Cell-type caveat unchanged: whole blood ≠ HUDEP-2.

---

## 3. Design deltas vs G9 (complete list)

| Knob | G9 | G9b |
|------|----|-----|
| AF band | [0.05, 0.50] | **[0.01, 0.50]** |
| HTTP 400 / empty / not-in-map | ERROR | **MISS** |
| Other HTTP 5xx / network after retries | ERROR | ERROR (unchanged) |
| error_rate INCONCLUSIVE gate | >0.10 | >0.10 (unchanged) |
| min_n for Fisher | 30 | 30 (unchanged) |
| Primary / replication datasets | QTD000356 / QTD000373 if PASS | same |
| Geography | chr11; HBB + holdout exclude | same |
| Seed | 20260722 | **20260723** (new match draw) |
| Panel cap | 200 | 200 |

No other knob changes. No Stage-3 reopen. No holdout.

---

## 4. Freeze

Artifact: `g9b_common_alu_ctcf_panel_freeze_v1.json` (+ sha256)  
No eQTL fields. New freeze required (AF band changed) — do **not** reuse G9 freeze IDs as primary.

If after freeze `n_case < 30` or `n_ctrl < 30` → stop with verdict **INCONCLUSIVE**
(`underpowered_freeze`) **without** eQTL queries.

---

## 5. eQTL status rule

For each variant × dataset:

1. Query Catalogue API v2 associations by `chr11_{pos}_{ref}_{alt}`  
2. If any assoc `pvalue ≤ 5e-8` (or nlog10p ≥ 7.3010) → **HIT**  
3. If HTTP **400**, or HTTP 200 with empty list, or all p above threshold → **MISS**  
4. If other failures after retries → **ERROR**

---

## 6. Decision rule

Identical to G9 Fisher table on HIT vs MISS (ERROR excluded from denominator).  
If error_rate > 0.10 → INCONCLUSIVE.  
PASS / REJECT / INCONCLUSIVE thresholds unchanged.

Replication QTD000373 only if primary PASS.

---

## 7. Forbidden

- Post-hoc reclassification of G9 rows  
- Changing p-threshold or min_n after seeing G9b results  
- Expanding to other chromosomes inside this claim (would need G9c)  
- Wet GO / holdout / Hi-C rescue

---

## 8. Scripts

- Reuse `g9_eqtl_lib.py` with G9b constants / miss-on-400 helper  
- `freeze_g9b_common_alu_ctcf_panel.py`  
- `run_g9b_common_alu_blood_eqtl.py`  
- Extend `tests/test_g9_eqtl_lib.py` for HTTP-400→MISS
