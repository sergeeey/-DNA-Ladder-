# G8 — Rare Alu/SVA activity public-readout — DECISION v1

**Date:** 2026-07-22  
**Claim:** `G8_activity_public_readout_CLAIM_v1.md`  
**Gate:** `G8_activity_public_readout_data_gate_v1.md`  
**Verdict:** **DATA_GAP_STOP**

---

## Result

The pre-registered sequence stopped at the data-availability gate.

| Check | Outcome |
|-------|---------|
| Open HUDEP-2 / erythroid MPRA of Alu/SVA rare CTCF SNVs | FAIL — none found |
| Open erythroid caQTL covering the panel | FAIL |
| BLUEPRINT erythroblast eQTL | BLOCKED — EGA/DAC |
| Open whole-blood cis-eQTL (GTEx / eQTL Catalogue / eQTLGen / SABR) | POWER_FAIL — panel 12/12 AF < 0.01 |
| Effect lookup on panel coordinates | **Not performed** (forbidden under STOP) |
| Stage-3 contact reopen | **Not performed** (branch closed) |

**Panel intersection and replication steps are cancelled** for this claim version.

---

## What this does NOT mean

1. Does **not** mean Alu/SVA CTCF-disrupting rare SNVs lack expression or MPRA effects.
2. Does **not** falsify or support the broader TE/Alu regulatory hypothesis.
3. Does **not** reopen Stage-3 Hi-C contact analysis.
4. Does **not** authorize wet-lab purchase, oligos, or holdout unblind.
5. Does **not** license a silent pivot to common-variant blood eQTL enrichment
   without a new pre-registered claim and panel freeze.

---

## Next allowed moves

1. Human unlocks EGA erythroblast eQTL → new claim with rare-variant plan  
2. New open erythroid MPRA/caQTL appears → re-run gate  
3. Optional **new** L0 claim: common Alu/SVA CTCF-overlapping SNPs × blood eQTL
   (different estimand; must freeze before peeking)  
4. Remain paused on computational activity until one of the above

---

## Filing

Null filing: `null_results/20260722-te-alu-activity-public-readout-gap.md`
