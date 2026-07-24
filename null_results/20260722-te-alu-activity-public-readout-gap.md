# Decision: TE/Alu rare-panel activity public-readout gate

**Date:** 2026-07-22  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — DATA_GAP_STOP (no effect test run)

## Result

After Stage-3 contact closure, the next planned computational branch was
intersection of rare Alu/SVA CTCF-disruption candidates with public
MPRA / caQTL / eQTL / CRISPR-screen readouts in erythroid context.

The pre-registered data-availability gate failed:

- No open HUDEP-2 genome-wide MPRA of rare Alu/SVA CTCF SNVs
- No open erythroid caQTL covering the panel
- BLUEPRINT erythroblast eQTL is EGA-controlled (not used)
- Open blood eQTL maps are common-variant; the r4 panel is 12/12 AF < 0.01
  → structural POWER_FAIL

No panel×readout p-values or betas were queried. Intersection and replication
steps were cancelled by design.

## Evidence chain

- Claim: `tracks/te_alu_3d/09_outputs/prospective/G8_activity_public_readout_CLAIM_v1.md`
- Gate: `tracks/te_alu_3d/09_outputs/prospective/G8_activity_public_readout_data_gate_v1.md`
- Decision: `tracks/te_alu_3d/09_outputs/prospective/G8_activity_public_readout_decision_v1.md`

## What This Result Does NOT Mean

1. It does not show that panel variants lack regulatory activity.
2. It does not replace or reopen the Stage-3 Hi-C contact null.
3. It does not justify wet-lab GO or holdout unblind.
4. It does not authorize same-data Hi-C rescue or post-hoc common-SNP pivots
   without a new claim.

## Allowed next steps

- Unlock EGA / new open erythroid activity maps → re-gate  
- Separate claim for common Alu CTCF SNPs × blood eQTL (new freeze)  
- Remain computationally paused on activity until data exists
