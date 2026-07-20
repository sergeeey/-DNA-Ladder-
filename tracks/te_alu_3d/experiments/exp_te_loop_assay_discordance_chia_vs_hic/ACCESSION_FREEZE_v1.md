# ACCESSION_FREEZE v1 — C-A1 loop discordance desk experiment

**Date:** 2026-07-20  
**Experiment:** `exp_te_loop_assay_discordance_chia_vs_hic`  
**Source probe:** `data/t0_accession_probe.json`  
**Scope:** Metadata freeze only — **no** multi-GB downloads in this step  
**Assembly freeze:** **GRCh38**

---

## Rejected placeholders (do not use)

| Accession | Finding | Action |
|-----------|---------|--------|
| `ENCSR000BZZ` | Released ChIA-PET, target **ESR1** (not Pol II / POLR2A) | **WRONG target** — excluded |
| `ENCSR444WCX` | ENCODE **404** | Discarded |

---

## Primary frozen accessions

### Pol II (RNAPII) ChIA-PET — K562

| Field | Value |
|-------|-------|
| Experiment | `ENCSR880DSH` |
| **Primary bedpe** | **`ENCFF511QFN`** |
| File type | `bedpe` / output_type `loops` |
| Assembly | GRCh38 |
| Replicate | biological_replicates `[1]` |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal) | `ec8482f0227730d178169776b209c10f` |
| href | https://www.encodeproject.org/files/ENCFF511QFN/@@download/ENCFF511QFN.bedpe.gz |

**Why this primary:** Among `ENCFF511QFN` / `ENCFF759YBZ` / `ENCFF030PMM` (all released GRCh38 `bedpe` loops from `ENCSR880DSH`), `ENCFF511QFN` is the portal **preferred_default**, biorep 1, and the largest processed loop call set from the Ruan/ENCODE ChIA-PET pipeline (`*.e500.clusters.cis.BE3` → bedpe).

**Replication / sensitivity (not primary):**

| File | Biorep | Role |
|------|--------|------|
| `ENCFF759YBZ` | 2 | MAPQ / replication sensitivity |
| `ENCFF030PMM` | 3 | MAPQ / replication sensitivity |

### Hi-C — K562

| Field | Value |
|-------|-------|
| Experiment | `ENCSR545YBD` (in situ Hi-C) |
| **Primary bedpe** | **`ENCFF693XIL`** |
| File type | `bedpe` / output_type `loops` |
| Assembly | GRCh38 |
| Caller path | ENCODE processing **HiCCUPS** `merged_loops_30.bedpe` |
| Replicates | bioreps `[1,2,3,4]` (merged call) |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal) | `ae663464bdbe60998e422254ea0dac2c` |
| href | https://www.encodeproject.org/files/ENCFF693XIL/@@download/ENCFF693XIL.bedpe.gz |

**Why this primary (vs intact `ENCFF598CLH`):** Prefer ENCODE **processed loop calls** from the in situ Hi-C experiment already used as the track’s K562 loop proxy (`ENCFF693XIL`). Portal marks it preferred_default; HiCCUPS merged_loops_30 is the standard ENCODE4 processed loop product (Mustache/HiCCUPS-class processed loops — not raw contacts). Intact Hi-C localizer calls (`ENCFF598CLH` on `ENCSR479XDG`) remain **alternate** for sensitivity, not primary.

**Alternate (sensitivity only):**

| File | Experiment | Notes |
|------|------------|-------|
| `ENCFF598CLH` | `ENCSR479XDG` intact Hi-C | localizer `localized_loops_1.bedpe` |
| `ENCFF256ZMD` | `ENCSR479XDG` | localizer `localized_loops_30.bedpe` |

---

## T0 probe status

- Usable processed bedpe Pol II: **yes**
- Usable processed bedpe Hi-C: **yes**
- Large `.hic` / FASTQ: **not downloaded** (forbidden this step)

## Still pending (not freeze)

- Local download + on-disk md5 verification → `data_manifest.md`
- RMSK + mappability + CTCF peak accessions for controls
- Any enrichment OR (must not be invented)

**Frozen IDs for claim language:** primary Pol II = `ENCFF511QFN`; primary Hi-C = `ENCFF693XIL`.
