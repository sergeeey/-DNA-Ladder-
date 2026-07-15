# P3 — Matched-null kill-test for frozen panel ×13

**Status:** PRE-REGISTERED (thresholds locked before results)  
**Date locked:** 2026-07-15  
**L0:** Predictive (desk): observed AG/PWM scores for panel alleles are **not** explained by matched TE / geometry / mutation-type background.  
**Not causal. Not holdout. Not wet-lab.**

**Inputs (frozen):** `stage1_desk_screen_v1.json` frozen_panel (n=13) + SCORED pool (n=28)  
**Out:** `P3_matched_null_panel_v1.md` / `.json`

---

## Estimand

For each frozen candidate \(i\) (except known_positive assay control):

1. Build matched control set \(C_i\) from SCORED Stage-1 pool alleles (exclude self; exclude same-locus alleles when \(n_{\text{other}}\ge 1\)).
2. Primary score \(S_i\):
   - roles `TEMPLATE_DEV`, `activity_m3`, `matched_negative`, `principled_disagreement` → \(S = |\mathrm{ag\_chip\_tf\_mae}|\)
   - role `architecture_m1` → \(S = |\mathrm{ag\_contact\_mae}|\) (CHIP as secondary)
3. Report empirical percentile of \(S_i\) within \(\{S_i\} \cup \{S_c : c\in C_i\}\), effect \(S_i - \mathrm{median}(C_i)\), control balance n, match level, leave-one-out rank stability, and block-permutation one-sided p (focal > matched controls).

---

## Matching hierarchy (escalating; report level used)

| Level | Criteria |
|------:|----------|
| **L1** | same `te_family` ∧ same CTCF bin (`dist==0` vs `>0`) ∧ same 5 Mb chr11 block ∧ same REF→ALT |
| **L2** | same TE clade (`AluS*`,`AluY*`,`AluJ*`,`FLAM*`,`FRAM*`,other) ∧ CTCF bin ∧ 5 Mb block |
| **L3** | same TE clade ∧ CTCF bin |
| **L4** | same CTCF bin only (**weak**; cannot support RETAIN_HP alone) |

Escalation: use the **strictest** level with \(n_{\mathrm{ctrl}} \ge 5\). If even L3 has \(n<5\), use best available and mark `INSUFFICIENT_MATCH`.

Editability (`pe_desk`) is reported as balance diagnostic, not a hard caliper (pool almost all PASS_DESK).

---

## Pre-registered decision rules (locked)

### Activity / template / disagreement (CHIP primary)

| Verdict | Rule |
|---------|------|
| **RETAIN_HP** | match level ∈ {L1,L2} ∧ \(n_{\mathrm{ctrl}}\ge5\) ∧ percentile ≥ **90** ∧ effect > **0.05** |
| **KILL_HP_DEMOTION** | percentile < **75** OR effect ≤ **0** (at the level used) |
| **INCONCLUSIVE** | else, OR `INSUFFICIENT_MATCH`, OR level L4 |

### Architecture_m1 (CONTACT primary)

Same numeric thresholds on contact MAE; CHIP percentile reported as secondary only.

### Matched_negative

| Verdict | Rule |
|---------|------|
| **PASS_AS_NEGATIVE** | percentile ≤ **50** OR effect ≤ 0 |
| **NEGATIVE_FAIL** | percentile ≥ **90** ∧ effect > 0.05 (negative slot behaves like activity hit) |
| **INCONCLUSIVE** | else |

### Known_positive `P1_SYSTEM_3primeHS1`

**SKIP** — assay-chain control, not an AG-scored rare SNV in this pool.

### Panel-level kill

- **PANEL_ACTIVITY_CLAIM_WEAKENED** if ≥2 of {C1 TEMPLATE, C2, C3, C3b, A114} are `KILL_HP_DEMOTION`.
- **PANEL_NEGATIVE_BROKEN** if any matched_negative is `NEGATIVE_FAIL`.
- Does **not** open holdout, reshape Stage-3, or authorize wet-lab.

---

## Explicit non-goals

- No new enrichment discovery / E/P shopping  
- No holdout touch  
- No Stage-3 reassignment after this test  
- No claim that AG percentile = biology  

---

## Script

`pilot_scaffold/scripts/run_p3_matched_null_panel.py`
