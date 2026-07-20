# Decision — exp_sva_f_ccre_state_switching (C-A2 true)

**Date:** 2026-07-20  
**Status:** `REJECT` (desk **CLOSED**; gate `FAIL_KILL`)  
**OR:** **0.489** (Woolf 95% CI 0.243–0.985; Fisher p≈0.044)  
**null_results:** `null_results/20260720-sva-f-dels-state-switching.md`

## Verdict

**Terminal desk status: `REJECT` / `FAIL_KILL`.**

Frozen claim (OR(switcher | SVA_F dELS) ≥ 1.4 vs matched non-TE) is **falsified**:

| Arm | OR | Kill OR&lt;1.1? |
|-----|-----:|:---:|
| Primary (N=10 switching biosamples) | **0.489** | yes (also &lt; MCID) |
| Odd panel (5 biosamples) | **0.655** | yes |
| Even panel (5 biosamples) | **0.411** | yes |

Kill rule (≥2 independent panels with OR &lt; 1.1) **met** (2/2).

Direction is **opposite** to the enrichment claim: SVA_F dELS switcher rate **0.147** vs matched
non-TE **0.268** (table [10, 58, 91, 249]; k=5; n_SVA_F=68; 0 undermatched).

## What WAS tested

1. L0 Descriptive prereg (`claim.md` / `controls.md` / `notes.md`) before outcomes.
2. T0: SCREEN Registry-V3 + ENCODE v3 Full-classification panel (`PASS_FREEZE_CANDIDATE`).
   Single-file SCREEN CTS/Signal matrix **absent** (404) — panel beds used as processed
   substitute (documented).
3. Phase B matching lock on chrom / length quartile / GC decile / TSS bin / held-out
   SK-N-SH baseline **before** switching labels (`results/matching_lock.json`).
4. Primary Fisher OR + odd/even falsification panels.

## What was NOT tested

- Causal SVA_F → switching mechanism.
- ChIA-PET / Hi-C AluSz discordance (parked `C-K1-CTCF-chia-fallback`).
- Wet / holdout / C1 E/P.

## Forbidden overclaim language

- Do **not** reframe as “SVA_F protects against switching” without a new claim freeze
  (this desk only REJECTS OR≥1.4 enrichment).
- Do **not** confuse with ChIA-PET C-A2 alias.
- Do **not** reopen C-A1 INCONCLUSIVE or C-K1 BLOCKED_DATA as rescued by this result.

## Gate checklist

| Gate | Status |
|------|--------|
| L0 Descriptive prereg | DONE |
| Match before outcomes | DONE |
| T0 panel ≥8 Full-class beds | PASS (10 + baseline) |
| Primary OR ≥ 1.4 | **FAIL** (0.489) |
| Odd/even kill OR&lt;1.1 in ≥2 | **FAIL_KILL** (2/2) |
| Holdout / wet / C1 | SEALED / FORBIDDEN |

## What this does NOT mean

1. NOT that SVA_F lacks all regulatory biology — only that the frozen switching-enrichment
   OR≥1.4 claim fails on this SCREEN panel.  
2. NOT license for causal or enhancer↔silencer mechanism language.  
3. NOT wet / holdout / C1 authorization.  
4. NOT a ChIA-PET result.

## Next fruit

Recommend **C-H1** (Micro-C vs Hi-C TE recovery) if processed Micro-C loops verified; else
**C-L1** (cross-cell transfer of discordant-TE pattern). Do not auto-start without queue.
See `NEXT_FRUIT_NOTE.md`.
