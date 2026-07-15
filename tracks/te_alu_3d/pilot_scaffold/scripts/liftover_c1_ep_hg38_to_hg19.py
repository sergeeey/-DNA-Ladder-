"""Lift locked C1 / E / P coordinates GRCh38 -> GRCh37/hg19 via Ensembl REST."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "09_outputs" / "prospective" / "c1_ep_liftover_hg19.yaml"

COORDS = [
    ("C1", 11, 62753923, 62753923),
    ("E", 11, 62390000, 62395000),
    ("P", 11, 62690000, 62695000),
]


def lift(chrom: int, start: int, end: int) -> list[dict]:
    url = (
        f"https://rest.ensembl.org/map/human/GRCh38/"
        f"{chrom}:{start}..{end}:1/GRCh37?content-type=application/json"
    )
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = json.load(resp)
    return data.get("mappings") or []


def main() -> None:
    lines = [
        "# Auto-generated liftOver via Ensembl REST map/human/GRCh38→GRCh37",
        "# DO NOT paste GRCh38 coords into hg19 .hic Juicebox windows",
        "source_assembly: GRCh38",
        "target_assembly: GRCh37/hg19",
        "method: ensembl_rest_map",
        "locked_ref: C1_claim_freeze_pack_v1.md",
        "regions:",
    ]
    for name, chrom, start, end in COORDS:
        maps = lift(chrom, start, end)
        lines.append(f"  - id: {name}")
        lines.append(f"    grch38: chr{chrom}:{start}-{end}")
        if not maps:
            lines.append("    hg19: null")
            lines.append("    status: NO_MAPPING")
            continue
        m0 = maps[0]["mapped"]
        hg = f"chr{m0['seq_region_name']}:{m0['start']}-{m0['end']}"
        lines.append(f"    hg19: {hg}")
        lines.append(f"    strand: {m0['strand']}")
        lines.append(f"    n_mappings: {len(maps)}")
        lines.append("    status: MAPPED")
        print(name, f"chr{chrom}:{start}-{end}", "->", hg)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
