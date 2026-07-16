# P8 — Power simulation for reporter & Capture-C

**Status:** PRE-REGISTERED (before results)  
**Date locked:** 2026-07-16  
**L0:** Predictive desk — can the pre-registered MCID be distinguished under realistic noise?  
**Not wet-lab. Not holdout. Does not authorize oligo order.**

## MCIDs (frozen)

| Assay | MCID |
|-------|------|
| Reporter | \|log2(ALT/REF)\| ≥ **0.5** in ≥ **2** independent transfections |
| Capture-C / contact | \|ΔContact\| ≥ **25%** of WT **or** \|ΔOE\| ≥ **0.5** |

## Simulation design (locked)

### Reporter
- Model: independent tx draws `log2(ALT/REF) ~ N(μ, σ²)`
- True effects μ ∈ {0.0, 0.35, **0.50**, 0.75, 1.0}
- Noise σ ∈ {**low 0.25**, **mid 0.40**, **high 0.60**} (log2 units)
- Replicates n_tx ∈ {2, 3, 4, 6, 8}
- Success rule (matches MCID wording): **≥2** txs each with \|x_i\| ≥ 0.5 **and** same sign as mean
- Also report one-sample t-test power vs 0 at α=0.05 (secondary, not MCID)

### Capture-C
- Observed ΔContact_frac = ε_edit × Δ_true + noise, noise ~ N(0, σ_c²)
- Edit efficiency ε ∈ {0.3, 0.5, 0.7, 0.9} (ALT allele / clone purity proxy)
- True \|Δ\|/WT ∈ {0.15, **0.25**, 0.40, 0.60}
- σ_c ∈ {**low 0.08**, **mid 0.15**, **high 0.25**} (fraction of WT units)
- Batches n_batch ∈ {2, 3, 4, 6}
- Success: mean \|Δ̂\| ≥ 0.25 across batches **or** mean \|ΔOE\|≥0.5 (OE path: scale Δ by 2× as desk proxy when OE not measured)

## Kill / caution labels

| ID | Rule |
|----|------|
| **P8_UNDERPOWERED** | At mid noise, power to detect MCID-true effect &lt; **0.5** even at n=6 |
| **P8_MARGINAL** | Mid-noise power ∈ [0.5, 0.8) at recommended n |
| **P8_ADEQUATE** | Mid-noise power ≥ **0.8** at some n ≤ 6 |

Separate labels for reporter vs Capture-C.

## Seed

`20260716` — fixed for reproducibility.

## Script / arts

`pilot_scaffold/scripts/run_p8_power_simulation.py`  
Out: `P8_power_simulation_v1.md` / `.json`
