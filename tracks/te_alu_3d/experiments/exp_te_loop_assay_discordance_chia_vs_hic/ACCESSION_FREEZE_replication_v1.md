# ACCESSION_FREEZE replication v1 — C-A1 independent cell type

**Date:** 2026-07-20  
**Experiment:** `exp_te_loop_assay_discordance_chia_vs_hic`  
**Role:** Independent replication cell type for claim-level falsification  
**Assembly freeze:** **GRCh38**  
**Cell type:** **GM12878** (preferred over HCT116: preferred_default Pol II + HiCCUPS Hi-C pair)

---

## Rationale

K562 desk primary (T3) yielded AluSz OR ≈ 0.908 (`FAIL_DESK_PRIMARY`). Claim.md requires
an independent processed loop file / cell type before claim-level REJECT. GM12878 has
ENCODE-processed Pol II (POLR2A) ChIA-PET bedpe loops and in situ Hi-C HiCCUPS
`merged_loops_30` on GRCh38 — matching the K562 primary product class.

HCT116 also has Pol II ChIA-PET + Hi-C loop bedpe on GRCh38; not used as primary
replication freeze (kept as alternate if GM12878 pipeline fails).

---

## Frozen replication accessions

### Pol II (POLR2A) ChIA-PET — GM12878

| Field | Value |
|-------|-------|
| Experiment | `ENCSR905HWW` |
| **Primary bedpe** | **`ENCFF913VWM`** |
| File type | `bedpe` / output_type `loops` |
| Assembly | GRCh38 |
| Target | POLR2A |
| Replicate | biological_replicates `[2]` |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal = on-disk) | `04d3b1fb8ef74777f8f70d19da489215` |
| href | https://www.encodeproject.org/files/ENCFF913VWM/@@download/ENCFF913VWM.bedpe.gz |
| Submitted name | `LHG0045V.e500.clusters.cis.BE3` (Ruan/ENCODE ChIA-PET pipeline) |

**Alternate (same experiment, biorep 1, not preferred):** `ENCFF040KUS` (md5
`ee1769db8550afac18adb3715c2977bd`) — sensitivity only.

### Hi-C — GM12878

| Field | Value |
|-------|-------|
| Experiment | `ENCSR410MDC` (in situ Hi-C) |
| **Primary bedpe** | **`ENCFF781ASD`** |
| File type | `bedpe` / output_type `loops` |
| Assembly | GRCh38 |
| Caller path | ENCODE processing **HiCCUPS** `merged_loops_30.bedpe` |
| Replicates | bioreps `[1..9]` (merged call) |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal = on-disk) | `9bd4e66734ffacabdffa3ccbe4f0d21c` |
| href | https://www.encodeproject.org/files/ENCFF781ASD/@@download/ENCFF781ASD.bedpe.gz |

**Why this Hi-C:** Same product class as K562 primary `ENCFF693XIL` (HiCCUPS
merged_loops_30, preferred_default). Alternates on same experiment (not frozen):
`ENCFF583FAZ` (merged_loops_1), `ENCFF554XMH` (delta predicted loops).

### CTCF peaks (positive gate) — GM12878

| Field | Value |
|-------|-------|
| Experiment | `ENCSR000DZN` (CTCF TF ChIP-seq, GM12878) |
| **Peaks file** | **`ENCFF796WRU`** |
| Output type | conservative IDR thresholded peaks |
| Assembly | GRCh38 |
| ENCODE flag | **`preferred_default: true`** |
| md5sum (portal = on-disk) | `3f36655eb9a421a542ff031fc7b5e9aa` |
| href | https://www.encodeproject.org/files/ENCFF796WRU/@@download/ENCFF796WRU.bed.gz |

---

## Alternate cell type (not frozen primary replication)

| Role | Cell | Notes |
|------|------|-------|
| Pol II ChIA-PET | HCT116 | Multiple POLR2A bedpe (e.g. `ENCFF586MYT` / `ENCSR180DXE`) |
| Hi-C | HCT116 | e.g. `ENCFF522WVV` preferred on `ENCSR176BRX` |

Not downloaded for v1; GM12878 pair preferred.

---

## Explicit non-use

- No K562 biorep swap presented as independent cell-type replication
- No hg19 GIS ChIA-PET without liftOver as primary
- No `.hic` / FASTQ downloads
- Primary TE remains **AluSz** (no post-hoc switch on replication)

**Frozen IDs for replication claim language:** Pol II = `ENCFF913VWM`; Hi-C =
`ENCFF781ASD`; CTCF gate = `ENCFF796WRU`; cell = GM12878.
