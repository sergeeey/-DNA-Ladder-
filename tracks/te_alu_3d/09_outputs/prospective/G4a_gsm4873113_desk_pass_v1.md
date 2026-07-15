# G4a desk pass — GSM4873113 (HUDEP-2 WT Hi-C)

**Date:** 2026-07-14  
**Method:** `juicer_tools dump` observed/OE KR on local `.hic`  
**Locks:** `C1_claim_freeze_pack_v1.md` / `c1_ep_liftover_hg19.yaml`  
**Verdict:** `PASS_DESK`

## Status translation

| Gate | Status |
|------|--------|
| G4a WT Contact(E,P) | **PASS_DESK** (desk) |
| G4b allele ΔContact | NOT TESTED |
| Architecture freeze | still **NO-GO** until P1 + edit/assay path |
| Allowed language | still activity-candidate unless Branch A fully opens |

## Locus (hg19)

| Anchor | Coordinate |
|--------|------------|
| E | chr11:62157472-62162472 |
| P | chr11:62457472-62462472 |
| C1 | chr11:62521395 |

## Metrics 10 kb

| binsize | 10000 |
| primary pair | 62150000 × 62450000 |
| observed KR | 7.131877 |
| OE KR | 3.198061 |
| same-dist bg n | 118 |
| bg mean obs | 2.0963568427118644 |
| enrichment vs mean | 3.4020338783420794 |
| obs percentile | 1.0 |
| OE percentile | 1.0 |
| C1-row nonzero | 139 |

## Metrics 25 kb

| binsize | 25000 |
| primary pair | 62150000 × 62450000 |
| observed KR | 29.820076 |
| OE KR | 2.1376076 |
| same-dist bg n | 56 |
| bg mean obs | 12.16587060357143 |
| enrichment vs mean | 2.451125527444454 |
| obs percentile | 0.9821428571428571 |
| OE percentile | 0.9821428571428571 |
| C1-row nonzero | 61 |

## Decision rule (pre-registered for this desk)

```text
PASS_DESK if at BOTH 10kb and 25kb:
  primary_obs present
  AND enrichment_vs_mean_bg ≥ 1.5
  AND obs percentile among same-distance bins ≥ 0.75
  AND OE ≥ 1.2
  AND C1-row has nonzero coverage
```

Soft positive / mixed → INCONCLUSIVE(_LEAN_POSITIVE).  

## Amendment 2026-07-15 — multi-sample robustness

Re-tested locked E–P on GSM4873113–3115 (GW) + VC norm + leave-one-out.  
**Result:** `PASS_DESK_ROBUST` · kills K1–K3 **none**.  
See `G4a_multisample_kill_test_v1.md`. Capture 3116 dump failed (wrong bait locus).  
Allele effect of C1 still **NOT TESTED**.

## Caveats

- Original analysis was a single sample `.hic` dump; multi-sample amendment above.
- E/P remain K562-proxy locks mapped to hg19 — gene identity of P not claimed.
- KR values are relative; do not over-interpret absolute counts.
- Capture Hi-C of this series is β-globin-targeted and was not used for C1.

## Next

- If PASS / lean-positive: download GSM4873114/3115 for P1-system.
- If FAIL: Branch B activity; drop architecture primary claim.
- Do not rewrite E/P after seeing these numbers.
