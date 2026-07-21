# Decision — exp_te_loop_caller_concordance (C-F1)

**Date:** 2026-07-21  
**Verdict:** **BLOCKED_DATA**  
**Stage:** T0 only — ΔJaccard **not computed**

## Gate

No released K562 GRCh38 **Mustache** processed loop bedpe on ENCODE.

| Probe | Result |
|-------|--------|
| K562 GRCh38 `output_type=loops` bedpe | **15** files (HiCCUPS / DELTA / localizer / ChIA) |
| Alias / title / software containing Mustache | **0** |
| ENCODE `type=Software` catalog Mustache | **0** |
| HiCCUPS target `ENCFF693XIL` | **present** (preferred_default; `call-hiccups` alias) |

Full JSON: `data/t0_accession_probe.json`.  
Consistent with C-A1 T6 note (Mustache N/A; DELTA used there — **not** substituted here).

## What this does NOT mean

1. NOT a scientific REJECT of Mustache↔HiCCUPS TE concordance (data never entered).
2. NOT license to treat DELTA (`ENCFF657QKE`) as Mustache for this claim.
3. NOT wet / holdout / C1 / pathogenicity license.
4. Does NOT reopen C-A1 INCONCLUSIVE_CROSS_CELL or C-H1 Gnocchi SUPPORT_WITH_CAVEATS.

## Next fruit

Recommend **C-G1** (RAD21 vs CTCF ChIA TE odds) **or** **C-D1** (TE age vs loop reproducibility) T0 — human pick. Holdout / C1 / wet untouched.
