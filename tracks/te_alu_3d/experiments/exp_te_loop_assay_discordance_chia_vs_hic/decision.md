# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `PENDING_T0`

## Verdict

No primary analysis results yet. This file must not invent enrichment ORs or pass/fail biology.

**T0 accession probe:** **PASS** (processed bedpe available for both Pol II ChIA-PET and Hi-C).  
Primary ENCFF IDs frozen in `ACCESSION_FREEZE_v1.md`. Local bedpe download + on-disk checksums
still outstanding — hence status remains `PENDING_T0` (download/manifest completion), not
analysis PASS/REJECT.

## Current gate

| Gate | Status |
|------|--------|
| Deep Research promote | `VALIDATE_DESK` (C-A1; score 7.06; C-B1 was 7.47 but not selected) |
| Standard-tier preregistration | Written (`claim.md`, `controls.md`, `notes.md`) |
| T0 ENCODE accession probe | **PASS** — processed bedpe yes/yes |
| Accession freeze | **DONE** — Pol II `ENCFF511QFN`; Hi-C `ENCFF693XIL` |
| Primary bedpe on-disk download | PENDING (no multi-GB / no OR yet) |
| Primary TE OR analysis | NOT STARTED |
| Holdout | SEALED (untouched) |
| Wet-lab / oligos | FORBIDDEN |

### T0 probe + freeze summary

Source: `data/t0_accession_probe.json` + `ACCESSION_FREEZE_v1.md`.

| Check | Result |
|-------|--------|
| `ENCSR000BZZ` | **WRONG** — ESR1 ChIA-PET (not Pol II) |
| `ENCSR444WCX` | **404** |
| Pol II processed bedpe | **yes** → primary **`ENCFF511QFN`** (`ENCSR880DSH`; preferred_default) |
| Hi-C processed bedpe | **yes** → primary **`ENCFF693XIL`** (`ENCSR545YBD`; HiCCUPS preferred_default) |

## Stop / branch rules (from report §16)

- If Pol II ChIA-PET K562 processed bedpe/loops unavailable (FASTQ-only) → `BLOCKED_DATA`;
  demote C-A1; consider C-B1 or C-K1. *(T0: not triggered — bedpe available.)*
- If MAPQ≥30 + replication yield OR < 1.1 for all pre-registered subfamilies → `REJECT`
  (file `null_results/`).
- If CTCF positive gate fails pipeline sanity → debug / `INCONCLUSIVE`, do not claim TE biology.

## What a future result will still NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  

## Next edit to this file

After primary bedpe download + on-disk md5 in `data_manifest.md`: advance T0 download gate;
still no ORs until analysis is run under frozen claim.
