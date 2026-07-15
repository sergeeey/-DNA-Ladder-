"""Fetch HBB window fasta + protein-coding TSS (Ensembl REST). No bulk genome."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
UA = {"User-Agent": "DNK-TE3D-pilot/1.0"}


def _get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={**UA, "Content-Type": "text/plain"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_hbb_fasta(start: int = 5_200_000, end: int = 5_300_000) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    out = DATA / "chr11_hbb_window.fa"
    url = (
        f"https://rest.ensembl.org/sequence/region/human/11:{start}..{end}"
        f"?content-type=text/plain"
    )
    print("GET", url)
    seq = _get(url).decode("utf-8").replace("\n", "").upper()
    out.write_text(f">chr11:{start}-{end}\n{seq}\n", encoding="utf-8")
    meta = DATA / "chr11_hbb_window.fa.meta.json"
    meta.write_text(
        json.dumps({"chrom": "chr11", "start": start, "end": end, "length": len(seq)}, indent=2),
        encoding="utf-8",
    )
    print(f"fasta length={len(seq)} -> {out}")
    return out


def fetch_tss_bed(start: int = 5_100_000, end: int = 5_400_000) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    out = DATA / "gencode_v46_protein_coding_TSS_chr11.bed"
    url = (
        f"https://rest.ensembl.org/overlap/region/human/11:{start}-{end}"
        f"?feature=transcript;content-type=application/json"
    )
    print("GET", url)
    req = urllib.request.Request(
        url, headers={**UA, "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        feats = json.load(resp)

    lines: set[str] = set()
    for f in feats:
        if f.get("biotype") != "protein_coding":
            continue
        strand = int(f.get("strand", 1))
        if strand == 1:
            tss = int(f["start"]) - 1
            strand_s = "+"
        else:
            tss = int(f["end"]) - 1
            strand_s = "-"
        name = f.get("external_name") or f.get("id") or "transcript"
        lines.add(f"chr11\t{tss}\t{tss + 1}\t{name}\t0\t{strand_s}")

    header = (
        "# protein_coding TSS via Ensembl REST (GRCh38)\n"
        f"# region chr11:{start}-{end}; GENCODE-equivalent biotype filter\n"
    )
    out.write_text(header + "\n".join(sorted(lines)) + "\n", encoding="utf-8")
    print(f"TSS n={len(lines)} -> {out}")
    return out


def main() -> int:
    fetch_hbb_fasta()
    fetch_tss_bed()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
