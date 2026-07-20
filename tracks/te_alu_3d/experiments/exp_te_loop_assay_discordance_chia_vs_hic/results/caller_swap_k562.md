# Caller-swap sensitivity — K562 AluSz OR (T6)

**Computed:** `2026-07-20T12:21:37.440096+00:00`  
**Pol II fixed:** `ENCFF511QFN`  
**Primary TE:** `AluSz` (frozen)  
**Mustache:** UNAVAILABLE_ON_ENCODE_K562_GRCh38

## Estimand

Same as T3: Fisher OR for AluSz in fixed 1 kb midpoint windows of merged
anchors — Pol II ChIA-PET vs each Hi-C loop call set (K562 / GRCh38).
Descriptive only; not causal; not a new primary estimand.

## Results

| Role | Hi-C file | Caller | n Hi-C windows | AluSz Fisher OR | Woolf 95% CI | Desk verdict |
|------|-----------|--------|----------------|-----------------|--------------|--------------|
| PRIMARY_FROZEN | `ENCFF693XIL` | HiCCUPS (juicertools merged_loops_30) | 17183 | **0.9075** | 0.8514–0.9673 | `FAIL_DESK_PRIMARY` |
| CALLER_SWAP_PRIMARY | `ENCFF657QKE` | DELTA v1.9 predicted_loops_merged | 12094 | **0.9129** | 0.8462–0.9849 | `FAIL_DESK_PRIMARY` |
| CALLER_SWAP_SECONDARY_ASSAY | `ENCFF256ZMD` | intact Hi-C localizer localized_loops_30 (juicertools) | 37342 | **1.1066** | 1.0548–1.1609 | `INCONCLUSIVE_DESK` |

## Interpretation

- Primary HiCCUPS OR ≈ **0.908** (`FAIL_DESK_PRIMARY`).
- DELTA caller-swap OR ≈ **0.913** (`FAIL_DESK_PRIMARY`).
Caller-swap **does not reverse** K562 FAIL: DELTA OR 0.913 and HiCCUPS OR 0.908 both remain < 1.1 (depletion / null enrichment). Does **not** convert three-cell pattern to REJECT (replication arms still mid-zone) nor to SUPPORT.

## Notes

- ENCODE portal search (2026-07-20): no released K562 GRCh38 bedpe loops tagged to Mustache software. Caller-swap uses DELTA (same experiment) instead of Mustache.
- Intact localizer (`ENCFF256ZMD`) is assay+caller sensitivity, not a pure
  within-library algorithm swap.
- Does **not** rescue K562 enrichment claim (MCID ≥ 1.3) if OR remains < 1.1,
  nor convert mid-zone replication cells into SUPPORT.

## What this does NOT mean

1. NOT proof that HiCCUPS vs DELTA is biologically superior.
2. NOT a Mustache comparison (Mustache file absent on portal).
3. NOT causal TE → loop; NOT wet/holdout/C1 authorization.
4. NOT a license to switch primary TE or rebrand FAIL as SUPPORT.
