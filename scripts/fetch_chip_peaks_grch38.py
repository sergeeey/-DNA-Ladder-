#!/usr/bin/env python3
"""Fetch BRD4/MED1/POLR2A ChIP-seq narrowPeak files from ENCODE, all GRCh38
(genome-build decision recorded in experiments/exp_llps_promoter_vs_se_chip_evidence/claim.md
2026-07-08: MED1 has no released hg19 files, so GRCh38 is used uniformly for
all three factors rather than mixing builds).

Accessions chosen 2026-07-08 via the ENCODE REST API (see claim.md):
  BRD4:   ENCSR583ACG -> file ENCFF863NLN (IDR thresholded peaks, GRCh38, released)
  MED1:   ENCSR269BSA -> file ENCFF240BWI (IDR thresholded peaks, GRCh38, released)
  POLR2A: ENCSR031TFS -> file ENCFF881ONC (optimal IDR thresholded peaks, GRCh38, released)
"""

import gzip
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

FILES = {
    "BRD4": "ENCFF863NLN",
    "MED1": "ENCFF240BWI",
    "POLR2A": "ENCFF881ONC",
}

OUT_DIR = ROOT / "data/input"


def fetch_narrowpeak(accession: str):
    url = f"https://www.encodeproject.org/files/{accession}/@@download/{accession}.bed.gz"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    peaks = []
    with gzip.open(io.BytesIO(raw)) as gz:
        for line in gz:
            cols = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(cols) < 7:
                continue
            chrom, start, end = cols[0], int(cols[1]), int(cols[2])
            signal_value = float(cols[6])  # narrowPeak col 7 = signalValue
            peaks.append({"chrom": chrom, "start": start, "end": end, "signal": signal_value})
    return peaks


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for factor, accession in FILES.items():
        print(f"Fetching {factor} ({accession})...")
        peaks = fetch_narrowpeak(accession)
        print(f"  {len(peaks)} peaks (GRCh38)")
        out_path = OUT_DIR / f"chip_{factor.lower()}_grch38.json"
        with open(out_path, "w") as f:
            json.dump(
                {
                    "factor": factor,
                    "accession": accession,
                    "source": f"https://www.encodeproject.org/files/{accession}/",
                    "assembly": "GRCh38",
                    "n_peaks": len(peaks),
                    "peaks": peaks,
                },
                f,
            )
        print(f"  Saved: {out_path}")


if __name__ == "__main__":
    main()
