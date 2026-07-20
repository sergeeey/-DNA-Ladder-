# Data manifest — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Status:** Primary bedpe + CTCF + RMSK **downloaded**; T3 primary OR computed.  
**Probe JSON:** `data/t0_accession_probe.json`  
**Checksum JSON:** `data/download_checksums.json`  
**Assembly:** GRCh38  
**Operator:** cloud agent 2026-07-20 (T0→T3)

## Rules

- Real public ENCODE / UCSC files only
- Large binaries in `data/input/` (gitignored); commit manifests + checksums only
- T3 primary AluSz OR finalized at desk (`FAIL_DESK_PRIMARY`); MAPQ/umap still pending

## Rejected placeholders

| Accession | Reason |
|-----------|--------|
| `ENCSR000BZZ` | **WRONG** — ESR1 ChIA-PET, not Pol II |
| `ENCSR444WCX` | **404** on ENCODE |

## Frozen / downloaded files

| Role | Experiment | File | Format | Assembly | Portal md5 | On-disk md5 | On-disk sha256 | Size (bytes) | Notes |
|------|------------|------|--------|----------|------------|-------------|----------------|--------------|-------|
| **Pol II ChIA-PET primary** | `ENCSR880DSH` | **`ENCFF511QFN`** | bedpe.gz | GRCh38 | `ec8482f0227730d178169776b209c10f` | `ec8482f0227730d178169776b209c10f` | `145af802bd55daa585f47be071f82d19a73e2b841e1becc20221827e34fe34a1` | 11964739 | preferred_default; **MATCH** |
| **Hi-C primary** | `ENCSR545YBD` | **`ENCFF693XIL`** | bedpe.gz | GRCh38 | `ae663464bdbe60998e422254ea0dac2c` | `ae663464bdbe60998e422254ea0dac2c` | `db7fd5f97064899130838b943379ac5d527bf94bb19b6a7073fcea57136e2f2a` | 900362 | HiCCUPS merged_loops_30; **MATCH** |
| **CTCF peaks (positive gate)** | `ENCSR000AKO` | **`ENCFF769AUF`** | bed.gz | GRCh38 | `7d086cac19c5311a77b7e21e3d931435` | `7d086cac19c5311a77b7e21e3d931435` | `d269cd9b06ec5d9986d331a5623283f396977cdf2e94c83ab9a409171470f28e` | 919491 | conservative IDR; preferred_default; **MATCH** |
| TE annotation (RMSK) | UCSC hg38 | `rmsk.txt.gz` | txt.gz | hg38/GRCh38 | — | `b2e108b535550ba9e3cf83c77417380f` | `db60e6aa7ac175f8f5465cd01b48b550e67e1fb0fd828608d8343481867bb276` | 155633856 | https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz |
| Pol II sensitivity | `ENCSR880DSH` | `ENCFF759YBZ` | bedpe | GRCh38 | `c4bcd92733e0861184966acbe346d11c` | _not downloaded_ | — | — | biorep 2 |
| Pol II sensitivity | `ENCSR880DSH` | `ENCFF030PMM` | bedpe | GRCh38 | `66ee96602bb7762314b7fd6f5e990621` | _not downloaded_ | — | — | biorep 3 |
| Hi-C alternate | `ENCSR479XDG` | `ENCFF598CLH` | bedpe | GRCh38 | `8795e2e90f554bff5e83db09ae3b1eea` | _not downloaded_ | — | — | intact localizer |
| Mappability (umap) | — | — | — | GRCh38 | — | _pending_ | — | — | optional for matched-null |
| ATAC K562 | — | — | — | GRCh38 | — | _pending_ | — | — | not required for T2 CTCF gate |

### Download URLs

| File | URL |
|------|-----|
| ENCFF511QFN | https://www.encodeproject.org/files/ENCFF511QFN/@@download/ENCFF511QFN.bedpe.gz |
| ENCFF693XIL | https://www.encodeproject.org/files/ENCFF693XIL/@@download/ENCFF693XIL.bedpe.gz |
| ENCFF769AUF | https://www.encodeproject.org/files/ENCFF769AUF/@@download/ENCFF769AUF.bed.gz |
| rmsk.txt.gz | https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz |

### CTCF freeze rationale

Among released GRCh38 K562 CTCF IDR peak beds, **`ENCFF769AUF`** (`ENCSR000AKO`, conservative IDR thresholded peaks) is portal **preferred_default**. Alternate optimal IDR on same experiment: `ENCFF519CXF` (not used).

## Download log

| Date | File | URL | md5 | Operator |
|------|------|-----|-----|----------|
| 2026-07-20 | ENCFF511QFN.bedpe.gz | ENCODE @@download | ec8482f0227730d178169776b209c10f | t1_download_primary_inputs.py |
| 2026-07-20 | ENCFF693XIL.bedpe.gz | ENCODE @@download | ae663464bdbe60998e422254ea0dac2c | t1_download_primary_inputs.py |
| 2026-07-20 | ENCFF769AUF.bed.gz | ENCODE @@download | 7d086cac19c5311a77b7e21e3d931435 | t1_download_primary_inputs.py |
| 2026-07-20 | rmsk.txt.gz | UCSC hg38 | b2e108b535550ba9e3cf83c77417380f | t1_download_primary_inputs.py |
