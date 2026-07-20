# ACCESSION_FREEZE replication HCT116 v1 — C-A1 second independent cell type

**Date:** 2026-07-20  
**Experiment:** `exp_te_loop_assay_discordance_chia_vs_hic`  
**Role:** Second independent replication cell type (after GM12878)  
**Assembly freeze:** **GRCh38**  
**Cell type:** **HCT116**  
**Primary TE:** **AluSz** (unchanged; no post-hoc switch)

---

## Rationale

K562 desk primary failed (AluSz OR ≈ 0.91); GM12878 replication landed mid-zone
(OR ≈ 1.25). Claim.md falsification needs an independent processed loop file / cell
type. HCT116 has ENCODE-processed **POLR2A ChIA-PET** bedpe loops on plain HCT116
plus in situ Hi-C **HiCCUPS** `merged_loops_30` on GRCh38 — same product class as
K562 (`ENCFF511QFN` / `ENCFF693XIL`) and GM12878 (`ENCFF913VWM` / `ENCFF781ASD`).

RAD21/CTCF ChIA-PET is **not** an acceptable Pol II substitute (documented below).

---

## Frozen replication accessions (HCT116)

### Pol II (POLR2A) ChIA-PET — HCT116

| Field | Value |
|-------|-------|
| Experiment | `ENCSR035PVZ` |
| **Primary bedpe** | **`ENCFF322FOT`** |
| File type | `bedpe` / output_type `loops` |
| Assembly | GRCh38 |
| Target | POLR2A |
| Biosample | Homo sapiens HCT116 (no treatment / no genetic modification listed) |
| Replicate | biological_replicates `[2]` |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal) | `fa2693618035e033ef7c975198493a9e` |
| href | https://www.encodeproject.org/files/ENCFF322FOT/@@download/ENCFF322FOT.bedpe.gz |
| Submitted name | `LHH0128V.e500.clusters.cis.BE3` (Ruan/ENCODE ChIA-PET pipeline) |

**Alternate (same experiment, biorep 1, not preferred):** `ENCFF246ZKR` (md5
`0b76632d693f8fc93073e1142fb922ad`) — sensitivity only.

**Rejected as primary Pol II:** degron/auxin POLR2A ChIA-PET series (e.g.
`ENCSR180DXE` / `ENCFF586MYT` SMARCA5-AID + 5-Ph-IAA) — not plain HCT116.

### Hi-C — HCT116

| Field | Value |
|-------|-------|
| Experiment | `ENCSR123UVP` (in situ Hi-C) |
| **Primary bedpe** | **`ENCFF060QTI`** |
| File type | `bedpe` / output_type `loops` |
| Assembly | GRCh38 |
| Caller path | ENCODE processing **HiCCUPS** `merged_loops_30.bedpe` |
| Replicates | bioreps `[1..4]` (merged call) |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal) | `3cf083558b07ba7ab29cb6509610d522` |
| href | https://www.encodeproject.org/files/ENCFF060QTI/@@download/ENCFF060QTI.bedpe.gz |
| Biosample note | HCT116 RAD21-AID genotype **without** auxin treatment (untreated control arm) |

**Why this Hi-C:** Same product class as K562/GM12878 primary (HiCCUPS
`merged_loops_30`, preferred_default). No plain-HCT116 **in situ** HiCCUPS bedpe
exists on the portal; untreated RAD21-AID is the closest HiCCUPS match.

**Alternate (not frozen primary):** `ENCSR477GZK` / `ENCFF308MMM` — plain HCT116
**intact** Hi-C localizer loops (preferred_default). Different caller than
K562/GM12878 HiCCUPS; reserved for sensitivity if needed.

**Rejected:** `ENCSR176BRX` / `ENCFF522WVV` — HiCCUPS preferred_default but
**auxin-treated** RAD21 degron (not replication-comparable to untreated K562/GM12878).

### CTCF peaks (positive gate) — HCT116

| Field | Value |
|-------|-------|
| Experiment | `ENCSR240PRQ` (CTCF TF ChIP-seq, HCT116) |
| **Peaks file** | **`ENCFF463FGL`** |
| Output type | conservative IDR thresholded peaks |
| Assembly | GRCh38 |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal) | `d1ca230c75391179937ace2a17ed0043` |
| href | https://www.encodeproject.org/files/ENCFF463FGL/@@download/ENCFF463FGL.bed.gz |

---

## Explicit non-use / BLOCKED substitutes

| Candidate class | Verdict |
|-----------------|---------|
| RAD21 ChIA-PET (`ENCSR028AOM`, `ENCSR309KYA`, …) | **NOT acceptable** Pol II substitute |
| CTCF ChIA-PET (many HCT116 AID series) | **NOT acceptable** Pol II substitute |
| Invented / guessed accessions | Forbidden |
| hg19 without liftOver as primary | Forbidden |
| `.hic` / FASTQ bulk | Forbidden |
| Post-hoc primary TE switch | Forbidden |

**Pol II availability:** Processed POLR2A ChIA-PET bedpe **is available**
(`ENCFF322FOT`). Status is **not** `BLOCKED_DATA_HCT116`.

---

## Relation to GM12878 freeze

See `ACCESSION_FREEZE_replication_v1.md` (GM12878 primary replication). This document
extends the replication freeze set; it does **not** replace GM12878.

**Frozen IDs for HCT116 claim language:** Pol II = `ENCFF322FOT`; Hi-C =
`ENCFF060QTI`; CTCF gate = `ENCFF463FGL`; cell = HCT116.
