#!/usr/bin/env python3
"""Fetch all inputs needed for exp_llps_promoter_vs_se_hepg2_replication:
dbSUPER HepG2 super-enhancers (hg19, lifted to GRCh38 via this repo's own
liftover.py) and BRD4/MED1/POLR2A ChIP-seq peaks (GRCh38, ENCODE). Reuses
GENCODE TSS data already fetched for the K562 experiment (build-independent
of cell line)."""

import gzip
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))

from liftover import lift_interval, load_chain_file  # noqa: E402

DBSUPER_URL = "https://asntech.org/dbsuper/data/bed/hg19/HepG2.bed"
CHAIN_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz"
SE_OUT = ROOT / "data/input/hepg2_super_enhancers_grch38.json"

PEAK_FILES = {
    "BRD4": "ENCFF898YRY",
    "MED1": "ENCFF493UFO",
    "POLR2A": "ENCFF354VWZ",
}


def fetch_se():
    print(f"Fetching dbSUPER HepG2 (hg19): {DBSUPER_URL}")
    req = urllib.request.Request(DBSUPER_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        se_hg19_text = resp.read().decode("utf-8")
    se_hg19 = []
    for line in se_hg19_text.strip().splitlines():
        cols = line.split("\t")
        chrom, start, end, name = cols[0], int(cols[1]), int(cols[2]), cols[3]
        se_hg19.append((chrom, start, end, name))
    print(f"  {len(se_hg19)} super-enhancers in hg19")

    print(f"Fetching UCSC chain file: {CHAIN_URL}")
    req = urllib.request.Request(CHAIN_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        chain_bytes = resp.read()
    chains = load_chain_file(chain_bytes)

    se_grch38 = []
    n_failed = 0
    for chrom, start, end, name in se_hg19:
        lifted = lift_interval(chains, chrom, start, end)
        if lifted is None:
            n_failed += 1
            continue
        lchrom, lstart, lend = lifted
        se_grch38.append({"chrom": lchrom, "start": lstart, "end": lend, "name": name})
    print(f"  Lifted {len(se_grch38)}/{len(se_hg19)} to GRCh38 ({n_failed} failed to map)")

    SE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(SE_OUT, "w") as f:
        json.dump(
            {
                "source": f"dbSUPER HepG2 (hg19): {DBSUPER_URL}, lifted via {CHAIN_URL}",
                "n_hg19": len(se_hg19),
                "n_grch38_lifted": len(se_grch38),
                "n_failed_to_lift": n_failed,
                "super_enhancers": se_grch38,
            },
            f,
            indent=2,
        )
    print(f"  Saved: {SE_OUT}")


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
            peaks.append({"chrom": chrom, "start": start, "end": end, "signal": float(cols[6])})
    return peaks


def fetch_peaks():
    for factor, accession in PEAK_FILES.items():
        print(f"Fetching {factor} ({accession})...")
        peaks = fetch_narrowpeak(accession)
        print(f"  {len(peaks)} peaks (GRCh38)")
        out_path = ROOT / f"data/input/chip_{factor.lower()}_hepg2_grch38.json"
        with open(out_path, "w") as f:
            json.dump(
                {
                    "factor": factor,
                    "cell_line": "HepG2",
                    "accession": accession,
                    "assembly": "GRCh38",
                    "n_peaks": len(peaks),
                    "peaks": peaks,
                },
                f,
            )
        print(f"  Saved: {out_path}")


if __name__ == "__main__":
    fetch_se()
    fetch_peaks()
