#!/usr/bin/env python3
"""T1 download C-A2 inputs into data/input/ (gitignored bulky files)."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

from t0_probe_screen_matrix import (
    BASELINE,
    GENCODE,
    REGISTRY_V3,
    RMSK,
    SWITCHING,
    TWOBIT,
    USER_AGENT,
    encode_file_href,
)

ROOT = Path(__file__).resolve().parent.parent
INP = ROOT / "data" / "input"
MANIFEST = ROOT / "data_manifest.md"


def download(url: str, dest: Path, desc: str) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        h = _sha256(dest)
        print(f"SKIP exists {dest.name} sha256={h[:12]}…")
        return {"url": url, "path": str(dest.relative_to(ROOT)), "sha256": h, "bytes": dest.stat().st_size, "skipped": True}
    print(f"GET {desc}: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=600) as resp, open(dest, "wb") as out:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    h = _sha256(dest)
    print(f"  -> {dest} ({dest.stat().st_size} bytes) sha256={h[:12]}…")
    return {"url": url, "path": str(dest.relative_to(ROOT)), "sha256": h, "bytes": dest.stat().st_size, "skipped": False}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    records = []
    records.append(download(REGISTRY_V3, INP / "GRCh38-cCREs.Registry-V3.bed", "registry-v3"))
    records.append(download(RMSK, INP / "rmsk.txt.gz", "rmsk"))
    records.append(download(TWOBIT, INP / "hg38.2bit", "hg38.2bit"))
    records.append(download(GENCODE, INP / "gencode.v47.basic.annotation.gtf.gz", "gencode"))
    records.append(
        download(
            encode_file_href(BASELINE["accession"]),
            INP / f"{BASELINE['accession']}_{BASELINE['biosample']}.bed.gz",
            f"baseline {BASELINE['biosample']}",
        )
    )
    for row in SWITCHING:
        records.append(
            download(
                encode_file_href(row["accession"]),
                INP / f"{row['accession']}_{row['biosample']}.bed.gz",
                f"panel {row['biosample']}",
            )
        )

    meta = {"experiment": "exp_sva_f_ccre_state_switching", "files": records}
    (INP / "download_checksums.json").write_text(json.dumps(meta, indent=2) + "\n")

    lines = [
        "# data_manifest — C-A2 SVA_F dELS switching",
        "",
        "Bulky files under `data/input/` (gitignored). SHA-256 below.",
        "",
        "| File | Bytes | SHA-256 |",
        "|------|------:|---------|",
    ]
    for r in records:
        lines.append(f"| `{r['path']}` | {r['bytes']} | `{r['sha256']}` |")
    MANIFEST.write_text("\n".join(lines) + "\n")
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
