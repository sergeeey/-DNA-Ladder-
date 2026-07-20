#!/usr/bin/env python3
"""T0 probe: SCREEN Registry-V3 + ENCODE v3 Full-classification cCRE panel (C-A2).

Metadata / HEAD checks + freeze list. Writes data/t0_accession_probe.json.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent.parent / "data" / "t0_accession_probe.json"
USER_AGENT = "DNA-Ladder-C-A2-T0/1.0 (desk metadata; no bulk unless freeze)"

REGISTRY_V3 = "https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.bed"
RMSK = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz"
TWOBIT = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.2bit"
GENCODE = (
    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/"
    "release_47/gencode.v47.basic.annotation.gtf.gz"
)

# Frozen panel (see ACCESSION_FREEZE_v1.md)
BASELINE = {"biosample": "SK-N-SH", "accession": "ENCFF948UCK"}
SWITCHING = [
    {"biosample": "GM12878", "accession": "ENCFF733BFV"},
    {"biosample": "H1", "accession": "ENCFF803RKE"},
    {"biosample": "HCT116", "accession": "ENCFF127CMS"},
    {"biosample": "HeLa-S3", "accession": "ENCFF830EEV"},
    {"biosample": "HepG2", "accession": "ENCFF287MQD"},
    {"biosample": "IMR-90", "accession": "ENCFF799ZNT"},
    {"biosample": "K562", "accession": "ENCFF210CAN"},
    {"biosample": "MCF-7", "accession": "ENCFF837CPX"},
    {"biosample": "Panc1", "accession": "ENCFF812GKZ"},
    {"biosample": "PC-3", "accession": "ENCFF664YMN"},
]

MISSING_MATRIX_URLS = [
    "https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.CTS",
    "https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.Signal",
]


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def head(url: str, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return {
                "ok": True,
                "status": resp.status,
                "url": url,
                "content_length": headers.get("content-length"),
                "content_type": headers.get("content-type"),
                "last_modified": headers.get("last-modified"),
            }
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "url": url, "error": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "url": url, "error": str(e)}


def encode_file_href(acc: str) -> str:
    return f"https://www.encodeproject.org/files/{acc}/@@download/{acc}.bed.gz"


def classify_verdict(report: dict[str, Any]) -> str:
    """Terminal T0 gate for C-A2 data readiness."""
    if not report.get("registry_v3_ok"):
        return "BLOCKED_DATA"
    n_ok = int(report.get("n_switching_beds_ok") or 0)
    if n_ok < 8:
        return "BLOCKED_DATA"
    if not report.get("baseline_bed_ok"):
        return "BLOCKED_DATA"
    if not report.get("rmsk_ok"):
        return "BLOCKED_DATA"
    # Single-file SCREEN CTS matrix is optional; panel beds substitute.
    return "PASS_FREEZE_CANDIDATE"


def main() -> None:
    registry = head(REGISTRY_V3)
    rmsk = head(RMSK)
    twobit = head(TWOBIT)
    gencode = head(GENCODE)
    missing = [head(u) for u in MISSING_MATRIX_URLS]

    switching_meta = []
    n_ok = 0
    for row in SWITCHING:
        h = head(encode_file_href(row["accession"]))
        ok = bool(h.get("ok"))
        n_ok += int(ok)
        switching_meta.append({**row, "head": h, "ok": ok})

    base_h = head(encode_file_href(BASELINE["accession"]))
    report: dict[str, Any] = {
        "experiment": "exp_sva_f_ccre_state_switching",
        "candidate_id": "C-A2",
        "probed_at_utc": datetime.now(timezone.utc).isoformat(),
        "registry_v3": registry,
        "registry_v3_ok": bool(registry.get("ok")),
        "screen_single_matrix_urls": missing,
        "screen_single_matrix_available": any(m.get("ok") for m in missing),
        "note_matrix": (
            "No single SCREEN multi-cell CTS/Signal file; using ENCODE v3 "
            "Full-classification per-biosample beds as processed substitute."
        ),
        "switching_panel": switching_meta,
        "n_switching_beds_ok": n_ok,
        "baseline": {**BASELINE, "head": base_h, "ok": bool(base_h.get("ok"))},
        "baseline_bed_ok": bool(base_h.get("ok")),
        "rmsk": rmsk,
        "rmsk_ok": bool(rmsk.get("ok")),
        "hg38_2bit": twobit,
        "hg38_2bit_ok": bool(twobit.get("ok")),
        "gencode": gencode,
        "gencode_ok": bool(gencode.get("ok")),
        "min_switching_beds_required": 8,
        "N_switching": len(SWITCHING),
        "not_chia_pet": True,
    }
    report["t0_verdict"] = classify_verdict(report)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"t0_verdict": report["t0_verdict"], "n_switching_ok": n_ok}, indent=2))


if __name__ == "__main__":
    main()
