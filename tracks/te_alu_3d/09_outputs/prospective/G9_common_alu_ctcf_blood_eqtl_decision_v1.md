# G9 — Common Alu/SVA × CTCF blood eQTL — DECISION v1

**Date:** 2026-07-23  
**Claim:** `G9_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`  
**Freeze:** `g9_common_alu_ctcf_panel_freeze_v1.json`  
**Freeze sha256:** `315b67e6010771de1b15534c48f9083def03f2a29da7581c411be7c8f93c43c8`  
**Primary dataset:** `QTD000356` (GTEx blood ge)  
**Verdict:** **INCONCLUSIVE** (`api_error_rate`)

---

## Panel freeze

| Arm | n |
|-----|--:|
| CASE_CTCF_ALU (common AF 0.05–0.50 in Alu∩CTCF) | 23 |
| CTRL_ALU_NONCTCF (AF-decile matched) | 23 |
| Overlaps queried (chr11) | 118 CTCF×Alu |

Both arms **below** the pre-registered `min_n=30` power floor.

---

## Primary counts (QTD000356)

| Arm | hit | miss | error | tested | error_rate |
|-----|----:|-----:|------:|-------:|-----------:|
| case | 1 | 17 | 5 | 18 | 0.217 |
| ctrl | 8 | 10 | 5 | 18 | 0.217 |

Pre-registered gate: if `n_error / n_queried > 0.10` → **INCONCLUSIVE** (no Fisher).  
Errors were HTTP 400 Bad Request from the Catalogue API for 10/46 variants.

**Descriptive only (not decision-bearing):** among successful queries, case hit-rate 1/18 ≈ 0.06 vs ctrl 8/18 ≈ 0.44 (wrong direction for the enrichment hypothesis). Replication **not run** (primary not PASS).

---

## What this does NOT mean

1. Not causal Alu → CTCF → expression.  
2. Not erythroid / HUDEP-2 specific (whole blood only).  
3. Not a rescue of Stage-3 Hi-C or G8 rare-panel gap.  
4. Not wet-lab GO / holdout unlock.  
5. Not permission to reclassify HTTP 400 as MISS post-hoc without a new claim.

---

## Allowed next moves

- New claim treating Catalogue HTTP 400 as “not tested / miss” with larger genome-wide common Alu panel  
- EGA erythroblast eQTL unlock  
- Remain paused on activity enrichment
