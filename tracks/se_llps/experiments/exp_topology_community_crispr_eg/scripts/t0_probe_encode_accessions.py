#!/usr/bin/env python3
"""T0 accession probe for C-B1 (topology community vs SE for CRISPR E–G, K562).

Queries ENCODE REST API + records public EngreitzLab CRISPR benchmark / SCREEN cCRE v3
availability. Metadata only — does NOT download multi-GB prediction beds.

Writes: ../data/t0_accession_probe.json
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENCODE = "https://www.encodeproject.org"
OUT = Path(__file__).resolve().parent.parent / "data" / "t0_accession_probe.json"
USER_AGENT = "DNA-Ladder-T0-probe/1.0 (C-B1 topology CRISPR; metadata only)"

# Known pins to verify (not invent)
HIC_EXP = "ENCSR545YBD"
HIC_LOOP_PREFERRED = "ENCFF693XIL"
CCRE_V4_AGNOSTIC = "ENCSR800VNX"
CCRE_V3_K562 = "ENCSR940SYU"
CCRE_V4_K562 = "ENCSR935IVQ"
RE2G_K562 = "ENCSR512SWG"
RE2G_EXT_K562 = "ENCSR621BIJ"

CRISPR_BENCH_URL = (
    "https://raw.githubusercontent.com/EngreitzLab/ENCODE_rE2G/main/"
    "reference/EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz"
)
CRISPR_BENCH_SHA256 = (
    "d0806eb8a3cfe71066a9a1c88da2f730ccf5d86364bd52ca9bc6ba628744e417"
)
SCREEN_V3_CCRE = "https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.bed"


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def encode_get(path_or_url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    if path_or_url.startswith("http"):
        url = path_or_url
    else:
        url = ENCODE + path_or_url
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=90, context=_ctx()) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return {"_error": True, "status": e.code, "url": url, "body": body}
    except Exception as e:  # noqa: BLE001 — record network failures in probe JSON
        return {"_error": True, "status": None, "url": url, "body": str(e)[:500]}


def head_meta(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60, context=_ctx()) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return {
                "url": url,
                "ok": True,
                "http_status": getattr(resp, "status", 200),
                "content_length": headers.get("content-length"),
                "content_type": headers.get("content-type"),
                "etag": headers.get("etag"),
                "last_modified": headers.get("last-modified"),
            }
    except urllib.error.HTTPError as e:
        return {"url": url, "ok": False, "http_status": e.code, "error": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "ok": False, "http_status": None, "error": str(e)}


def file_summary(acc: str) -> dict[str, Any]:
    d = encode_get(f"/files/{acc}/", {"format": "json"})
    if d.get("_error"):
        return {"accession": acc, "exists": False, "error": d}
    return {
        "accession": acc,
        "exists": True,
        "status": d.get("status"),
        "file_format": d.get("file_format"),
        "output_type": d.get("output_type"),
        "assembly": d.get("assembly"),
        "file_size": d.get("file_size"),
        "preferred_default": d.get("preferred_default"),
        "dataset": d.get("dataset"),
        "href": d.get("href"),
        "cloud_metadata": bool(d.get("cloud_metadata")),
        "md5sum": d.get("md5sum"),
    }


def annotation_summary(acc: str) -> dict[str, Any]:
    d = encode_get(f"/annotations/{acc}/", {"format": "json"})
    if d.get("_error"):
        return {"accession": acc, "exists": False, "error": d}
    return {
        "accession": acc,
        "exists": True,
        "status": d.get("status"),
        "annotation_type": d.get("annotation_type"),
        "encyclopedia_version": d.get("encyclopedia_version"),
        "description": (d.get("description") or "")[:240],
        "date_released": d.get("date_released"),
        "aliases": d.get("aliases"),
        "href": f"{ENCODE}/annotations/{acc}/",
    }


def experiment_summary(acc: str) -> dict[str, Any]:
    d = encode_get(f"/experiments/{acc}/", {"format": "json"})
    if d.get("_error"):
        return {"accession": acc, "exists": False, "error": d}
    return {
        "accession": acc,
        "exists": True,
        "status": d.get("status"),
        "assay_title": d.get("assay_title"),
        "biosample_summary": d.get("biosample_summary"),
        "description": (d.get("description") or "")[:240],
        "href": f"{ENCODE}/experiments/{acc}/",
    }


def list_dataset_files(dataset_path: str, limit: int = 30) -> list[dict[str, Any]]:
    d = encode_get(
        "/search/",
        {
            "type": "File",
            "dataset": dataset_path,
            "status": "released",
            "format": "json",
            "limit": str(limit),
        },
    )
    if d.get("_error"):
        return [{"_error": d}]
    out = []
    for f in d.get("@graph", []):
        out.append(
            {
                "accession": f.get("accession"),
                "file_format": f.get("file_format"),
                "output_type": f.get("output_type"),
                "assembly": f.get("assembly"),
                "file_size": f.get("file_size"),
                "preferred_default": f.get("preferred_default"),
                "href": f.get("href"),
            }
        )
    return out


def search_flowfish(limit: int = 15) -> dict[str, Any]:
    d = encode_get(
        "/search/",
        {
            "type": "FunctionalCharacterizationExperiment",
            "assay_title": "Flow-FISH CRISPR screen",
            "biosample_ontology.term_name": "K562",
            "status": "released",
            "format": "json",
            "limit": str(limit),
        },
    )
    if d.get("_error"):
        return {"_error": d}
    rows = []
    for e in d.get("@graph", []):
        rows.append(
            {
                "accession": e.get("accession"),
                "assay_title": e.get("assay_title"),
                "description": (e.get("description") or "")[:160],
                "href": f"{ENCODE}/functional-characterization-experiments/{e.get('accession')}/",
            }
        )
    return {"total": d.get("total"), "sample": rows}


def search_element_quant_files(limit: int = 20) -> dict[str, Any]:
    d = encode_get(
        "/search/",
        {
            "type": "File",
            "assay_title": "Flow-FISH CRISPR screen",
            "biosample_ontology.term_name": "K562",
            "output_type": "element quantifications",
            "status": "released",
            "format": "json",
            "limit": str(limit),
        },
    )
    if d.get("_error"):
        return {"_error": d}
    rows = []
    for f in d.get("@graph", []):
        rows.append(
            {
                "accession": f.get("accession"),
                "file_format": f.get("file_format"),
                "assembly": f.get("assembly"),
                "file_size": f.get("file_size"),
                "dataset": f.get("dataset"),
            }
        )
    return {"total": d.get("total"), "sample": rows}


def main() -> int:
    report: dict[str, Any] = {
        "probe": "t0_probe_encode_accessions_c_b1_topology",
        "experiment": "exp_topology_community_crispr_eg",
        "candidate_id": "C-B1",
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "encode_base": ENCODE,
        "note": "Metadata only — no multi-GB ENCODE-rE2G prediction downloads",
        "crispr_benchmark": {},
        "flowfish_encode": {},
        "hic_loops_k562": {},
        "ccre": {},
        "encode_re2g_k562_products": {},
        "t0_status": "UNKNOWN",
        "freeze_recommendation": {},
    }

    print("=== CRISPR ensemble benchmark (EngreitzLab) ===")
    head = head_meta(CRISPR_BENCH_URL)
    # GitHub raw may not support HEAD well; also try GET range via encode_get style
    if not head.get("ok"):
        req = urllib.request.Request(
            CRISPR_BENCH_URL,
            headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=90, context=_ctx()) as resp:
                head = {
                    "url": CRISPR_BENCH_URL,
                    "ok": True,
                    "http_status": getattr(resp, "status", 200),
                    "content_length": resp.headers.get("Content-Length")
                    or resp.headers.get("Content-Range"),
                    "note": "range_get_fallback",
                }
        except Exception as e:  # noqa: BLE001
            head = {"url": CRISPR_BENCH_URL, "ok": False, "error": str(e)}
    report["crispr_benchmark"] = {
        "url": CRISPR_BENCH_URL,
        "head": head,
        "sha256_precomputed": CRISPR_BENCH_SHA256,
        "n_pairs_expected": 10412,
        "cell_type": "K562",
        "includes_FlowFISH_K562": True,
        "repo_commit_path_note": "EngreitzLab/ENCODE_rE2G reference/ (public)",
    }
    print("crispr ok=", head.get("ok"), "sha256=", CRISPR_BENCH_SHA256[:16], "...")

    print("\n=== ENCODE Flow-FISH CRISPR K562 ===")
    ff = search_flowfish()
    eq = search_element_quant_files()
    report["flowfish_encode"] = {
        "experiments": ff,
        "element_quantification_files": eq,
        "note": (
            "Many per-locus Flow-FISH screens released; primary frozen labels for C-B1 "
            "are the EngreitzLab ensemble CRISPR benchmark (harmonized positives/negatives)."
        ),
    }
    print("Flow-FISH experiments total=", ff.get("total"), "element quant files=", eq.get("total"))

    print("\n=== Hi-C loops K562 ===")
    hic_exp = experiment_summary(HIC_EXP)
    hic_file = file_summary(HIC_LOOP_PREFERRED)
    hic_files = list_dataset_files(f"/experiments/{HIC_EXP}/", limit=40)
    bedpe_loops = [
        f
        for f in hic_files
        if isinstance(f, dict)
        and (f.get("file_format") or "").lower() == "bedpe"
        and "loop" in (f.get("output_type") or "").lower()
    ]
    report["hic_loops_k562"] = {
        "experiment": hic_exp,
        "preferred_loop_file": hic_file,
        "bedpe_loop_files_sample": bedpe_loops[:12],
        "usable_processed_bedpe": bool(
            hic_file.get("exists") and hic_file.get("status") == "released"
        ),
    }
    print(
        HIC_LOOP_PREFERRED,
        "exists=",
        hic_file.get("exists"),
        "preferred_default=",
        hic_file.get("preferred_default"),
        "size=",
        hic_file.get("file_size"),
    )

    print("\n=== cCRE v3 / v4 ===")
    screen_v3 = head_meta(SCREEN_V3_CCRE)
    ccre_v3_k562 = annotation_summary(CCRE_V3_K562)
    ccre_v3_files = list_dataset_files(f"/annotations/{CCRE_V3_K562}/")
    ccre_v4_agn = annotation_summary(CCRE_V4_AGNOSTIC)
    ccre_v4_files = list_dataset_files(f"/annotations/{CCRE_V4_AGNOSTIC}/")
    ccre_v4_k562 = annotation_summary(CCRE_V4_K562)
    report["ccre"] = {
        "screen_registry_v3_bed": screen_v3,
        "encode_v3_k562": {"annotation": ccre_v3_k562, "files": ccre_v3_files},
        "encode_v4_agnostic": {"annotation": ccre_v4_agn, "files": ccre_v4_files},
        "encode_v4_k562": {"annotation": ccre_v4_k562},
        "preferred_for_claim": "SCREEN Registry-V3 GRCh38-cCREs.bed (v3); ENCODE ENCFF210CAN as portal v3 K562 bed",
    }
    print("SCREEN v3 ok=", screen_v3.get("ok"), "len=", screen_v3.get("content_length"))
    print("ENCODE v3 K562", CCRE_V3_K562, "exists=", ccre_v3_k562.get("exists"))

    print("\n=== ENCODE-rE2G K562 prediction products (reference only) ===")
    re2g = annotation_summary(RE2G_K562)
    re2g_ext = annotation_summary(RE2G_EXT_K562)
    report["encode_re2g_k562_products"] = {
        "standard": {"annotation": re2g, "files": list_dataset_files(f"/annotations/{RE2G_K562}/")},
        "extended": {
            "annotation": re2g_ext,
            "files": list_dataset_files(f"/annotations/{RE2G_EXT_K562}/"),
        },
        "usage": "Reference / optional EXPLORATORY ceiling only — NOT primary features for C-B1",
    }

    crispr_ok = bool(head.get("ok"))
    hic_ok = bool(report["hic_loops_k562"]["usable_processed_bedpe"])
    ccre_ok = bool(screen_v3.get("ok") or ccre_v3_k562.get("exists"))
    flowfish_ok = bool((ff.get("total") or 0) > 0) or crispr_ok

    if crispr_ok and hic_ok and ccre_ok:
        t0 = "PASS_FREEZE"
    elif hic_ok and ccre_ok and flowfish_ok:
        t0 = "PASS_PARTIAL_CRISPR_VIA_ENSEMBLE_OR_FLOWFISH"
    else:
        t0 = "BLOCKED_DATA"

    report["t0_status"] = t0
    report["freeze_recommendation"] = {
        "crispr_eg_labels": {
            "primary": CRISPR_BENCH_URL,
            "sha256": CRISPR_BENCH_SHA256,
            "status": "FROZEN" if crispr_ok else "BLOCKED",
        },
        "hic_loops_k562": {
            "experiment": HIC_EXP,
            "file": HIC_LOOP_PREFERRED,
            "status": "FROZEN" if hic_ok else "BLOCKED",
        },
        "ccre_v3": {
            "screen_bed": SCREEN_V3_CCRE,
            "encode_k562_bed_candidate": "ENCFF210CAN",
            "encode_k562_annotation": CCRE_V3_K562,
            "v4_fallback_agnostic_bed": "ENCFF420VPZ",
            "status": "FROZEN" if ccre_ok else "BLOCKED",
        },
        "se_membership": {
            "path": "tracks/se_llps/data/input/k562_super_enhancers_grch38.json",
            "status": "ON_DISK",
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print("\nWrote", OUT)
    print("t0_status=", t0)
    return 0 if t0.startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
