# Decision — exp_rad21_vs_ctcf_chia_te_odds (C-G1)

**Date:** 2026-07-21  
**Verdict:** **BLOCKED_DATA**  
**Stage:** T0 only — OR **not computed**

## Gate

| Probe | Result |
|-------|--------|
| CTCF ChIA-PET `ENCSR597AKG` | GRCh38 loops **yes** — preferred `ENCFF118PBQ` (+ `ENCFF607PZX`) |
| RAD21 `ENCSR338WUS` | **fastq only** (30 reads files; no processed loops) |
| RAD21 `ENCSR000FDB` | loops/peaks **hg19 archived** (TSV/bed); no GRCh38 bedpe |

Full JSON: `data/t0_accession_probe.json`.

## What this does NOT mean

1. NOT a scientific REJECT of RAD21 vs CTCF TE-anchor odds.
2. NOT license to lift hg19 archived RAD21 loops without a new claim freeze.
3. NOT wet / holdout / C1 license.

## Next fruit

Recommend **C-D1** (TE age vs loop reproducibility) T0, or human reopen if RAD21 GRCh38
processed loops appear. Holdout / C1 / wet untouched.
