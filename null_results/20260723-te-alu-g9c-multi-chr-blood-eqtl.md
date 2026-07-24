# Decision: TE/Alu multi-chrom common Alu∩CTCF × GTEx blood eQTL (G9c)

**Date:** 2026-07-23  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — REJECT (negligible blood-eQTL enrichment)

## Result

On a pre-registered panel across chr1/2/6/11 (n=200 case / 200 ctrl; AF 0.01–0.50;
HTTP 400→MISS), GTEx whole-blood cis-eQTL hit-rates were:

| Arm | hit-rate |
|-----|---------:|
| Alu∩HUDEP-2 CTCF | 11/200 = 0.055 |
| Alu outside CTCF±250bp | 4/200 = 0.020 |

risk_diff = +0.035; Fisher p = 0.112. Per claim: |diff| < 0.05 and p > 0.01 →
**REJECT** (`negligible_diff`). No replication.

Together with G9/G9b (INCONCLUSIVE) and Stage-3 contact CLOSED, public-desk
support for “Alu∩CTCF common SNVs carry elevated blood cis-eQTL signal” is
**not obtained**.

## Evidence chain

- Claim / freeze / result / decision under `tracks/te_alu_3d/09_outputs/prospective/G9c_*`
- TE source: UCSC hg38 rmsk filtered locally (`repeatmasker_g9c_alu_sva.bed`;
  bulk `rmsk_hg38.txt.gz` stays local, not committed)
- Tests: `test_g9_eqtl_lib.py` (20 passed)

## What This Result Does NOT Mean

1. Does not prove Alu∩CTCF SNVs never affect expression.  
2. Does not test erythroid / HUDEP-2 eQTL.  
3. Does not reopen Hi-C Stage-3 or wet-lab GO.

## Allowed next steps

- Pause computational activity enrichment  
- EGA erythroblast eQTL (human unlock)  
- Wet-lab B0 signature
