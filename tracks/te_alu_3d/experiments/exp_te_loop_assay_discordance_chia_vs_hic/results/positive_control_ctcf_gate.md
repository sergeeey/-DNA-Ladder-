# Positive control — CTCF gate (T2)

**Computed:** `2026-07-20T06:55:00.114820+00:00`  
**Verdict:** `PASS`  
**Decision status:** `PENDING_PRIMARY`  

## Inputs

- Hi-C loops: `ENCFF693XIL` (data/input/ENCFF693XIL.bedpe.gz)
- CTCF peaks: `ENCFF769AUF` / `ENCSR000AKO`
- Assembly: GRCh38

## Counts

| Metric | Value |
|--------|-------|
| Unique Hi-C anchors (chr1–22,X) | 24049 |
| CTCF peaks | 51759 |
| Anchors overlapping CTCF (obs) | 12607 (0.5242) |
| Mean null overlaps (chr-preserving shuffle, n=50) | 4258.54 (0.1771) |

## Statistics

| Statistic | Value |
|-----------|-------|
| Fisher OR (gate) | 5.1192 |
| Fisher p (two-sided) | ≈0 (float underflow; highly significant) |
| Woolf OR (95% CI) | 5.1192 (4.9103–5.3371) |
| Empirical rate ratio | 2.9604 |
| Gate threshold | OR ≥ 2.0 |

**Gate note:** PASS means pipeline recovers CTCF enrichment at Hi-C anchors; does NOT authorize primary TE OR claims.

## What this does NOT mean

1. NOT a primary TE enrichment result (none computed).
2. NOT causal CTCF → loop proof.
3. NOT authorization to unseal holdout, edit C1 E/P, or order oligos.

