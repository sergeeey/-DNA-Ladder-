# P2 expand — C1 satmut AG (all A→G + random 100)

**Status:** PRE-REGISTERED addendum to `C1_saturation_mutagenesis_v1`  
**Date locked:** 2026-07-16  
**Does not change S1/S2/S3 thresholds** (locked in v1 before first AG ranks).

## Why expand

v1 scored **C1 + top-100 |PWM|** only (n=101/903). That is **stricter against C1**
(competitors already motif-strong) but leaves open:

1. **S3 composition** — mean of *all* other A→G in the 301 bp window (not just PWM-rich)
2. **Background density** — random non-PWM substitutions as a less biased peer set

## Expand design (locked before run)

| Stratum | Action |
|---------|--------|
| Prior v1 AG | **reuse** (no re-score) |
| All A→G in 301 bp window except C1 | AG-score every missing site (~60 A positions) |
| Random 100 | AG-score 100 other single-base alts not already scored (seed=`20260716`) |

Union set = evaluation universe for S1/S2/S3.

## Same kill rules (unchanged)

- **S1:** C1 not in top 5% by `chip_tf_mae` among AG-scored union
- **S2:** ≥20 other subst with `chip_tf_mae ≥ 0.9 × C1`
- **S3:** mean CHIP_TF of other A→G (now as complete as scored) ≥ C1

Retain lean if no kills fire.

## Explicit non-goals

- Not full 903 AG (budget)
- Not wet-lab / holdout / Stage-3 reshape
- Not changing primary metric away from `chip_tf_mae`

## Script

`pilot_scaffold/scripts/run_c1_satmut_ag_expand_v2.py`  
Out: `C1_saturation_mutagenesis_v2.md` / `.json`
