# Decision: TE/Alu common Alu∩CTCF × GTEx blood eQTL (G9b)

**Date:** 2026-07-23  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — INCONCLUSIVE (effect_uncertain; wrong-direction lean)

## Result

G9b fixed G9's two blockers (AF≥0.01 panel n=46; HTTP 400→MISS, error_rate=0)
and re-tested the same estimand on a new freeze.

| Arm | hit | miss | tested | hit-rate |
|-----|----:|-----:|-------:|---------:|
| CASE Alu∩CTCF | 1 | 45 | 46 | 0.022 |
| CTRL Alu non-CTCF | 9 | 37 | 46 | 0.196 |

Fisher p=0.0152 (two-sided). Pre-registered PASS requires case>ctrl and p≤0.01;
REJECT-wrong-direction requires p≤0.01. Neither fires → **INCONCLUSIVE**.

Observed lean is **against** the enrichment hypothesis (controls richer in blood
eQTL hits), but not decisive at α=0.01.

## Evidence chain

- Claim: `tracks/te_alu_3d/09_outputs/prospective/G9b_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`
- Freeze / result / decision under `09_outputs/prospective/g9b_*`
- Tests: `test_g9_eqtl_lib.py` (20 passed)
- Parent G9 remains INCONCLUSIVE (api_error_rate)

## What This Result Does NOT Mean

1. Does not prove Alu∩CTCF SNVs lack blood eQTL effects.  
2. Does not prove depletion either (p above α).  
3. Does not authorize α-hacking or Stage-3 / wet reopen.

## Allowed next steps

- Pause activity enrichment on public blood eQTL for this geography  
- New claim on other chromosomes / erythroid EGA data  
- Wet-lab B0 if human signs
