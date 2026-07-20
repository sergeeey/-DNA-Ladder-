#!/usr/bin/env python3
"""T1 download: frozen primary bedpe + CTCF peaks (+ optional RMSK).

Real public ENCODE / UCSC files only. Computes on-disk md5/sha256.
Large binaries land in ../data/input/ (gitignored); writes checksum sidecar JSON
and prints rows for data_manifest.md.

Does NOT compute enrichment ORs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXP = Path(__file__).resolve().parent.parent
OUT_DIR = EXP / "data" / "input"
MANIFEST_JSON = EXP / "data" / "download_checksums.json"
ENCODE = "https://www.encodeproject.org"
USER_AGENT = "DNA-Ladder-C-A1-T1/1.0 (desk; public ENCODE/UCSC only)"

# Frozen primary + CTCF control (CTCF chosen: preferred_default conservative IDR, K562, GRCh38)
DEFAULT_FILES: dict[str, dict[str, Any]] = {
    "ENCFF511QFN": {
        "role": "pol2_chia_pet_primary_loops",
        "experiment": "ENCSR880DSH",
        "assembly": "GRCh38",
        "format": "bedpe.gz",
        "portal_md5": "ec8482f0227730d178169776b209c10f",
        "url": f"{ENCODE}/files/ENCFF511QFN/@@download/ENCFF511QFN.bedpe.gz",
        "filename": "ENCFF511QFN.bedpe.gz",
        "required": True,
    },
    "ENCFF693XIL": {
        "role": "hic_primary_loops",
        "experiment": "ENCSR545YBD",
        "assembly": "GRCh38",
        "format": "bedpe.gz",
        "portal_md5": "ae663464bdbe60998e422254ea0dac2c",
        "url": f"{ENCODE}/files/ENCFF693XIL/@@download/ENCFF693XIL.bedpe.gz",
        "filename": "ENCFF693XIL.bedpe.gz",
        "required": True,
    },
    "ENCFF769AUF": {
        "role": "ctcf_k562_conservative_idr_peaks",
        "experiment": "ENCSR000AKO",
        "assembly": "GRCh38",
        "format": "bed.gz",
        "portal_md5": "7d086cac19c5311a77b7e21e3d931435",
        "url": f"{ENCODE}/files/ENCFF769AUF/@@download/ENCFF769AUF.bed.gz",
        "filename": "ENCFF769AUF.bed.gz",
        "required": True,
        "notes": "CTCF K562 TF ChIP-seq; conservative IDR thresholded peaks; preferred_default",
    },
}

RMSK = {
    "role": "repeatmasker_hg38",
    "assembly": "hg38/GRCh38",
    "format": "txt.gz",
    "url": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz",
    "filename": "rmsk.txt.gz",
    "required": False,
    "notes": "UCSC RepeatMasker table dump; large — gitignored",
}


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def encode_file_meta(accession: str) -> dict[str, Any]:
    url = f"{ENCODE}/files/{accession}/?format=json"
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=90, context=_ctx()) as resp:
        d = json.load(resp)
    href = d.get("href") or f"/files/{accession}/@@download/{accession}"
    if not href.startswith("http"):
        href = ENCODE + href
    return {
        "accession": accession,
        "md5sum": d.get("md5sum"),
        "file_size": d.get("file_size"),
        "assembly": d.get("assembly"),
        "output_type": d.get("output_type"),
        "file_format": d.get("file_format"),
        "href": href,
        "dataset": d.get("dataset"),
        "preferred_default": d.get("preferred_default"),
    }


def hash_file(path: Path) -> dict[str, str]:
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            md5.update(chunk)
            sha.update(chunk)
    return {"md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def download(url: str, dest: Path, expected_md5: str | None = None) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        digests = hash_file(dest)
        if expected_md5 and digests["md5"] != expected_md5:
            print(f"  WARN existing {dest.name} md5 mismatch portal; re-downloading")
            dest.unlink()
        else:
            print(f"  skip (exists): {dest.name} size={dest.stat().st_size}")
            return {
                "status": "cached",
                "path": str(dest),
                "size_bytes": dest.stat().st_size,
                **digests,
                "url": url,
            }

    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=600, context=_ctx()) as resp:
            with dest.open("wb") as out:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
    except urllib.error.HTTPError as e:
        return {"status": "error", "url": url, "http_status": e.code, "error": str(e)}
    except Exception as e:  # noqa: BLE001 — record network failures honestly
        return {"status": "error", "url": url, "error": str(e)}

    digests = hash_file(dest)
    row = {
        "status": "downloaded",
        "path": str(dest),
        "size_bytes": dest.stat().st_size,
        **digests,
        "url": url,
    }
    if expected_md5:
        row["portal_md5_match"] = digests["md5"] == expected_md5
        if not row["portal_md5_match"]:
            print(
                f"  WARN md5 mismatch: got {digests['md5']} expected {expected_md5}"
            )
    print(f"  ok size={row['size_bytes']} md5={digests['md5']}")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--with-rmsk",
        action="store_true",
        help="Also download UCSC hg38 rmsk.txt.gz (large; optional for T2 CTCF gate)",
    )
    ap.add_argument(
        "--skip-pol2",
        action="store_true",
        help="Skip Pol II bedpe (CTCF gate needs Hi-C + CTCF only)",
    )
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "script": "t1_download_primary_inputs",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembly": "GRCh38",
        "files": {},
        "ctcf_freeze": {
            "accession": "ENCFF769AUF",
            "experiment": "ENCSR000AKO",
            "output_type": "conservative IDR thresholded peaks",
            "rationale": "preferred_default K562 CTCF TF ChIP-seq IDR peaks, GRCh38",
        },
    }

    targets = dict(DEFAULT_FILES)
    if args.skip_pol2:
        targets.pop("ENCFF511QFN", None)

    for acc, meta in targets.items():
        print(f"=== {acc} ({meta['role']}) ===")
        try:
            api = encode_file_meta(acc)
            url = api["href"]
            portal_md5 = api.get("md5sum") or meta.get("portal_md5")
            report["files"][acc] = {
                **meta,
                "api": api,
            }
        except Exception as e:  # noqa: BLE001
            print(f"  API meta failed ({e}); using freeze URL")
            url = meta["url"]
            portal_md5 = meta.get("portal_md5")
            report["files"][acc] = {**meta, "api_error": str(e)}

        dest = OUT_DIR / meta["filename"]
        result = download(url, dest, expected_md5=portal_md5)
        report["files"][acc]["download"] = result
        if meta.get("required") and result.get("status") == "error":
            print(f"REQUIRED download failed: {acc}", file=sys.stderr)
            MANIFEST_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            return 1

    if args.with_rmsk:
        print("=== rmsk.txt.gz (UCSC) ===")
        dest = OUT_DIR / RMSK["filename"]
        result = download(RMSK["url"], dest)
        report["files"]["rmsk_hg38"] = {**RMSK, "download": result}

    MANIFEST_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {MANIFEST_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
