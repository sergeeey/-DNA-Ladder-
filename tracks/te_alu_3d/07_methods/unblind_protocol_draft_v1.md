# Unblind protocol draft v1 — confirmatory holdout (NOT authorized)

**Date:** 2026-07-14  
**Status:** `DRAFT_ONLY`  
**Authority:** `holdout_manifest.yaml` → `unblind_authorized: false` (unchanged by this draft)  
**Router:** R3/R5 — draft allowed; execution **FORBIDDEN** until gates below PASS

This document defines *how* unblinding would work. It does **not** unblind, score, or inspect outcome labels.

---

## Purpose

Pre-register confirmatory analysis of sealed windows HO_A / HO_B / HO_C  
(`chr11:64–68 Mb`, non-HBB) under primary estimand **T** (`total_te_effect`).

---

## Hard preconditions (all required)

```text
[ ] scientific_freeze_v1 still FROZEN; primary_estimand = total_te_effect
[ ] score_freeze primary admitted: ARCHCODE OR validated 2nd type (not PWM alone)
[ ] archcode_admission_gate OR second_scorer_admission_gate → AVAILABLE / PASS
[ ] scorer_benchmark PASS for the admitted primary
[ ] holdout windows identical to sealed_at (no window shopping)
[ ] leakage_audit PASS on any prospective ranking path
[ ] dating human note sets unblind_authorized: true (who / why / commit hash)
```

If any box fails → **STOP**. Do not score `pilot_scaffold/data/holdout/`.

---

## What remains sealed until GO

| Artifact | Action before GO |
|----------|------------------|
| Holdout VCF/TSV under `data/holdout/` | no enrichment / no ranking-by-score |
| Outcome-linked ClinVar severity on holdout alleles | no peek for candidate pick |
| Any “pearl” shortlist from holdout scores | forbidden |

Desk geography (L-HO_*) and public CTCF density **are** allowed (already used).

---

## Unblind sequence (only after GO)

```text
1. Set unblind_authorized: true in holdout_manifest.yaml (+ dated human note)
2. Freeze analysis script versions + random seed in a signed run card
3. KC0 cell-context check (HUDEP-2)
4. QC gates 1–4 on holdout variants
5. Control A matching for estimand T
6. Score with ADMITTED primary only (version + hash recorded)
7. Block permutation + cluster-aware effective N
8. Report C as secondary only (no primary switch)
9. Write Decision: PASS | FAIL | INCONCLUSIVE into registry
10. Register nulls in Null Results / registry (no silent discard)
```

---

## PASS / FAIL (confirmatory enrichment)

```text
PASS:  T direction TE_gt_control AND perm_p < alpha AND cluster-aware N_eff gate met
FAIL:  direction fails OR perm_p ≥ alpha OR N_eff gate fails
INCONCLUSIVE: QC incompleteness after frozen gap policy — do not soft-promote
```

Language after PASS still **forbidden** as confirmatory biology claim:

```text
FORBIDDEN: "3D genome disruption" / pathogenicity / wet-lab GO without G1–G9
ALLOWED: predicted CTCF-motif disruption enrichment under frozen protocol
```

---

## Architecture / cultivation fork (separate)

Unblind of Track A enrichment is **orthogonal** to allele cultivation:

- Cultivation freeze (G3–G9) needs admitted primary + leakage-free ranking  
- May use non-holdout panels **or** post-unblind holdout alleles under a separate protocol note  
- G4 allele E–P still requires observed WT contact (see `G4_contact_desk_pass_v1.md`)

Do not use HBB T/C results to choose alleles.

---

## Explicit non-goals of this draft

- Does not set `unblind_authorized: true`  
- Does not run scoring  
- Does not fetch new holdout labels  
- Does not authorize wet-lab

---

## Sign-off block (empty until real GO)

```yaml
unblind_authorized: false
draft_version: v1
draft_date: "2026-07-14"
executed_by: null
executed_at: null
primary_scorer_id: null
primary_scorer_hash: null
git_commit: null
human_gate: null
```
