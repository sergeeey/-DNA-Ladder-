# Data manifest — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Status:** K562 primary + umap + GM12878 + HCT116 + caller-swap **done**; desk
**CLOSED** as `INCONCLUSIVE_CROSS_CELL`.  
**Probe JSON:** `data/t0_accession_probe.json`  
**Checksum JSON:** `data/download_checksums.json`  
**Assembly:** GRCh38  
**Operator:** cloud agent 2026-07-20 (T0→T6 closure)

## Rules

- Real public ENCODE / UCSC / Hoffman-lab files only
- Large binaries in `data/input/` (gitignored); commit manifests + checksums only
- T3 AluSz OR `FAIL_DESK_PRIMARY`; T4 umap≥0.3 OR 0.898; T5 GM12878 OR 1.252;
  T5b HCT116 OR 1.280; T6 DELTA caller-swap OR 0.913 — combined
  `INCONCLUSIVE_CROSS_CELL`; null_results **INCONCLUSIVE** filed

## Rejected placeholders

| Accession | Reason |
|-----------|--------|
| `ENCSR000BZZ` | **WRONG** — ESR1 ChIA-PET, not Pol II |
| `ENCSR444WCX` | **404** on ENCODE |
| HCT116 RAD21/CTCF ChIA-PET | **NOT** Pol II substitute |
| `ENCFF522WVV` / `ENCSR176BRX` | HiCCUPS but **auxin-treated** RAD21 degron |

## Frozen / downloaded files

| Role | Experiment | File | Format | Assembly | Portal md5 | On-disk md5 | Size (bytes) | Notes |
|------|------------|------|--------|----------|------------|-------------|--------------|-------|
| **Pol II ChIA-PET primary** | `ENCSR880DSH` | **`ENCFF511QFN`** | bedpe.gz | GRCh38 | `ec8482f0227730d178169776b209c10f` | `ec8482f0227730d178169776b209c10f` | 11964739 | preferred_default; **MATCH** |
| **Hi-C primary** | `ENCSR545YBD` | **`ENCFF693XIL`** | bedpe.gz | GRCh38 | `ae663464bdbe60998e422254ea0dac2c` | `ae663464bdbe60998e422254ea0dac2c` | 900362 | HiCCUPS merged_loops_30; **MATCH** |
| **CTCF peaks (positive gate)** | `ENCSR000AKO` | **`ENCFF769AUF`** | bed.gz | GRCh38 | `7d086cac19c5311a77b7e21e3d931435` | `7d086cac19c5311a77b7e21e3d931435` | 919491 | conservative IDR; preferred_default; **MATCH** |
| TE annotation (RMSK) | UCSC hg38 | `rmsk.txt.gz` | txt.gz | hg38/GRCh38 | — | `b2e108b535550ba9e3cf83c77417380f` | 155633856 | UCSC rmsk |
| **Umap k100 (T4)** | Hoffman lab | `k100.Umap.MultiTrackMappability.bw` | bigWig | hg38 | — | `59646493c85a8f991603d8af8701bdc4` | 864604710 | multi-read; MAPQ proxy |
| **Pol II GM12878 (T5)** | `ENCSR905HWW` | **`ENCFF913VWM`** | bedpe.gz | GRCh38 | `04d3b1fb8ef74777f8f70d19da489215` | `04d3b1fb8ef74777f8f70d19da489215` | 7372214 | preferred_default; **MATCH** |
| **Hi-C GM12878 (T5)** | `ENCSR410MDC` | **`ENCFF781ASD`** | bedpe.gz | GRCh38 | `9bd4e66734ffacabdffa3ccbe4f0d21c` | `9bd4e66734ffacabdffa3ccbe4f0d21c` | 986986 | HiCCUPS merged_loops_30; **MATCH** |
| **CTCF GM12878 (T5)** | `ENCSR000DZN` | **`ENCFF796WRU`** | bed.gz | GRCh38 | `3f36655eb9a421a542ff031fc7b5e9aa` | `3f36655eb9a421a542ff031fc7b5e9aa` | 711745 | conservative IDR; preferred_default; **MATCH** |
| **Pol II HCT116 (T5b)** | `ENCSR035PVZ` | **`ENCFF322FOT`** | bedpe.gz | GRCh38 | `fa2693618035e033ef7c975198493a9e` | `fa2693618035e033ef7c975198493a9e` | 1855045 | preferred_default; plain HCT116; **MATCH** |
| **Hi-C HCT116 (T5b)** | `ENCSR123UVP` | **`ENCFF060QTI`** | bedpe.gz | GRCh38 | `3cf083558b07ba7ab29cb6509610d522` | `3cf083558b07ba7ab29cb6509610d522` | 324914 | HiCCUPS merged_loops_30; untreated RAD21-AID; **MATCH** |
| **CTCF HCT116 (T5b)** | `ENCSR240PRQ` | **`ENCFF463FGL`** | bed.gz | GRCh38 | `d1ca230c75391179937ace2a17ed0043` | `d1ca230c75391179937ace2a17ed0043` | 987887 | conservative IDR; preferred_default; **MATCH** |
| Hi-C alternate (T6 DELTA) | `ENCSR545YBD` | `ENCFF657QKE` | bedpe.gz | GRCh38 | `0a3751e380c7b18e8565addaa23595ff` | `0a3751e380c7b18e8565addaa23595ff` | 208215 | DELTA v1.9; caller-swap; **MATCH** |
| Hi-C alternate (intact sens.) | `ENCSR479XDG` | `ENCFF256ZMD` | bedpe.gz | GRCh38 | `47a1aa77c97c340234a1da38a21b8c62` | `47a1aa77c97c340234a1da38a21b8c62` | 2869470 | localizer loops_30; **MATCH** |
| Pol II sensitivity | `ENCSR880DSH` | `ENCFF759YBZ` | bedpe | GRCh38 | `c4bcd92733e0861184966acbe346d11c` | _not downloaded_ | — | biorep 2 |
| Pol II sensitivity | `ENCSR880DSH` | `ENCFF030PMM` | bedpe | GRCh38 | `66ee96602bb7762314b7fd6f5e990621` | _not downloaded_ | — | biorep 3 |
| Hi-C alternate (legacy note) | `ENCSR479XDG` | `ENCFF598CLH` | bedpe | GRCh38 | `8795e2e90f554bff5e83db09ae3b1eea` | _not downloaded_ | — | intact localizer loops_1 |

