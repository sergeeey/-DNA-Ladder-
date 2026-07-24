# Stage-3 Architecture WT Contact — bg_tol_bins=0 Sensitivity Decision

**Role:** Post-analysis advisory side-car; does NOT change the main panel verdict.
**Sensitivity CLAIM:** `G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_CLAIM_v1.md`
**Parent CLAIM / Decision:**
  `G4a_stage3_architecture_wt_contact_CLAIM_v1.md` (panel verdict **INCONCLUSIVE**)
  `G4a_stage3_architecture_wt_contact_decision_v1.md`
**Freeze:** `stage3_architecture_anchor_freeze_v1.json` (Ensembl 116;
  sha256 `fed26bb76b5c2127…`)
**Manifest:** `stage3_wt_dumps_manifest_v1.json` (sha256 `ac5037bc080893ef…`)
**Baseline pin:** `stage3_architecture_wt_contact_v1.json` (sha256 `9909542b4843c213…`)
**Analysis run:** 2026-07-21T14:28:18.232220+00:00
**bg_tol_bins:** 0 (exact-distance background only)
**Advisory panel verdict (tol=0):** `INCONCLUSIVE`
**Main panel verdict (tol=1):** `INCONCLUSIVE` — **UNCHANGED**

---

## Score transition summary

| Slot | Candidate | Res | Score (tol=1) | Score (tol=0) | Transition | Δbg_n | Δenrich_mean | Δobs_pct |
|------|-----------|-----|--------------|--------------|-----------|-------|-------------|---------|
| ARCH_01 | A754 | 10 kb | `PASS` | `FAIL` | **DOWNGRADED** | -200.0000 | -0.2773 | -0.0036 |
| ARCH_01 | A754 | 25 kb | `FAIL` | `FAIL` | **STABLE** | -80.0000 | -0.0409 | +0.2079 |
| ARCH_02 | A518 | 10 kb | `FAIL` | `FAIL` | **STABLE** | -166.0000 | -0.2074 | -0.0253 |
| ARCH_02 | A518 | 25 kb | `UNRESOLVED_SAME_BIN` | `SAME_BIN_GUARD_VIOLATION` | **SAME_BIN_BLOCKED_HARD_FAIL** | n/a | n/a | n/a |

---

## Per-slot details

### ARCH_01 — A754 (chr11:75445532:G:A)

**Sensitivity outcome (bg_tol_bins=0):** `UNSUPPORTED`

#### 10 kb

| metric | value |
|--------|-------|
| score (bg_tol=0) | `FAIL` |
| primary_obs | 73.85924 |
| primary_oe | 1.6989803 |
| bg_n (tol=0) | 99 |
| enrich_mean | 1.3893839343955179 |
| obs_percentile | 0.9595959595959596 |
| focal_row_nonzero | 90 |

Transition: `PASS` → `FAIL` — **DOWNGRADED**

#### 25 kb

| metric | value |
|--------|-------|
| score (bg_tol=0) | `FAIL` |
| primary_obs | 191.03401 |
| primary_oe | 1.5165274 |
| bg_n (tol=0) | 39 |
| enrich_mean | 1.1830612382737593 |
| obs_percentile | 0.8717948717948718 |
| focal_row_nonzero | 41 |

Transition: `FAIL` → `FAIL` — **STABLE**

### ARCH_02 — A518 (chr11:518575:C:A)

**Sensitivity outcome (bg_tol_bins=0):** `INCONCLUSIVE`

#### 10 kb

| metric | value |
|--------|-------|
| score (bg_tol=0) | `FAIL` |
| primary_obs | 88.683716 |
| primary_oe | 2.039987 |
| bg_n (tol=0) | 82 |
| enrich_mean | 1.1828582440004403 |
| obs_percentile | 0.8658536585365854 |
| focal_row_nonzero | 78 |

Transition: `FAIL` → `FAIL` — **STABLE**

#### 25 kb

| metric | value |
|--------|-------|
| error | same_bin_guard_violation |
| message | HARD-FAIL: E_mid_bin == P_mid_bin == 500000 at binsize=25000. bg_tol_bins=0 on a same-bin pair produces a diagonal-only background; computation blocked. |

Transition: `UNRESOLVED_SAME_BIN` → `SAME_BIN_GUARD_VIOLATION` — **SAME_BIN_BLOCKED_HARD_FAIL**


---

## Interpretation constraints

- **This is an advisory-only sensitivity check.**
- The main panel verdict (**INCONCLUSIVE**) is unchanged.
- Stage-3 slot assignments remain LOCKED (see registry, 2026-07-15).
- No enhanced contact language is permitted from this result alone.
- NOT CLAIMED: enhancer–promoter contact, target-gene identity, allele effect, expression
  change, regulation, or pathogenicity.
- G4b allele ΔContact: NOT TESTED.
- Wet-lab: NO-GO (B0 UNSIGNED as of 2026-07-21).
- Single WT replicate; no independent replicate Hi-C available.

## Caveats

- Terminology in the locked parent claim is corrected by
  `G4_stage3_background_direction_ERRATUM_v1.md`: the mixed tol=1 pool
  inflated A754 enrichment in the observed parent matrix.
- A754 10 kb is the principal sensitivity finding: `PASS` at tol=1 becomes
  `FAIL` at exact distance because enrich_mean falls below 1.5. The original
  PASS is therefore background-definition-sensitive and must not be upgraded.
- A518 25 kb: `SAME_BIN_GUARD_VIOLATION` (E_mid == P_mid at 25 kb; diagonal background
  at bg_tol_bins=0 is undefined; computation hard-failed, consistent with parent UNRESOLVED_SAME_BIN).
- A754 25 kb: bg_n at tol=0 is much smaller than at tol=1 (only exact-distance pixels);
  result validity depends on bg_n remaining ≥ 20.
- Enrichment comparisons with tol=1 baseline are informational only; same-distance pool
  composition differs.
- hg19 coordinates derived from GRCh38 via Ensembl REST (same as parent claim).
- Architecture candidates; contact evidence alone does not confirm causal role.
