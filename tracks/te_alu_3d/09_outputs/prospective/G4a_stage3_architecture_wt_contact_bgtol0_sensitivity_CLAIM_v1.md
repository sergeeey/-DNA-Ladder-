# Stage-3 Architecture WT Contact bg_tol_bins=0 Sensitivity — CLAIM v1

**Pre-registration date:** 2026-07-21
**L0 gate:** Descriptive
**Status:** LOCKED — do not edit after analysis begins
**Role:** Post-analysis advisory side-car; does NOT supersede or modify the main claim/result/decision
**Parent claim:** `G4a_stage3_architecture_wt_contact_CLAIM_v1.md` (bg_tol_bins=1; panel verdict INCONCLUSIVE)

---

## 1. Purpose

The main analysis used `bg_tol_bins=1` (tolerance ±1 bin), which for short-range anchor pairs
mixes diagonal (0-bin), 1-bin, and 2-bin background pixels.  §8 of the parent claim acknowledged
this as a "conservative but heterogeneous near-diagonal comparison".

This sensitivity check re-analyzes the **same frozen dump files** using `bg_tol_bins=0`
(exact-distance background only) to quantify how much the scores depend on background pool
composition.

**This result does NOT:**
- Change the main panel verdict (INCONCLUSIVE)
- Change Stage-3 slot assignments (LOCKED per registry 2026-07-15)
- Constitute an independent replication
- Use new Hi-C data, new juicer_tools/Java calls, new network requests, or any holdout access

**This result DOES:**
- Report score transitions: STABLE / UPGRADED / DOWNGRADED / CHANGED / SAME_BIN_BLOCKED_HARD_FAIL
- Quantify bg_n and enrich_mean under exact-distance background
- Serve as an advisory-only sensitivity comparison

---

## 2. Locked slots (non-holdout, GRCh38)

Same as parent claim.

| Slot ID | Candidate | Variant (GRCh38) | Registry key |
|---------|-----------|-----------------|--------------|
| ARCH_01 | A754 | chr11:75445532:G:A | architecture_strong_1 |
| ARCH_02 | A518 | chr11:518575:C:A | architecture_strong_2 |

**Holdout:** SEALED — not accessed, not unblinded, no change.

---

## 3. Analysis parameters

- **bg_tol_bins:** 0 (exact-distance background only; tol = binsize × 0 = 0 bp)
- **Dumps:** same 8 files as main analysis (no new juicer_tools calls, no Java, no network)
- **Freeze:** `stage3_architecture_anchor_freeze_v1.json` (Ensembl 116; sha256 verified before run)
- **Manifest:** `stage3_wt_dumps_manifest_v1.json`
  - Created **before** the sensitivity runner is executed
  - Contains sha256 of: freeze JSON, baseline result JSON, all 8 dump files, this CLAIM file
- **Baseline pin:** `stage3_architecture_wt_contact_v1.json` sha256 pinned in manifest;
  runner verifies file has not changed before proceeding
- **Library:** `hic_contact_lib.py` unmodified; calls `analyze_contact(bg_tol_bins=0)`,
  then `score_resolution` / `sample_verdict` (thresholds unchanged from parent claim)

---

## 4. Same-bin guard (hard-fail)

When E_mid_bin == P_mid_bin the inter-anchor distance is 0.  With `bg_tol_bins=0` the background
pool would consist only of diagonal pixels at distance 0, which is not a valid same-distance
background for an E–P contact comparison.

**Rule:** if E_mid_bin == P_mid_bin for any (slot, resolution), the computation for that pair is
**HARD-FAILED** (`SameBinGuardError` raised; caught by the runner; recorded as score =
`SAME_BIN_GUARD_VIOLATION`).  The runner does **not** call `analyze_contact` for that case and
continues with remaining (slot, resolution) combinations.

**Known same-bin case:** ARCH_02 A518 at 25 kb (also `UNRESOLVED_SAME_BIN` in parent claim).

---

## 5. Score transition taxonomy

| Label | Definition |
|-------|-----------|
| STABLE | old_score == new_score (both analysable) |
| UPGRADED | new_score = PASS, old_score ≠ PASS |
| DOWNGRADED | old_score = PASS, new_score ≠ PASS |
| CHANGED | any other non-stable, non-upgrade, non-downgrade transition |
| SAME_BIN_BLOCKED_HARD_FAIL | E_mid == P_mid at bg_tol_bins=0; guard raised; computation blocked |

---

## 6. Decision rule

**Advisory only** — no pre-registered pass/fail threshold.

The sensitivity result records for each (slot, resolution): old_score, new_score, transition,
and key metric deltas (Δbg_n, Δenrich_mean, Δobs_percentile).

**The main claim panel verdict (INCONCLUSIVE) is unchanged regardless of sensitivity scores.**
No language implying confirmed contact, regulatory role, or pathogenicity is permitted.

---

## 7. Scope constraints

- allele_effect: NOT_TESTED
- G4b allele ΔContact: NOT_TESTED
- wet-lab: NO_GO (B0 UNSIGNED as of 2026-07-21)
- No new Hi-C data, no juicer_tools/Java calls, no network requests
- No holdout access
- Language constraint (identical to parent claim): no "regulatory", "pathogenic", "causal",
  "enhancer–promoter", or "target gene" phrasing

---

## 8. Integrity ordering

1. This CLAIM file is written **before** the manifest is created.
2. Manifest (`stage3_wt_dumps_manifest_v1.json`) is created **before** the runner executes.
3. Runner verifies freeze hash → manifest hash → 8 dump hashes → baseline JSON pin
   before computing any metrics.
4. Sensitivity result is written to separate files:
   - `stage3_architecture_wt_contact_bgtol0_sensitivity_v1.json`
   - `G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_decision_v1.md`
5. Parent result (`stage3_architecture_wt_contact_v1.json`) and decision MD are **not** modified.
