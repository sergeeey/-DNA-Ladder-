# Decision: TE/Alu common Alu∩CTCF × independent HUDEP-2 Hi-C (G10)

**Date:** 2026-07-24  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — REJECT (no PASS slots; ≥2 UNSUPPORTED)

## Result

Four pre-declared common Alu∩CTCF anchors on chr11 (excluding Stage-3 A754/A518),
contact-tested on **GSE201820 noIAAdiff** (independent of GSM4873113), KR 10/25 kb,
`bg_tol_bins=0`:

| Slot | Variant | Outcome |
|------|---------|---------|
| G10_01 | chr11:304951:C:T | INCONCLUSIVE (same-bin both resolutions) |
| G10_02 | chr11:696612:G:C | INCONCLUSIVE (same-bin both resolutions) |
| G10_03 | chr11:765550:G:A | UNSUPPORTED (FAIL/FAIL) |
| G10_04 | chr11:3564660:C:T | UNSUPPORTED (FAIL/FAIL) |

Panel: **REJECT** (`no_pass_majority_unsupported`) — 0 PASS, 2 UNSUPPORTED among 4 OK slots.
noIAAundiff informational arm skipped (no local mirror; not used in panel rule).

## Evidence chain

- Claim / freeze / dumps / decision under `tracks/te_alu_3d/09_outputs/prospective/G10_*`
- Scripts: `freeze_g10_common_alu_ctcf_anchors.py`, `run_g10_common_alu_ctcf_indep_hic.py`
- Tests: `test_g10_indep_hic.py`

## What This Result Does NOT Mean

1. Not a rescue or re-analysis of Stage-3 A754/A518.  
2. Not GSM4873113 same-data fishing.  
3. Not regulatory / architecture / causal language.  
4. Not wet-lab GO / holdout unlock.

## Allowed next steps

- Human B0 wet signature  
- EGA erythroblast unlock with new claim  
- **Not:** more Hi-C on these anchors / GSM4873113 / further blood/LCL eQTL tissue fishing
