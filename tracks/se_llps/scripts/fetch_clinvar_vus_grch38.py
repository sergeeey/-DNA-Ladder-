#!/usr/bin/env python3
"""exp_heritability_vus_se_frequency: fetch ClinVar SNVs genome-wide (GRCh38)
with ClinicalSignificance == "Uncertain significance" (strict, single-
category, excludes conflicting-interpretation entries). Classifies each VUS
as inside/outside a super-enhancer region using the K562/HepG2 dbSUPER
calls already fetched for the LLPS experiments -- no new SE data needed.
"""

import bisect
import gzip
import io
import json
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
OUT = ROOT / "data/input/clinvar_vus_grch38_se_classified.json"

SE_FILES = {
    "K562": ROOT / "data/input/k562_super_enhancers_grch38.json",
    "HepG2": ROOT / "data/input/hepg2_super_enhancers_grch38.json",
}


def load_se_intervals(path):
    with open(path) as f:
        data = json.load(f)
    by_chrom = defaultdict(list)
    for se in data["super_enhancers"]:
        by_chrom[se["chrom"]].append((se["start"], se["end"]))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return dict(by_chrom)


def in_any_interval(chrom, pos, by_chrom):
    intervals = by_chrom.get(chrom)
    if not intervals:
        return False
    starts = [s for s, _ in intervals]
    i = bisect.bisect_right(starts, pos) - 1
    if i < 0:
        return False
    s, e = intervals[i]
    return s <= pos < e


def main() -> None:
    se_by_cell = {name: load_se_intervals(path) for name, path in SE_FILES.items()}
    print(f"Loaded SE region sets: {list(se_by_cell.keys())}")

    print("Downloading ClinVar variant_summary.txt.gz...")
    with urllib.request.urlopen(CLINVAR_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    vus_list = []
    seen = set()
    n_scanned = n_grch38_snv = n_vus = 0

    with gzip.open(io.BytesIO(raw)) as gz:
        header = gz.readline().decode().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        for line in gz:
            n_scanned += 1
            row = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(row) <= max(col.values()):
                continue
            if row[col.get("Assembly", -1)] != "GRCh38":
                continue
            if row[col.get("Type", -1)] != "single nucleotide variant":
                continue
            n_grch38_snv += 1

            sig = row[col.get("ClinicalSignificance", -1)]
            if sig.strip() != "Uncertain significance":
                continue
            n_vus += 1

            chrom_raw = row[col["Chromosome"]]
            chrom = "chr" + chrom_raw if not chrom_raw.startswith("chr") else chrom_raw
            try:
                start = int(row[col["Start"]])
            except (ValueError, KeyError):
                continue

            pos_vcf = row[col.get("PositionVCF", -1)] if "PositionVCF" in col else None
            ref_vcf = (
                row[col.get("ReferenceAlleleVCF", -1)] if "ReferenceAlleleVCF" in col else None
            )
            alt_vcf = (
                row[col.get("AlternateAlleleVCF", -1)] if "AlternateAlleleVCF" in col else None
            )

            key = (chrom, start, pos_vcf, ref_vcf, alt_vcf)
            if key in seen:
                continue
            seen.add(key)

            in_se = {name: in_any_interval(chrom, start, se_by_cell[name]) for name in se_by_cell}

            vus_list.append(
                {
                    "chrom": chrom,
                    "start": start,
                    "gene_symbol": row[col.get("GeneSymbol", -1)],
                    "position_vcf": pos_vcf,
                    "ref_vcf": ref_vcf,
                    "alt_vcf": alt_vcf,
                    "in_se": in_se,
                }
            )

    n_in_k562_se = sum(1 for v in vus_list if v["in_se"]["K562"])
    n_in_hepg2_se = sum(1 for v in vus_list if v["in_se"]["HepG2"])
    print(
        f"  Scanned {n_scanned} rows, {n_grch38_snv} GRCh38 SNVs, {n_vus} strict VUS "
        f"({len(vus_list)} unique)"
    )
    print(f"  In K562 SE: {n_in_k562_se}, in HepG2 SE: {n_in_hepg2_se}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {
                "source": "ClinVar variant_summary.txt.gz (NCBI FTP), GRCh38",
                "filter": "GRCh38 SNV, ClinicalSignificance == 'Uncertain significance' (strict)",
                "n_total": len(vus_list),
                "n_in_k562_se": n_in_k562_se,
                "n_in_hepg2_se": n_in_hepg2_se,
                "variants": vus_list,
            },
            f,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
