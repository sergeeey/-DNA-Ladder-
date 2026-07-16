# P8 — Power simulation v1

**Date:** 2026-07-16
**Status:** `P8_POWER_COMPLETE`
**Claim:** `P8_POWER_CLAIM_v1.md`
**Seed / sims:** 20260716 / 5000

## Labels

| Assay | Label | Mid-noise power @ n=6 (MCID-true) |
|-------|-------|----------------------------------:|
| Reporter (μ=0.5) | **P8_ADEQUATE** | 0.894 |
| Capture-C (Δ=0.25, ε=0.7) | **P8_UNDERPOWERED** | 0.111 |

- Reporter recommended n_tx (mid, power≥0.8): **6**
- Capture recommended n_batch (mid, ε=0.7, power≥0.8): **None**
- Reporter false-positive under MCID rule (μ=0, mid, n=6): **0.220**

## Reporter — power for μ=0.5 (MCID boundary)

| n_tx | low σ=0.25 | mid σ=0.40 | high σ=0.60 |
|-----:|-----------:|-----------:|------------:|
| 2 | 0.257 | 0.255 | 0.245 |
| 3 | 0.493 | 0.492 | 0.498 |
| 4 | 0.676 | 0.690 | 0.678 |
| 6 | 0.887 | 0.894 | 0.888 |
| 8 | 0.966 | 0.966 | 0.955 |

## Capture-C — power for Δ=0.25 WT (MCID boundary), mid noise

| n_batch | ε=0.3 | ε=0.5 | ε=0.7 | ε=0.9 |
|--------:|------:|------:|------:|------:|
| 2 | 0.047 | 0.122 | 0.241 | 0.408 |
| 3 | 0.023 | 0.073 | 0.192 | 0.392 |
| 4 | 0.010 | 0.047 | 0.155 | 0.360 |
| 6 | 0.002 | 0.024 | 0.111 | 0.344 |

## Plain language

Считаем, хватит ли 2–6 реплик, чтобы поймать ваш MCID, если шум низкий / средний / высокий, и если edit не 100% чистый. Это не обещание лаборатории — проверка, не фантазия ли план.

## What this does NOT mean

- Not calibrated to real HUDEP-2 variance (priors are desk assumptions)
- Not wet GO / not oligo order
- Capture OE path is a desk proxy (2×\|Δ\|), not measured OE

Full grid: `P8_power_simulation_v1.json`
