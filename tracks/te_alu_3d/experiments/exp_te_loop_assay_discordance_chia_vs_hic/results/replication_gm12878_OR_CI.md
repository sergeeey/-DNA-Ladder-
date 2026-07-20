# Replication — AluSz OR (GM12878)

**Computed:** `2026-07-20T10:49:24.704819+00:00`  
**Status:** `DONE`  
**Primary TE:** `AluSz` (frozen; same as K562)  
**Replication verdict:** `INCONCLUSIVE_REPLICATION`

## Frozen accessions

| Role | Experiment | File |
|------|------------|------|
| Pol II ChIA-PET | `ENCSR905HWW` | `ENCFF913VWM` |
| Hi-C loops | `ENCSR410MDC` | `ENCFF781ASD` |
| CTCF peaks (gate) | `ENCSR000DZN` | `ENCFF796WRU` |

See `ACCESSION_FREEZE_replication_v1.md`.

## Pipeline

Identical to T3 K562 desk: merged ≥1 kb anchors; Fisher OR for AluSz on fixed 1 kb
midpoint windows. Descriptive association in processed public call sets only.

## Anchor counts

| Arm | Raw unique | Merged ≥1 kb | 1 kb windows |
|-----|------------|--------------|--------------|
| Pol II | 896183 | 371255 | 371255 |
| Hi-C | 23861 | 17130 | 17130 |

## AluSz statistics

| Metric | Value |
|--------|-------|
| Pol II AluSz+ / n | 25521 / 371255 (rate 0.0687) |
| Hi-C AluSz+ / n | 953 / 17130 (rate 0.0556) |
| Fisher OR | **1.2524** |
| Woolf 95% CI | 1.1718 – 1.3386 |
| Chrom block-bootstrap 95% CI | 1.1721 – 1.3454 |
| Matched-null emp. p | 0.004975 (n_perm=200) |

**Verdict note:** OR=1.2524 between 1.15 and 1.3; replication inconclusive for falsification rule.

## CTCF positive gate (GM12878)

| Metric | Value |
|--------|-------|
| Fisher OR | 10.7356 |
| Woolf 95% CI | 10.2561 – 11.2376 |
| Gate threshold | ≥ 2.0 |
| Verdict | **PASS** |

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT a license to switch primary TE post-hoc.
3. NOT wet-lab / holdout / C1 authorization.
4. NOT multi-assay MAPQ on BAM (processed bedpe only).

