# Stage-3 background-direction ERRATUM v1

**Date:** 2026-07-21  
**Status:** POST-ANALYSIS INTEGRITY CORRECTION  
**Locked artifacts are not modified:** their SHA256 chains remain valid.

## Corrected statements

Two locked claims describe the `bg_tol_bins=1` near-diagonal background
incorrectly:

- `G4a_stage3_architecture_wt_contact_CLAIM_v1.md` §8 calls the mixed
  0/1/2-bin comparison “conservative”.
- `G4c_stage3_architecture_replic_CLAIM_v1.md` §4 says it compresses
  `enrich_mean`.

For A754 at 10 kb, the observed direction is the opposite:

| background | bg_mean_obs | enrich_mean |
|------------|------------:|------------:|
| exact distance, `tol=0` | 53.1597 | 1.3894 |
| mixed distances, `tol=1` | 44.3158 | 1.6667 |

Thus, in this observed matrix, the mixed pool lowered the background mean and
inflated the enrichment ratio enough to change `FAIL` to `PASS`. The cause is
not assigned beyond the changed distance-pool composition.

## Consequence

- The exact-distance sensitivity decision remains valid.
- G4c correctly uses `bg_tol_bins=0` as its only decision-bearing background.
- No G4a/G4c verdict, frozen anchor, or Stage-3 assignment is upgraded.
- The locked CLAIM files remain unchanged solely to preserve their audit hashes.

## Coordinate-contract note

The frozen GRCh37 anchors are stored as 1-based inclusive Ensembl intervals,
while `analyze_contact` documents half-open intervals. At 10 kb and 25 kb, an
explicit boundary audit confirms that converting starts to 0-based does not
change any E/P midpoint bin used in G4a or G4c. This mismatch is therefore
documented but does not alter the reported scores.

## G4c panel-rule omission

The locked G4c CLAIM does not specify the panel verdict when both slot-level
verdicts are `REPLICATION_PARTIAL`. The runner handles that unobserved
combination fail-closed as `REPLICATION_INCONCLUSIVE`. The actual G4c result
(`REPLICATION_UNSUPPORTED` plus `REPLICATION_INCONCLUSIVE`) does not enter this
fallback branch.
