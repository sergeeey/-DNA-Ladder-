# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `PENDING_PRIMARY`

## Verdict

**T2 CTCF positive-control gate: PASS** (Fisher OR = 5.12 ≥ 2.0; Woolf 95% CI 4.91–5.34).  
Pipeline recovers expected CTCF enrichment at Hi-C loop anchors vs chromosome-preserving
peak shuffle. Status advances to **`PENDING_PRIMARY`** (ready for T3 primary TE analysis
under frozen claim + completed `controls.md` checklist).

**No primary TE subfamily OR has been finalized.** T1 annotation skeleton exists as
`EXPLORATORY_PARTIAL` first-hit tallies only — not a claim result.

## Current gate

| Gate | Status |
|------|--------|
| Deep Research promote | `VALIDATE_DESK` (C-A1; score 7.06) |
| Standard-tier preregistration | Written (`claim.md`, `controls.md`, `notes.md`) |
| T0 ENCODE accession probe | **PASS** |
| Accession freeze | **DONE** — Pol II `ENCFF511QFN`; Hi-C `ENCFF693XIL` |
| Primary bedpe on-disk download + md5 | **DONE** (portal md5 match) |
| CTCF accession freeze | **DONE** — `ENCFF769AUF` (`ENCSR000AKO`) |
| T2 CTCF positive control gate | **PASS** (OR 5.12; threshold ≥2.0) |
| T1 TE annotation skeleton | **EXPLORATORY_PARTIAL** (no primary OR) |
| Primary TE OR analysis | NOT STARTED (blocked until controls checklist) |
| Holdout | SEALED (untouched) |
| Wet-lab / oligos | FORBIDDEN |

### T2 CTCF gate summary

Source: `results/positive_control_ctcf_gate.json`.

| Metric | Value |
|--------|-------|
| Hi-C anchors (unique, chr1–22,X) | 24049 |
| CTCF peaks | 51759 |
| Obs overlap rate | 0.524 |
| Null overlap rate (50 shuffles) | 0.177 |
| Fisher OR | **5.119** |
| Woolf OR 95% CI | 4.910 – 5.337 |
| Gate threshold | OR ≥ 2.0 |
| Verdict | **PASS** → `PENDING_PRIMARY` |

### T0 probe + freeze summary

| Check | Result |
|-------|--------|
| `ENCSR000BZZ` | **WRONG** — ESR1 ChIA-PET |
| `ENCSR444WCX` | **404** |
| Pol II primary | **`ENCFF511QFN`** |
| Hi-C primary | **`ENCFF693XIL`** |
| CTCF control | **`ENCFF769AUF`** (substitution vs TBD — frozen this step) |

## Stop / branch rules

- CTCF gate OR < 2.0 → `BLOCKED_PIPELINE` (not triggered).
- MAPQ≥30 + replication yield OR < 1.1 for all pre-registered subfamilies → `REJECT`.
- Do not invent primary TE ORs before matched-null controls are run.

## What this does NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  
5. Not a finalized primary TE enrichment claim (none yet)

## Next edit to this file

After T3 primary TE OR under frozen claim + controls checklist → PASS / REJECT /
INCONCLUSIVE with honest numbers; file `null_results/` if REJECT/INCONCLUSIVE.
