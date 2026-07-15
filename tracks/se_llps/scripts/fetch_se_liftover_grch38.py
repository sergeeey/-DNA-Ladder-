#!/usr/bin/env python3
"""Fetch dbSUPER's K562 super-enhancer call set (hg19, the only build dbSUPER
publishes -- verified: no hg38/GRCh38 version exists, 404 on both) and lift
it to GRCh38 via the real UCSC hg19ToHg38.over.chain.gz chain file, using
this repo's own from-scratch liftover.py (no external liftover dependency).
"""

import json
import os
import urllib.request
from pathlib import Path

from liftover import load_chain_file, lift_interval

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

DBSUPER_URL = "https://asntech.org/dbsuper/data/bed/hg19/K562.bed"
CHAIN_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz"
OUT = ROOT / "data/input/k562_super_enhancers_grch38.json"


def main() -> None:
    print(f"Fetching dbSUPER K562 (hg19): {DBSUPER_URL}")
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
    print(f"  loaded chains for {len(chains)} chromosomes")

    se_grch38 = []
    n_failed = 0
    for chrom, start, end, name in se_hg19:
        lifted = lift_interval(chains, chrom, start, end)
        if lifted is None:
            n_failed += 1
            continue
        lchrom, lstart, lend = lifted
        se_grch38.append({"chrom": lchrom, "start": lstart, "end": lend, "name": name})

    print(
        f"  Lifted {len(se_grch38)}/{len(se_hg19)} super-enhancers to GRCh38 "
        f"({n_failed} failed to map -- fell in a chain gap or unmapped region)"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {
                "source": f"dbSUPER K562 (hg19): {DBSUPER_URL}, lifted to GRCh38 via "
                f"UCSC chain file: {CHAIN_URL}",
                "n_hg19": len(se_hg19),
                "n_grch38_lifted": len(se_grch38),
                "n_failed_to_lift": n_failed,
                "super_enhancers": se_grch38,
            },
            f,
            indent=2,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
