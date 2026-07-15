# Decision: exp_se_continuous_rank_dichotomization_check

**Date:** 2026-07-10
**Verdict:** REJECT (of the MCID), but with a genuine, non-zero, directionally-consistent
signal below the practical-significance threshold -- qualitatively different from the
prior 5 clean nulls in this direction.

## Result

Pre-registered MCID: `abs(spearman_rho) >= 0.2 AND p_value_permutation < 0.05`

| Cell line | Endpoint | n | Spearman rho | permutation p | MCID? |
|---|---|---|---|---|---|
| K562 | Gnocchi Z | 4776 | -0.009 | 0.539 | No (both fail) |
| K562 | R-loop overlap | 5993 | **-0.146** | 0.0001 | No (delta) |
| K562 | G4 overlap | 5993 | **-0.159** | 0.0001 | No (delta) |
| HepG2 | Gnocchi Z | 1606 | 0.073 | 0.004 | No (both fail) |
| HepG2 | G4 overlap | 1889 | **-0.163** | 0.0001 | No (delta) |

No correlation reaches the pre-registered practical threshold (max \|rho\|=0.163, vs. 0.2
required). By the letter of the MCID, this is also a REJECT.

**But this is not the same shape of null as the prior 5 tests.** Three of five
correlations (K562 R-loop, K562 G4, HepG2 G4) show a small, consistent, statistically
robust (p at the permutation floor, not a borderline value) NEGATIVE relationship between
super-enhancer size and R-loop/G4 overlap -- bigger super-enhancers show *less* R-loop/G4
overlap among their constituent peaks, not more. This is a real, detectable, directionally
consistent signal that the binary SE-vs-typical tests could not have found even in
principle (binary tests cannot detect a within-group gradient). It just doesn't clear the
bar we pre-registered for "practically meaningful."

## Confound check (run before writing this decision, not after seeing a result we liked)

Concern: `overlap_fraction` divides by the constituent peak's own length, not the SE's
length. If bigger SEs happened to have systematically longer constituent peaks, a
denominator-dilution artifact could produce a spurious negative SE-size-vs-overlap-fraction
correlation with no real biology behind it.

Checked directly: SE length vs. constituent peak length, K562, same permutation-test
machinery: **rho=-0.142, p=0.0005** -- SE length is *negatively* (not positively)
correlated with constituent peak length. If anything, this confound would push the
SE-size-vs-overlap-fraction correlation in the OPPOSITE (positive) direction from what was
observed, not explain it away. This does not rule out other confounds, but the specific
denominator-dilution mechanism that would most obviously threaten this result does not
appear to be driving it.

## Relationship to the dichotomization hypothesis (from `cross-domain`/`hypothesis-revival`)

Partial support, not full vindication (as `claim.md` warned before running): the
dichotomization hypothesis predicted a real graded effect masked by binary classification.
We found exactly that shape of result for R-loop and G4 (small but real, directionally
consistent, statistically robust correlation invisible to a binary test) -- but the
magnitude is small enough that it would not have moved any of the 5 binary REJECT verdicts
into PROMOTE territory even if detected earlier. Gnocchi shows no such gradient (rho near
zero both cell lines) -- the dichotomization story does not apply uniformly across all
five original endpoints, only R-loop/G4.

## What This Result Does NOT Mean

1. Does NOT vindicate "super-enhancers aren't real" (Pott & Lieb's actual claim was more
   nuanced -- unclear functional distinctness, not "the size gradient is meaningless").
2. Does NOT mean SE size is unrelated to R-loop/G4 biology -- a real, small, directionally
   consistent effect was found; it simply falls short of the threshold this project
   pre-registered as "worth acting on."
3. Does NOT extend to the typical-enhancer population -- this tested only within the
   SE-constituent group, per the scope limitation stated in `claim.md` before running.
4. Does NOT explain the sign-flips between K562 and HepG2 seen in the original BRD4/MED1
   and Gnocchi binary tests -- this experiment does not address cell-line inconsistency at
   all, only within-cell-line gradients.

## Recommendation

File to `null_results/` as a REJECT-with-signal (not a clean null) -- worth distinguishing
from the prior 5 in the index. The dichotomization hypothesis is now down-weighted but not
dead: it explains a small real effect for 2 of 3 re-tested endpoints, not zero effect, but
also not enough to overturn any prior verdict. Diminishing returns on this specific
direction; the honest close-out for today's "why do 5/5 REJECT" investigation is: partly
dichotomization (small, real, below-threshold gradient for R-loop/G4), partly genuine null
(Gnocchi shows no gradient either way).
