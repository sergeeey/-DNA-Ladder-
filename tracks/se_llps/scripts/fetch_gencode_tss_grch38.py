#!/usr/bin/env python3
"""Fetch GENCODE GRCh38 (native, not lifted) protein-coding gene TSS
annotations -- matches the GRCh38 build decision for this experiment
(see experiments/exp_llps_promoter_vs_se_chip_evidence/claim.md, 2026-07-08)."""

import gzip
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/gencode.v47.basic.annotation.gtf.gz"
OUT = ROOT / "data/input/gencode_tss_grch38.json"


def main() -> None:
    print(f"Downloading GENCODE v47 (native GRCh38): {URL}")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = resp.read()
    print(f"  {len(raw) // 1_000_000}MB downloaded, parsing...")

    tss_list = []
    with gzip.open(io.BytesIO(raw)) as gz:
        for line in gz:
            line = line.decode("utf-8", errors="ignore")
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")
            if len(cols) < 9 or cols[2] != "gene":
                continue
            attrs = cols[8]
            if 'gene_type "protein_coding"' not in attrs:
                continue
            gene_name = None
            for part in attrs.split(";"):
                part = part.strip()
                if part.startswith("gene_name"):
                    gene_name = part.split('"')[1]
                    break
            strand = cols[6]
            start, end = int(cols[3]), int(cols[4])
            tss = start if strand == "+" else end
            tss_list.append({"chrom": cols[0], "tss": tss, "strand": strand, "gene": gene_name})

    print(f"  {len(tss_list)} protein-coding gene TSS")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {"source": URL, "assembly": "GRCh38", "n_genes": len(tss_list), "tss": tss_list}, f
        )
    print(f"Saved: {OUT}")

    noc2l = [g for g in tss_list if g["gene"] == "NOC2L"]
    print(
        f"  Sanity check NOC2L (expect TSS near 959309, per ARCHCODE-verified hg38 comment): {noc2l}"
    )


if __name__ == "__main__":
    main()
