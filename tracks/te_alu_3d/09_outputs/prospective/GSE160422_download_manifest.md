# GSE160422 download manifest (HUDEP-2 Hi-C / Capture Hi-C)

**SuperSeries:** GSE160425  
**Series:** GSE160422  
**Biosource:** HUDEP-2  
**Genome build (processed .hic):** hg19 / GRCh37  
**Local root:** `D:\DNK - 2\data\HUDEP2_GSE160422\`  
**Download started:** 2026-07-14  

## Priority queue

| Priority | Sample | File | Role | Size (approx) | Status |
|----------|--------|------|------|---------------|--------|
| 1 | GSM4873113 | GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic | G4_WT_CONTACT | 6.624 GB (7112676977 B) | **COMPLETE** SHA256 `A76017922096842BE6463FEB1D349BE5689EF96267BA51DD14777E94F2585226` |
| 2 | GSM4873114 | GSM4873114_B6-HUDEP2-HiC_allValidPairs.hic | P1_CTCF_DEL | ~6.6 GB | QUEUED |
| 3 | GSM4873115 | GSM4873115_A2-HUDEP2-HiC_allValidPairs.hic | P1_CTCF_INV | ~6.4 GB | QUEUED |
| later | GSM4873116 | …captureHiC… WT | P1_beta_globin_Capture | ~2.1–2.3 GB | OPTIONAL |
| later | GSM4873117 | …captureHiC… B6 del | P1_beta_globin_Capture | ~2.1–2.3 GB | OPTIONAL |
| later | GSM4873118 | …captureHiC… A2 inv | P1_beta_globin_Capture | ~2.1–2.3 GB | OPTIONAL |

## FTP URLs

```text
https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM4873nnn/GSM4873113/suppl/GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic
https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM4873nnn/GSM4873114/suppl/GSM4873114_B6-HUDEP2-HiC_allValidPairs.hic
https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM4873nnn/GSM4873115/suppl/GSM4873115_A2-HUDEP2-HiC_allValidPairs.hic
```

## Resume command (PowerShell)

```powershell
Set-Location "D:\DNK - 2\data\HUDEP2_GSE160422"
curl.exe -L -C - --retry 20 --retry-delay 10 `
  -o "GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic" `
  "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM4873nnn/GSM4873113/suppl/GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic"
```

After complete:

```powershell
Get-FileHash *.hic -Algorithm SHA256 | Export-Csv "checksums_sha256.csv" -NoTypeInformation
```

## Per-file YAML (fill sha256 after download)

```yaml
dataset: GSE160422
sample: GSM4873113
biosource: HUDEP-2
condition: WT
assay: Hi-C
genome_build: hg19
file: GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic
source_role: G4_WT_CONTACT
download_date: 2026-07-14
sha256: A76017922096842BE6463FEB1D349BE5689EF96267BA51DD14777E94F2585226
bytes: 7112676977
lifted_locus_note: see c1_ep_liftover_hg19.yaml
g4a_status: NOT_ESTABLISHED
```

Local copies: `D:\DNK - 2\data\HUDEP2_GSE160422\checksums_sha256.csv`, `GSM4873113_manifest.yaml`.

## Capture Hi-C caveat

β-globin bait — do **not** treat as C1 coverage without bait-coordinate audit.

## References

- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE160422  
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4873113  
- eLife 70557 / SuperSeries GSE160425  
