#!/usr/bin/env python3
"""Fetch GRCh38 chromosome sizes (UCSC, real public data) -- used to compute
total accessible genome space for the promoter-vs-SE peak-density test."""

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.chrom.sizes"
OUT = ROOT / "data/input/hg38_chrom_sizes.json"


def main() -> None:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        text = resp.read().decode()

    sizes = {}
    for line in text.splitlines():
        chrom, size = line.split("\t")
        if "_" in chrom or chrom == "chrM":
            continue
        sizes[chrom] = int(size)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"source": URL, "sizes": sizes}, f, indent=2)
    print(f"Saved {len(sizes)} chromosomes to {OUT}")


if __name__ == "__main__":
    main()
