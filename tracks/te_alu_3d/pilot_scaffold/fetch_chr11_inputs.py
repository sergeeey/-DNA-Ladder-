"""Fetch chr11-only inputs. Never downloads full gnomAD genome.

Usage:
  python fetch_chr11_inputs.py [--skip-clinvar] [--hbb-window]
"""

from __future__ import annotations

import gzip
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

# Small / medium public assets only
BLACKLIST_URL = (
    "https://raw.githubusercontent.com/Boyle-Lab/Blacklist/master/lists/"
    "hg38-blacklist.v2.bed.gz"
)
CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"

# UCSC table browser dumps via hgdownload (chrom-specific MySQL dumps not always available;
# use full rmssk then slice — rmsk for hg38 is large; prefer chromosome BED from annotation hub)
# Fallback: download chr11 fasta annotation via genome.ucsc.edu goldenPath
RM_CHR11_URL = (
    "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz"
)

# HBB locus window (hg38) for optional gnomAD slice documentation
HBB_WINDOW = ("chr11", 5_200_000, 5_300_000)


def _download(url: str, dest: Path, timeout: int = 120) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"GET {url}\n -> {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "DNK-pilot-scaffold/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        shutil.copyfileobj(resp, out)


def fetch_blacklist() -> Path:
    gz = DATA / "encode_blacklist_hg38.bed.gz"
    bed = DATA / "encode_blacklist_hg38.bed"
    if not bed.exists():
        _download(BLACKLIST_URL, gz)
        with gzip.open(gz, "rt", encoding="utf-8") as fin, bed.open("w", encoding="utf-8") as fout:
            for line in fin:
                fout.write(line)
    return bed


def fetch_clinvar_chr11(skip: bool = False) -> Path | None:
    out = DATA / "clinvar_chr11.vcf.gz"
    if out.exists():
        print(f"exists: {out}")
        return out
    if skip:
        print("skip clinvar fetch")
        return None
    full = DATA / "clinvar.vcf.gz"
    _download(CLINVAR_URL, full, timeout=600)
    # stream filter to chr11
    from vcf_loader import slice_vcf_to_chr

    n = slice_vcf_to_chr(full, out, chrom="chr11")
    print(f"clinvar chr11 records: {n}")
    return out


def build_alu_sva_from_rmsk(max_lines: int | None = None) -> Path | None:
    """Download UCSC rmsk and extract chr11 Alu/SVA BED (streaming)."""
    out = DATA / "repeatmasker_chr11_alu_sva.bed"
    if out.exists():
        print(f"exists: {out}")
        return out
    gz = DATA / "rmsk.txt.gz"
    if not gz.exists():
        print("Fetching UCSC rmsk.txt.gz (large; streaming Alu/SVA chr11 only)...")
        try:
            _download(RM_CHR11_URL, gz, timeout=900)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: rmsk fetch failed: {exc}")
            return None

    # rmsk format (ucsc): bin, swScore, milliDiv, milliDel, milliIns, genoName, genoStart, genoEnd,
    # genoLeft, strand, repName, repClass, repFamily, ...
    n = 0
    with gzip.open(gz, "rt", encoding="utf-8", errors="replace") as fin, out.open(
        "w", encoding="utf-8"
    ) as fout:
        for i, line in enumerate(fin):
            if max_lines and i >= max_lines:
                break
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 13:
                continue
            chrom = parts[5]
            if chrom != "chr11":
                continue
            rep_name, rep_class, rep_family = parts[10], parts[11], parts[12]
            is_alu = "Alu" in rep_name or rep_family == "Alu" or "Alu" in rep_class
            is_sva = "SVA" in rep_name or "SVA" in rep_family or rep_class == "Retroposon"
            if not (is_alu or is_sva):
                continue
            if is_sva and "SVA" not in rep_name and "SVA" not in rep_family:
                continue  # skip non-SVA Retroposon
            start, end = parts[6], parts[7]
            strand = parts[9]
            fout.write(
                f"{chrom}\t{start}\t{end}\t{rep_name}\t0\t{strand}\t{rep_class}/{rep_family}\n"
            )
            n += 1
    print(f"Alu/SVA chr11 intervals: {n}")
    return out


