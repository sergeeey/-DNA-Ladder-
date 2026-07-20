# Notes — exp_sva_f_ccre_state_switching (C-A2 true)

**Date:** 2026-07-20  
**Source:** Autonomous desk continuation after C-K1 `BLOCKED_DATA`. Human standing order:
start **true C-A2** = SVA_F dELS state switching (Deep Research regulatory-state fruit),
**NOT** the ChIA-PET variant that was temporarily queued under the C-A2 id.

## ID correction

| ID | Estimand | Status |
|----|----------|--------|
| **C-A2** (this desk) | SVA_F dELS active↔inactive switching vs matched non-TE | **ACTIVE** |
| `C-K1-CTCF-chia-fallback` | CTCF ChIA-PET vs Hi-C AluSz discordance | Remains **PARKED** (not this experiment) |
| C-K1 PLAC | H3K4me3 PLAC vs Hi-C AluSz | CLOSED `BLOCKED_DATA` |

Registry must show C-A2 → this path (`exp_sva_f_ccre_state_switching/`), not ChIA-PET.

## Why this estimand

SVA_F elements are young, primate-specific, and frequently annotated near regulatory
chromatin. A cheap descriptive test asks whether SVA_F-overlapping **dELS** flip
active/inactive across ENCODE biosamples more often than composition-matched non-TE dELS.
Publishable null is acceptable.

## SCREEN matrix note

No single Registry-V3 “multi-cell activity matrix” file was exposed at
`downloads.wenglab.org/Registry-V3/` (directory listing 403; guessed CTS/Signal URLs 404).
ENCODE releases **per-biosample** processed cCRE beds with Full-classification — these are
the processed substitute and are frozen as a panel (≥8 required; target ~10 switching + 1
held-out baseline).

## Pipeline order (honesty)

```text
T0  probe + ACCESSION_FREEZE (metadata)
T1  download registry / panel / rmsk / TSS / 2bit
T2  universe + covariates + 1:k match   ← STOP: no switcher yet
T3  attach switching labels → Fisher OR → odd/even kill
T4  decision (+ null_results if FAIL/REJECT/INCONCLUSIVE)
```

## Explicit non-actions

- Do not auto-start wet / holdout / C1 E/P  
- Do not reinterpret this as ChIA-PET C-A2  
- Do not match on switching-panel activity  
- Do not promote exploratory alternate switcher definitions post hoc
