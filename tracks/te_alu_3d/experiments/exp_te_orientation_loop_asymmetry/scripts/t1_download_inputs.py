#!/usr/bin/env python3
"""Download C-J1 primary inputs (ENCODE Hi-C bedpe + UCSC rmsk)."""

from __future__ import annotations

import hashlib
import json
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
OUT = EXP / "data" / "input"
MANIFEST = EXP / "data" / "download_checksums.json"
USER_AGENT = "DNA-Ladder-C-J1/1.0 (desk; public ENCODE/UCSC only)"
ENCODE = "https://www.encodeproject.org"

FILES = {
    "ENCFF693XIL": {
        "role": "hic_hiccups_loops",
        "url": f"{ENCODE}/files/ENCFF693XIL/@@download/ENCFF693XIL.bedpe.gz",
        "filename": "ENCFF693XIL.bedpe.gz",
        "portal_md5": "ae663464bdbe60998e422254ea0dac2c",
    },
    "rmsk_hg38": {
        "role": "repeatmasker_hg38",
        "url": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz",
        "filename": "rmsk.txt.gz",
        "portal_md5": None,
    },
}


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


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


def download(url: str, dest: Path, expected_md5: str | None) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        digests = hash_file(dest)
        if expected_md5 and digests["md5"] != expected_md5:
            print(f"  WARN md5 mismatch {dest.name}; re-download")
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
    with urllib.request.urlopen(req, timeout=600, context=_ctx()) as resp:
        with dest.open("wb") as out:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    digests = hash_file(dest)
    if expected_md5 and digests["md5"] != expected_md5:
        return {
            "status": "md5_mismatch",
            "path": str(dest),
            "expected_md5": expected_md5,
            **digests,
            "url": url,
        }
    return {
        "status": "downloaded",
        "path": str(dest),
        "size_bytes": dest.stat().st_size,
        **digests,
        "url": url,
    }


def main() -> int:
    report = {
        "experiment": "exp_te_orientation_loop_asymmetry",
        "candidate_id": "C-J1",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "files": {},
    }
    ok = True
    for key, meta in FILES.items():
        print(f"=== {key} ===")
        dest = OUT / meta["filename"]
        result = download(meta["url"], dest, meta.get("portal_md5"))
        report["files"][key] = {**meta, "download": result}
        if result.get("status") not in {"cached", "downloaded"}:
            ok = False
            print(f"  FAIL: {result}")
        else:
            print(f"  OK md5={result['md5']} size={result.get('size_bytes')}")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
