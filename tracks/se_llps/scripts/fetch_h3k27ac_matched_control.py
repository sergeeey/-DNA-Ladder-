#!/usr/bin/env python3
"""Fetch H3K27ac ChIP-seq peaks (GRCh38, K562 and HepG2) to build a matched
"typical enhancer" (TE) control region set: H3K27ac-marked regions that are
NOT part of a super-enhancer. This is the matched-control sensitivity check
requested after external review of exp_llps_promoter_vs_se_chip_evidence --
tests whether SE > "rest of genome" survives when the comparator is
H3K27ac-active-but-not-super regions instead of the whole genome (which
includes large amounts of inactive/heterochromatic DNA that trivially has
near-zero BRD4/MED1 signal).
"""

import gzip
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

H3K27AC_FILES = {
    "K562": "ENCFF038DDS",
    "HepG2": "ENCFF012ADZ",
}


def fetch_narrowpeak(accession: str):
    url = f"https://www.encodeproject.org/files/{accession}/@@download/{accession}.bed.gz"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    peaks = []
    with gzip.open(io.BytesIO(raw)) as gz:
        for line in gz:
            cols = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(cols) < 3:
                continue
            chrom, start, end = cols[0], int(cols[1]), int(cols[2])
            peaks.append({"chrom": chrom, "start": start, "end": end})
    return peaks


def main() -> None:
    for cell, accession in H3K27AC_FILES.items():
        print(f"Fetching H3K27ac {cell} ({accession})...")
        peaks = fetch_narrowpeak(accession)
        print(f"  {len(peaks)} peaks (GRCh38)")
        out_path = ROOT / f"data/input/h3k27ac_{cell.lower()}_grch38.json"
        with open(out_path, "w") as f:
            json.dump(
                {
                    "cell_line": cell,
                    "accession": accession,
                    "assembly": "GRCh38",
                    "n_peaks": len(peaks),
                    "peaks": peaks,
                },
                f,
            )
        print(f"  Saved: {out_path}")


if __name__ == "__main__":
    main()
