# Replication — AluSz OR (HCT116)

**Computed:** `2026-07-20T12:09:14.340572+00:00`  
**Status:** `DONE`  
**Primary TE:** `AluSz` (frozen; same as K562)  
**Replication verdict:** `INCONCLUSIVE_REPLICATION`

## Frozen accessions

| Role | Experiment | File |
|------|------------|------|
| Pol II ChIA-PET | `ENCSR035PVZ` | `ENCFF322FOT` |
| Hi-C loops | `ENCSR123UVP` | `ENCFF060QTI` |
| CTCF peaks (gate) | `ENCSR240PRQ` | `ENCFF463FGL` |

See `ACCESSION_FREEZE_replication_HCT116_v1.md`.

## Pipeline

Identical to T3 K562 desk: merged ≥1 kb anchors; Fisher OR for AluSz on fixed 1 kb
midpoint windows. Descriptive association in processed public call sets only.

## Anchor counts

| Arm | Raw unique | Merged ≥1 kb | 1 kb windows |
|-----|------------|--------------|--------------|
| Pol II | 223948 | 118680 | 118680 |
| Hi-C | 9160 | 7721 | 7721 |

## AluSz statistics

| Metric | Value |
|--------|-------|
| Pol II AluSz+ / n | 8873 / 118680 (rate 0.0748) |
| Hi-C AluSz+ / n | 458 / 7721 (rate 0.0593) |
| Fisher OR | **1.2802** |
| Woolf 95% CI | 1.1620 – 1.4103 |
| Chrom block-bootstrap 95% CI | 1.1782 – 1.3930 |
| Matched-null emp. p | 0.004975 (n_perm=200) |

**Verdict note:** OR=1.2802 between 1.15 and 1.3; replication inconclusive for falsification rule.

## CTCF positive gate (HCT116)

| Metric | Value |
|--------|-------|
| Fisher OR | 8.3519 |
| Woolf 95% CI | 7.8112 – 8.9299 |
| Gate threshold | ≥ 2.0 |
| Verdict | **PASS** |

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT a license to switch primary TE post-hoc.
3. NOT wet-lab / holdout / C1 authorization.
4. NOT multi-assay MAPQ on BAM (processed bedpe only).

