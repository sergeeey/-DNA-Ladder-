# Data manifest — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Status:** Accessions **FROZEN** (`ACCESSION_FREEZE_v1.md`). Large binaries **not** downloaded yet.  
**Probe JSON:** `data/t0_accession_probe.json`  
**Assembly:** GRCh38

## Rules

- Real public ENCODE files only
- Record on-disk md5/sha256 **after** real download — portal md5 below is metadata only
- Do not commit `.hic` / large matrices (see track `DATA.md` / root `.gitignore`)
- Do not invent enrichment ORs

## Rejected placeholders

| Accession | Reason |
|-----------|--------|
| `ENCSR000BZZ` | **WRONG** — ESR1 ChIA-PET, not Pol II |
| `ENCSR444WCX` | **404** on ENCODE |

## Frozen primary accessions

| Role | Experiment | File | Format | Assembly | Portal md5 | On-disk md5 | Notes |
|------|------------|------|--------|----------|------------|-------------|-------|
| **Pol II ChIA-PET primary** | `ENCSR880DSH` | **`ENCFF511QFN`** | bedpe loops | GRCh38 | `ec8482f0227730d178169776b209c10f` | _pending download_ | preferred_default; biorep 1 |
| Pol II sensitivity | `ENCSR880DSH` | `ENCFF759YBZ` | bedpe loops | GRCh38 | `c4bcd92733e0861184966acbe346d11c` | _pending_ | biorep 2 |
| Pol II sensitivity | `ENCSR880DSH` | `ENCFF030PMM` | bedpe loops | GRCh38 | `66ee96602bb7762314b7fd6f5e990621` | _pending_ | biorep 3 |
| **Hi-C primary** | `ENCSR545YBD` | **`ENCFF693XIL`** | bedpe loops | GRCh38 | `ae663464bdbe60998e422254ea0dac2c` | _pending download_ | HiCCUPS merged_loops_30; preferred_default |
| Hi-C alternate | `ENCSR479XDG` | `ENCFF598CLH` | bedpe loops | GRCh38 | `8795e2e90f554bff5e83db09ae3b1eea` | _pending_ | intact localizer; sensitivity only |
| TE annotation (RMSK) | — | TBD | — | GRCh38 | — | _pending_ | |
| Mappability track | — | TBD | — | GRCh38 | — | _pending_ | |
| CTCF peaks (positive gate) | TBD | TBD | — | GRCh38 | — | _pending_ | |

### Primary choice rationale (short)

- **Pol II:** `ENCFF511QFN` — only preferred_default among the three `ENCSR880DSH` bedpe loop files.
- **Hi-C:** `ENCFF693XIL` — preferred_default processed HiCCUPS loops on in situ Hi-C; preferred over intact localizer `ENCFF598CLH`.

## Download log

| Date | File | URL | Checksum | Operator |
|------|------|-----|----------|----------|
| — | — | — | — | — |