### Download URLs

| File | URL |
|------|-----|
| ENCFF511QFN | https://www.encodeproject.org/files/ENCFF511QFN/@@download/ENCFF511QFN.bedpe.gz |
| ENCFF693XIL | https://www.encodeproject.org/files/ENCFF693XIL/@@download/ENCFF693XIL.bedpe.gz |
| ENCFF769AUF | https://www.encodeproject.org/files/ENCFF769AUF/@@download/ENCFF769AUF.bed.gz |
| ENCFF913VWM | https://www.encodeproject.org/files/ENCFF913VWM/@@download/ENCFF913VWM.bedpe.gz |
| ENCFF781ASD | https://www.encodeproject.org/files/ENCFF781ASD/@@download/ENCFF781ASD.bedpe.gz |
| ENCFF796WRU | https://www.encodeproject.org/files/ENCFF796WRU/@@download/ENCFF796WRU.bed.gz |
| ENCFF322FOT | https://www.encodeproject.org/files/ENCFF322FOT/@@download/ENCFF322FOT.bedpe.gz |
| ENCFF060QTI | https://www.encodeproject.org/files/ENCFF060QTI/@@download/ENCFF060QTI.bedpe.gz |
| ENCFF463FGL | https://www.encodeproject.org/files/ENCFF463FGL/@@download/ENCFF463FGL.bed.gz |
| rmsk.txt.gz | https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz |
| k100 Umap | https://hgdownload.soe.ucsc.edu/gbdb/hg38/hoffmanMappability/k100.Umap.MultiTrackMappability.bw |

### MAPQ note

Processed bedpe lack MAPQ → documented **MAPQ=N/A**; T4 / optional HCT116 umap use
mean Umap ≥ 0.3 as preregistered proxy.

### Replication freezes

- GM12878: `ACCESSION_FREEZE_replication_v1.md`
- HCT116: `ACCESSION_FREEZE_replication_HCT116_v1.md`

Primary TE remains **AluSz**.