def fetch_segdup_chr11() -> Path | None:
    out = DATA / "genomicSuperDups_chr11.bed"
    if out.exists():
        return out
    url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/genomicSuperDups.txt.gz"
    gz = DATA / "genomicSuperDups.txt.gz"
    try:
        _download(url, gz, timeout=300)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: segdup fetch failed: {exc}")
        return None
    n = 0
    with gzip.open(gz, "rt", encoding="utf-8", errors="replace") as fin, out.open(
        "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            # chrom start end ...
            chrom = parts[1] if parts[1].startswith("chr") else parts[0]
            # UCSC genomicSuperDups: bin, chrom, chromStart, chromEnd, ...
            if parts[1].startswith("chr"):
                chrom, start, end = parts[1], parts[2], parts[3]
            else:
                chrom, start, end = parts[0], parts[1], parts[2]
            if chrom != "chr11":
                continue
            fout.write(f"{chrom}\t{start}\t{end}\tsegdup\n")
            n += 1
    print(f"segdup chr11: {n}")
    return out


def write_gnomad_fetch_note() -> None:
    note = DATA / "GNOMAD_FETCH_NOTE.md"
    chrom, start, end = HBB_WINDOW
    note.write_text(
        f"""# gnomAD — chr11 / HBB window only

**Forbidden:** full gnomAD genome download.

## Recommended (manual)

1. Open https://gnomad.broadinstitute.org/downloads
2. Download **sites VCF for chr11 only** (v4.1 genomes), OR
3. Use remote tabix for HBB window:

```bash
# Example — replace URL with current release chr11 sites file
bcftools view -r {chrom}:{start}-{end} -Oz -o data/gnomad_hbb_window.vcf.gz \\
  <gnomad.genomes.v4.1.sites.chr11.vcf.bgz>
tabix -p vcf data/gnomad_hbb_window.vcf.gz
```

Until gnomAD slice is present, `run_pilot.py` uses ClinVar P/LP as exploratory test
and builds control pool from non-TE ClinVar / local TSV.
""",
        encoding="utf-8",
    )
    print(f"wrote {note}")


def write_minimal_ctcf_tss_placeholders() -> None:
    """Placeholders near HBB until ENCODE/GENCODE fetch wired."""
    ctcf = DATA / "ctcf_GM12878_peaks.bed"
    tss = DATA / "gencode_v46_protein_coding_TSS_chr11.bed"
    if not ctcf.exists():
        # Approximate CTCF near HBB LCR / known peaks — FLAG as placeholder
        ctcf.write_text(
            "# PLACEHOLDER — replace with ENCODE GM12878 CTCF narrowPeak chr11\n"
            "chr11\t5220000\t5220500\tCTCF_HBB_proxy\n"
            "chr11\t5270000\t5270500\tCTCF_HBB_proxy2\n"
            "chr11\t10800000\t10800500\tCTCF_proxy\n",
            encoding="utf-8",
        )
        print(f"WARN: wrote placeholder {ctcf}")
    if not tss.exists():
        tss.write_text(
            "# PLACEHOLDER — replace with GENCODE TSS chr11\n"
            "chr11\t5225464\t5225475\tHBB\t0\t-\n"
            "chr11\t5246696\t5246707\tHBD\t0\t-\n"
            "chr11\t5255756\t5255767\tHBBP1\t0\t-\n",
            encoding="utf-8",
        )
        print(f"WARN: wrote placeholder {tss}")


def main() -> int:
    skip_clinvar = "--skip-clinvar" in sys.argv
    DATA.mkdir(parents=True, exist_ok=True)
    fetch_blacklist()
    fetch_segdup_chr11()
    build_alu_sva_from_rmsk()
    fetch_clinvar_chr11(skip=skip_clinvar)
    write_gnomad_fetch_note()
    write_minimal_ctcf_tss_placeholders()
    print("fetch done — see data/ and GNOMAD_FETCH_NOTE.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
