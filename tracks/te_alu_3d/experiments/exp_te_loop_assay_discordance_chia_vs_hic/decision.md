# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `PENDING_T0`

## Verdict

No primary analysis results yet. This file must not invent enrichment ORs, pass/fail
biology, or unverified accession biology.

## Current gate

| Gate | Status |
|------|--------|
| Deep Research promote | `VALIDATE_DESK` (C-A1) |
| Standard-tier preregistration | Written (`claim.md`, `controls.md`, `notes.md`) |
| T0 ENCODE accession probe | **DONE** (metadata JSON committed) — see below |
| Primary TE OR analysis | NOT STARTED |
| Holdout | SEALED (untouched) |
| Wet-lab / oligos | FORBIDDEN |

### T0 probe summary (accessions only — not enrichment results)

Source: `data/t0_accession_probe.json` (2026-07-20).

| Check | Result |
|-------|--------|
| `ENCSR000BZZ` | Exists but **ESR1** ChIA-PET — wrong target for C-A1 |
| `ENCSR444WCX` | **Not found** (404) |
| Pol II ChIA-PET processed bedpe | **yes** — `ENCSR880DSH` → `ENCFF759YBZ`, `ENCFF511QFN`, `ENCFF030PMM` (GRCh38) |
| Hi-C K562 processed bedpe loops | **yes** — e.g. `ENCFF693XIL` (`ENCSR545YBD`), `ENCFF598CLH` / `ENCFF256ZMD` (`ENCSR479XDG`) |

Overall usable processed bedpe for C-A1 desk path: **yes** (both assays). Download + md5 still pending (`data_manifest.md`).

## Stop / branch rules (from report §16)

- If Pol II ChIA-PET K562 processed bedpe/loops unavailable (FASTQ-only) → `BLOCKED_DATA`;
  demote C-A1; consider C-B1 or C-K1.
- If MAPQ≥30 + replication yield OR < 1.1 for all pre-registered subfamilies → `REJECT`
  (file `null_results/`).
- If CTCF positive gate fails pipeline sanity → debug / `INCONCLUSIVE`, do not claim TE biology.

## What a future result will still NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  

## Next edit to this file

After T0 JSON review: record verified ENCFF/ENCSR IDs and either proceed to download
manifest or set `BLOCKED_DATA`.
