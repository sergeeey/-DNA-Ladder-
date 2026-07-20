#!/usr/bin/env python3
"""T0 accession probe for C-I1 (Micro-C vs Hi-C Alu-anchor recovery).

Queries ENCODE + 4DN for processed Micro-C loop bedpe (GRCh38 preferred).
Metadata only — no large binary downloads.

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
FOURDN = "https://data.4dnucleome.org"
OUT = Path(__file__).resolve().parent.parent / "data" / "t0_accession_probe.json"
USER_AGENT = "DNA-Ladder-C-I1-T0/1.0 (desk metadata only; no bulk download)"


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def http_get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=120, context=_ctx()) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:400]
        return {"_error": True, "status": e.code, "url": url, "body": body}
    except Exception as e:  # noqa: BLE001
        return {"_error": True, "url": url, "exception": str(e)}


def encode_search(params: dict[str, Any]) -> dict[str, Any]:
    p = dict(params)
    p.setdefault("format", "json")
    return http_get_json(f"{ENCODE}/search/", p)


def list_encode_loopish_files(experiment_acc: str) -> list[dict[str, Any]]:
    d = encode_search(
        {
            "type": "File",
            "dataset": f"/experiments/{experiment_acc}/",
            "limit": "all",
        }
    )
    if d.get("_error"):
        return [{"_error": d}]
    out: list[dict[str, Any]] = []
    for f in d.get("@graph", []):
        fmt = (f.get("file_format") or "").lower()
        out_type = (f.get("output_type") or "").lower()
        ftype = (f.get("file_type") or "").lower()
        blob = f"{fmt} {out_type} {ftype}"
        if not any(k in blob for k in ("bedpe", "loop", "interaction", "contact", "pairs")):
            continue
        out.append(
            {
                "accession": f.get("accession"),
                "file_format": f.get("file_format"),
                "file_type": f.get("file_type"),
                "output_type": f.get("output_type"),
                "assembly": f.get("assembly"),
                "status": f.get("status"),
                "file_size": f.get("file_size"),
                "processed_grch38_bedpe_loop": (
                    fmt == "bedpe"
                    and f.get("assembly") == "GRCh38"
                    and f.get("status") in {"released", "archived"}
                    and ("loop" in out_type or "loop" in ftype)
                ),
            }
        )
    return out


def fourdn_search(params: dict[str, Any]) -> dict[str, Any]:
    return http_get_json(f"{FOURDN}/search/", params)


def summarize_4dn_set(acc: str) -> dict[str, Any]:
    d = http_get_json(f"{FOURDN}/experiment-set-replicates/{acc}/")
    if d.get("_error"):
        return {"accession": acc, "error": d}
    processed: list[dict[str, Any]] = []
    for pf in d.get("processed_files") or []:
        if not isinstance(pf, dict):
            continue
        fmt = pf.get("file_format")
        if isinstance(fmt, dict):
            fmt = fmt.get("display_title") or fmt.get("@id")
        processed.append(
            {
                "accession": pf.get("accession"),
                "file_type": pf.get("file_type"),
                "file_format": fmt,
                "display_title": pf.get("display_title"),
            }
        )
    has_bedpe = any(
        str(p.get("file_format") or "").lower() == "bedpe"
        or "bedpe" in str(p.get("display_title") or "").lower()
        for p in processed
    )
    return {
        "accession": acc,
        "dataset_label": d.get("dataset_label") or d.get("display_title"),
        "processed_files": processed,
        "has_processed_bedpe": has_bedpe,
        "processed_type_summary": sorted(
            {
                f"{p.get('file_type')}|{p.get('file_format')}"
                for p in processed
                if p.get("file_type") or p.get("file_format")
            }
        ),
    }


def classify_verdict(report: dict[str, Any]) -> str:
    if report.get("encode_usable_microc_grch38_bedpe") or report.get(
        "fourdn_usable_microc_grch38_bedpe"
    ):
        return "PASS_FREEZE_CANDIDATE"
    return "BLOCKED_DATA"


def main() -> int:
    report: dict[str, Any] = {
        "probe": "t0_probe_microc_vs_hic",
        "experiment": "exp_microc_vs_hic_alu_anchors",
        "candidate_id": "C-I1",
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "encode_base": ENCODE,
        "fourdn_base": FOURDN,
        "note": "Metadata only — no large file downloads",
        "prefer_cells": ["HFFc6", "H1", "GM12878", "K562"],
        "primary_te": "AluSz",
        "mcid_or": 1.5,
        "falsify_or_after_umap_0_3": 1.1,
    }

    encode_assay_probes: dict[str, Any] = {}
    for label, params in [
        ("assay_title_Micro-C", {"type": "Experiment", "assay_title": "Micro-C", "status": "released", "limit": "20"}),
        ("assay_term_micro-C", {"type": "Experiment", "assay_term_name": "micro-C", "status": "released", "limit": "20"}),
        ("assay_title_DNase-Micro-C", {"type": "Experiment", "assay_title": "DNase-Micro-C", "status": "released", "limit": "10"}),
        ("searchTerm_Micro-C", {"type": "Experiment", "searchTerm": "Micro-C", "status": "released", "limit": "20"}),
    ]:
        d = encode_search(params)
        encode_assay_probes[label] = {
            "error": d.get("_error"),
            "status": d.get("status"),
            "total": d.get("total"),
            "sample_accessions": [e.get("accession") for e in d.get("@graph", [])[:8]],
            "sample_biosamples": [e.get("biosample_summary") for e in d.get("@graph", [])[:8]],
        }
    report["encode_assay_probes"] = encode_assay_probes

    # Expand Micro-C experiments (assay_title) for loop bedpe
    micro = encode_search(
        {
            "type": "Experiment",
            "assay_title": "Micro-C",
            "status": "released",
            "limit": "all",
        }
    )
    if micro.get("_error") or not micro.get("total"):
        micro = encode_search(
            {
                "type": "Experiment",
                "assay_term_name": "micro-C",
                "status": "released",
                "limit": "all",
            }
        )

    micro_rows = []
    any_grch38_bedpe = False
    usable: list[dict[str, Any]] = []
    for e in micro.get("@graph", []) if not micro.get("_error") else []:
        acc = e.get("accession")
        files = list_encode_loopish_files(acc) if acc else []
        grch38_bedpe = [f for f in files if f.get("processed_grch38_bedpe_loop")]
        if grch38_bedpe:
            any_grch38_bedpe = True
            usable.append(
                {
                    "experiment": acc,
                    "biosample_summary": e.get("biosample_summary"),
                    "bedpe_files": grch38_bedpe,
                }
            )
        micro_rows.append(
            {
                "accession": acc,
                "biosample_summary": e.get("biosample_summary"),
                "loopish_files": files,
                "n_grch38_loop_bedpe": len(grch38_bedpe),
            }
        )
    report["encode_microc_experiments"] = {
        "total": micro.get("total") if not micro.get("_error") else None,
        "error": micro.get("_error"),
        "n_listed": len(micro_rows),
        "experiments": micro_rows[:40],  # cap JSON size
        "any_grch38_loop_bedpe": any_grch38_bedpe,
        "usable_grch38_loop_bedpe": usable,
    }

    # 4DN Micro-C sets
    fourdn_sets: list[dict[str, Any]] = []
    for q in (
        "Micro-C HFFc6",
        "Micro-C H1",
        "Micro-C GM12878",
        "Micro-C K562",
        "Micro-C",
    ):
        d = fourdn_search(
            {"type": "ExperimentSetReplicate", "q": q, "limit": 25, "status": "released"}
        )
        if d.get("_error"):
            fourdn_sets.append({"query": q, "error": d})
            continue
        for item in d.get("@graph", []):
            acc = item.get("accession")
            if not acc:
                continue
            if any(r.get("accession") == acc for r in fourdn_sets if "accession" in r):
                continue
            # Prefer titles mentioning Micro-C
            title = (item.get("display_title") or "") + " " + (item.get("dataset_label") or "")
            summary = summarize_4dn_set(acc)
            summary["query"] = q
            summary["display_title"] = item.get("display_title")
            summary["title_mentions_microc"] = "micro-c" in title.lower() or "microc" in title.lower()
            fourdn_sets.append(summary)
    report["fourdn_microc_experiment_sets"] = fourdn_sets
    report["fourdn_any_processed_bedpe"] = any(
        r.get("has_processed_bedpe") and r.get("title_mentions_microc")
        for r in fourdn_sets
        if isinstance(r, dict)
    )
    fourdn_usable = [
        r
        for r in fourdn_sets
        if isinstance(r, dict)
        and r.get("has_processed_bedpe")
        and r.get("title_mentions_microc")
    ]

    report["encode_usable_microc_grch38_bedpe"] = bool(usable)
    report["fourdn_usable_microc_grch38_bedpe"] = bool(fourdn_usable)
    report["fourdn_usable_sets"] = [
        {"accession": r.get("accession"), "dataset_label": r.get("dataset_label"), "has_bedpe": r.get("has_processed_bedpe")}
        for r in fourdn_usable
    ]
    report["verdict"] = classify_verdict(report)
    if report["verdict"] == "PASS_FREEZE_CANDIDATE":
        report["stop_condition"] = None
        report["next_step"] = "Write ACCESSION_FREEZE_v1.md and proceed to AluSz OR"
    else:
        report["stop_condition"] = (
            "No processed Micro-C loop bedpe (GRCh38) usable on ENCODE/4DN for preferred "
            "cells; do not call loops from pairs/mcool without new claim freeze."
        )
        report["next_fruit_recommend"] = "C-L1"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n")
    print(f"Wrote {OUT}")
    print("verdict=", report["verdict"])
    print("encode_usable=", report["encode_usable_microc_grch38_bedpe"], "n=", len(usable))
    print("fourdn_usable=", report["fourdn_usable_microc_grch38_bedpe"], "n=", len(fourdn_usable))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
