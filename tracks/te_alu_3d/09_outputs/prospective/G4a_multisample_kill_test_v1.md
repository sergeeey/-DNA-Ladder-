# G4a multi-sample kill test v1

**Date:** 2026-07-15  
**Overall:** `PASS_DESK_ROBUST`  
**Kills triggered:** none  
**Action:** Retain G4a PASS_DESK; multi-sample support

## Pre-registered kill criteria (before multi-sample view)

- **K1:** PASS only in GSM4873113 among GW Hi-C
- **K2:** KR PASS wiped out by VC on both resolutions
- **K3:** WT primary Contact/OE missing

## Sample verdicts (KR, tol±1 bin)

| Sample | Alias | Assay | Verdict | enrich10 | OE10 | enrich25 | OE25 |
|--------|-------|-------|---------|---------:|-----:|---------:|-----:|
| GSM4873113 | WT_GW | genome_wide | `PASS_DESK` | 3.4020338783420794 | 3.198061 | 2.451125527444454 | 2.1376076 |
| GSM4873114 | DEL_GW | genome_wide | `PASS_DESK` | 3.012541669949263 | 3.3252444 | 3.4288570738026047 | 3.2329397 |
| GSM4873115 | INV_GW | genome_wide | `PASS_DESK` | 3.4892002095724837 | 4.0461335 | 3.0355824682498915 | 3.0910716 |
| GSM4873117 | DEL_CAP | capture_betaglobin | `INCONCLUSIVE_LEAN_POSITIVE` | 1.053909781306675 | 2.9910064 | 3.4362458963679363 | 3.5701554 |
| GSM4873118 | INV_CAP | capture_betaglobin | `INCONCLUSIVE_LEAN_POSITIVE` | 0.8186924377969496 | 2.302375 | 2.1172077064982453 | 2.2203712 |

## VC sensitivity (WT GSM4873113)

```json
{
  "10000": {
    "resolution_score": "PASS",
    "enrich": 3.29408916657413,
    "oe": 2.1924558
  },
  "25000": {
    "resolution_score": "PASS",
    "enrich": 2.396702434355541,
    "oe": 1.4945189
  }
}
```

## Leave-one-out (GW enrich 10 kb)

```json
[
  {
    "left_out": "GSM4873113",
    "mean_enrich_remaining": 3.2508709397608735
  },
  {
    "left_out": "GSM4873114",
    "mean_enrich_remaining": 3.4456170439572817
  },
  {
    "left_out": "GSM4873115",
    "mean_enrich_remaining": 3.207287774145671
  }
]
```

## Interpretation constraint

This does **not** prove C1 allele effect. It only tests whether locked E–P WT contact
is an artifact of a single KR dump.

JSON: `G4a_multisample_metrics_v1.json`
