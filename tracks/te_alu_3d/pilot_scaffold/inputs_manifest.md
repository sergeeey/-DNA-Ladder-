# Inputs Manifest — Chr11 slices only (no bulk gnomAD)

**Rule:** скачивать только `chr11` (или `11`) регионы. Полный gnomAD VCF **запрещён**.

## Required files

| ID | File | Chr11 slice command | Used by |
|----|------|---------------------|---------|
| I01 | `data/clinvar_chr11.vcf.gz` | NCBI ClinVar VCF + tabix region | test set |
| I02 | `data/gnomad_chr11.vcf.gz` | gnomAD v4.1 chr11 only via HTTPS range/tabix | control pool + dual-track |
| I03 | `data/repeatmasker_chr11.bed` | UCSC RM track or Dfam intersect chr11 | TE annotation |
| I04 | `data/encode_blacklist_hg38.bed` | chr11 subset | gate 1 |
| I05 | `data/wgEncodeCrgMapabilityAlign100mer.bigWig` | chr11 fetch OK (full file ~small per chr) | gate 2 |
| I06 | `data/genomicSuperDups_chr11.bed` | UCSC segdup chr11 | gate 3 |
| I07 | `data/ctcf_GM12878_peaks.bed` | ENCODE GM12878 CTCF narrowPeak chr11 | matching + scoring |
| I08 | `data/gencode_v46_protein_coding_TSS_chr11.bed` | GENCODE TSS chr11 | distance-to-TSS |
| I09 | `data/gnomad_af_discordance_chr11.tsv` | optional precomputed exome vs genome p-values | gate 4 |

## Fetch recipes (examples)

### ClinVar chr11

```bash
# Full ClinVar VCF is small enough; still filter to chr11 at index time
curl -L -o data/clinvar.vcf.gz \
  https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
tabix -p vcf data/clinvar.vcf.gz
bcftools view -r chr11 -Oz -o data/clinvar_chr11.vcf.gz data/clinvar.vcf.gz
tabix -p vcf data/clinvar_chr11.vcf.gz
```

### gnomAD chr11 only (NOT bulk)

```bash
# Option A: gnomAD v4.1 sites VCF — chromosome 11 slice via tabix URL (if supported)
# Replace URL with current gnomAD release path from https://gnomad.broadinstitute.org/downloads
GNOMAD_chr11_URL="<release>/sites/chr11/gnomad.genomes.v4.1.sites.chr11.vcf.bgz"
curl -L -o data/gnomad_chr11.vcf.bgz "$GNOMAD_chr11_URL"
tabix -p vcf data/gnomad_chr11.vcf.bgz
bgzip -c data/gnomad_chr11.vcf.bgz > data/gnomad_chr11.vcf.gz  # if needed
tabix -p vcf data/gnomad_chr11.vcf.gz

# Option B: bcftools remote tabix (no full download)
# bcftools view -r chr11 -Oz -o data/gnomad_chr11.vcf.gz "$GNOMAD_chr11_URL"
```

### RepeatMasker chr11

```bash
# UCSC table export or BED from RepeatMasker/Dfam for hg38, then:
grep -E '^chr11\b' repeatMasker.hg38.bed > data/repeatmasker_chr11.bed
# Filter TE families: Alu + SVA (see config.yaml)
awk '$6 ~ /Alu|SVA/ || $4 ~ /Alu|SVA/' data/repeatmasker_chr11.bed > data/repeatmasker_chr11_alu_sva.bed
```

### ENCODE blacklist

```bash
curl -L -o data/encode_blacklist_hg38.bed \
  https://github.com/Boyle-Lab/Blacklist/raw/master/lists/hg38-blacklist.v2.bed.gz
# gunzip; grep chr11
```

### Mappability (Umap 36mer or 100mer — pick one, document in run)

```bash
# UCSC bigWig — can fetch full file once (~2GB) OR use pyBigWig remote
curl -L -o data/wgEncodeCrgMapabilityAlign100mer.bigWig \
  https://hgdownload.soe.ucsc.edu/gbdb/hg38/hg38/wgEncodeCrgMapabilityAlign100mer.bw
```

### CTCF GM12878

```bash
# ENCODE portal → GM12878 CTCF narrowPeak → export chr11
# Place at data/ctcf_GM12878_peaks.bed
```

### GENCODE TSS chr11

```bash
# GENCODE v46 protein_coding annotations → TSS BED chr11
# columns: chr start end name strand
```

## gnomAD discordance (gate 4)

If precomputed table unavailable, compute for chr11 variants:

```text
contingency test (exome AC/AN vs genome AC/AN) per variant
flag if p < 1e-4 (gnomAD v4.1.1 guidance)
```

Store: `variant_id, p_exome_genome_discordance, flagged`

## Validation before run

```bash
python -c "
from pathlib import Path
required = [
  'data/clinvar_chr11.vcf.gz',
  'data/gnomad_chr11.vcf.gz',
  'data/repeatmasker_chr11.bed',
  'data/encode_blacklist_hg38.bed',
  'data/ctcf_GM12878_peaks.bed',
  'data/gencode_v46_protein_coding_TSS_chr11.bed',
]
missing = [f for f in required if not Path(f).exists()]
print('MISSING:', missing if missing else 'none — ready for pilot')
"
```

## Dry-run without downloads

```bash
python qc_filters.py --dry-run
python build_matched_controls.py --dry-run
python permutation_test.py --dry-run
```

Uses synthetic chr11 variants in `data/dry_run/` (auto-created).
