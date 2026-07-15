# P5 R1 — AG context-length sign stability

**Date:** 2026-07-15
**Status:** `P5_R1_COMPLETE`
**Claim:** `P5_R1_CLAIM_v1.md`
**C1 verdict:** **`R1_PASS`**
**Branch B:** AG context-length proxy does not kill Branch B primary

## Proxy

Reporter windows 301/1kb/2kb are **not** AG-native.
Used `16kb / 100kb / 500kb` `predict_variant` lengths instead.

## Results (signed mean CHIP_TF)

| Allele | 16kb | 100kb | 500kb | flips | Verdict |
|--------|-----:|------:|------:|------:|---------|
| C1 | -2.9075 | -0.3471 | -0.0730 | 0 | **R1_PASS** |
| C2 | -0.9823 | -0.1289 | -0.0226 | 0 | **STABLE_NOTED** |
| C3 | -0.2881 | -0.1373 | -0.0409 | 0 | **STABLE_NOTED** |
| N3 | +0.0299 | +0.0090 | -0.0029 | 1 | **N3_OK_OR_MILD** |

## Plain language

Проверяем, меняет ли AlphaGenome **знак** эффекта ALT vs REF, когда контекст узкий / средний / широкий. Если знак прыгает на обеих ступеньках у C1 — reporter Branch B нельзя считать устойчивым к длине даже на desk-прокси.

## What this does NOT mean

- Not wet transfection of 301 bp constructs
- Not holdout / Stage-3 change / oligo GO
- MAE magnitude alone cannot pass R1 — sign ladder is primary
