#!/usr/bin/env python3
"""T0 accession probe for C-K1 (H3K4me3 PLAC-seq vs Hi-C Alu anchors).

Queries ENCODE + 4DN for processed PLAC-seq loop bedpe (GM12878 preferred, else K562).
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
USER_AGENT = "DNA-Ladder-C-K1-T0/1.0 (desk metadata only; no bulk download)"


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
    except Exception as e:  # noqa: BLE001 — probe must survive network quirks
        return {"_error": True, "url": url, "exception": str(e)}


def encode_search(params: dict[str, Any]) -> dict[str, Any]:
    p = dict(params)
    p.setdefault("format", "json")
    return http_get_json(f"{ENCODE}/search/", p)


def list_encode_files(experiment_acc: str) -> list[dict[str, Any]]:
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
        if not any(
            k in blob
            for k in ("bedpe", "loop", "interaction", "contact", "pairs", "biginteract")
        ):
            continue
        out.append(
            {
                "accession": f.get("accession"),
                "file_format": f.get("file_format"),
                "file_type": f.get("file_type"),
                "output_type": f.get("output_type"),
                "assembly": f.get("assembly"),
                "status": f.get("status"),
                "preferred_default": f.get("preferred_default"),
                "file_size": f.get("file_size"),
                "processed_grch38_bedpe": (
                    fmt == "bedpe"
                    and f.get("assembly") == "GRCh38"
                    and f.get("status") in {"released", "archived"}
                    and "loop" in out_type
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
    """Return BLOCKED_DATA unless a usable GRCh38 PLAC loop bedpe exists."""
    encode_bedpe = report.get("encode_usable_plac_grch38_bedpe")
    fourdn_bedpe = report.get("fourdn_usable_plac_grch38_bedpe")
    if encode_bedpe or fourdn_bedpe:
        return "PASS_FREEZE_CANDIDATE"
    return "BLOCKED_DATA"


def main() -> int:
    report: dict[str, Any] = {
        "probe": "t0_probe_plac_vs_hic",
        "experiment": "exp_plac_vs_hic_alu_anchors",
        "candidate_id": "C-K1",
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "encode_base": ENCODE,
        "fourdn_base": FOURDN,
        "note": "Metadata only — no large file downloads",
        "prefer_cell": "GM12878",
        "fallback_cell": "K562",
        "primary_te": "AluSz",
        "mcid_or": 1.5,
        "falsify_or_after_umap_0_3": 1.1,
    }

    # --- ENCODE: PLAC-seq assay facets ---
    encode_assay_probes = {}
    for label, params in [
        ("assay_title_PLAC-seq", {"type": "Experiment", "assay_title": "PLAC-seq", "status": "released", "limit": "5"}),
        ("assay_term_PLAC-seq", {"type": "Experiment", "assay_term_name": "PLAC-seq", "status": "released", "limit": "5"}),
        ("assay_title_HiChIP", {"type": "Experiment", "assay_title": "HiChIP", "status": "released", "limit": "5"}),
        ("searchTerm_PLAC-seq", {"type": "Experiment", "searchTerm": "PLAC-seq", "status": "released", "limit": "10"}),
    ]:
        d = encode_search(params)
        encode_assay_probes[label] = {
            "error": d.get("_error"),
            "status": d.get("status"),
            "total": d.get("total"),
            "note": (
                "placenta_name_collision"
                if not d.get("_error") and d.get("total")
                and any(
                    "placenta" in str(e.get("biosample_summary") or "").lower()
                    for e in d.get("@graph", [])[:5]
                )
                else None
            ),
            "sample_accessions": [e.get("accession") for e in d.get("@graph", [])[:5]],
        }
    report["encode_assay_probes"] = encode_assay_probes

    # --- ENCODE: H3K4me3 ChIA-PET (near-miss, not PLAC) ---
    chia = encode_search(
        {
            "type": "Experiment",
            "assay_title": "ChIA-PET",
            "target.label": "H3K4me3",
            "status": "released",
            "limit": "all",
        }
    )
    chia_rows = []
    any_grch38_bedpe = False
    for e in chia.get("@graph", []) if not chia.get("_error") else []:
        acc = e.get("accession")
        files = list_encode_files(acc) if acc else []
        grch38_bedpe = [f for f in files if f.get("processed_grch38_bedpe")]
        if grch38_bedpe:
            any_grch38_bedpe = True
        chia_rows.append(
            {
                "accession": acc,
                "biosample_summary": e.get("biosample_summary"),
                "loopish_files": files,
                "n_grch38_loop_bedpe": len(grch38_bedpe),
                "rejected_as_plac_substitute": True,
                "reject_reason": "assay_is_ChIA-PET_not_PLAC-seq",
            }
        )
    report["encode_h3k4me3_chia_pet"] = {
        "total": chia.get("total") if not chia.get("_error") else None,
        "error": chia.get("_error"),
        "experiments": chia_rows,
        "any_grch38_loop_bedpe": any_grch38_bedpe,
        "note": "Near-miss only; cannot freeze as H3K4me3 PLAC-seq primary",
    }

    # --- 4DN: PLAC-seq experiment sets for K562 / GM12878 ---
    fourdn_sets: list[dict[str, Any]] = []
    for q in ("K562 PLAC-seq", "GM12878 PLAC-seq H3K4me3", "GM12878 PLAC-seq"):
        d = fourdn_search(
            {"type": "ExperimentSetReplicate", "q": q, "limit": 20, "status": "released"}
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
            summary = summarize_4dn_set(acc)
            summary["query"] = q
            fourdn_sets.append(summary)
    report["fourdn_plac_experiment_sets"] = fourdn_sets
    report["fourdn_any_processed_bedpe"] = any(
        r.get("has_processed_bedpe") for r in fourdn_sets if isinstance(r, dict)
    )

    # --- 4DN bedpe files mentioning PLAC ---
    bedpe = fourdn_search(
        {"type": "FileProcessed", "file_format.file_format": "bedpe", "limit": 100}
    )
    plac_bedpe_hits = []
    if not bedpe.get("_error"):
        for item in bedpe.get("@graph", []):
            acc = item.get("accession")
            if not acc:
                continue
            full = http_get_json(f"{FOURDN}/files-processed/{acc}/")
            if full.get("_error"):
                continue
            desc = (full.get("description") or "") + " " + (full.get("display_title") or "")
            if "plac" not in desc.lower():
                continue
            plac_bedpe_hits.append(
                {
                    "accession": acc,
                    "genome_assembly": full.get("genome_assembly"),
                    "file_type": full.get("file_type"),
                    "description": (full.get("description") or "")[:280],
                    "plac_primary": False,
                    "note": "multi-assay_union_or_non_target_cell — reject as PLAC primary",
                }
            )
    report["fourdn_bedpe_mentioning_plac"] = plac_bedpe_hits

    # Usability flags for verdict
    report["encode_usable_plac_grch38_bedpe"] = False  # no PLAC assay / no freeze
    report["fourdn_usable_plac_grch38_bedpe"] = False  # pairs/hic/mcool only; union rejected
    report["verdict"] = classify_verdict(report)
    report["stop_condition"] = (
        "No processed H3K4me3 PLAC-seq loop bedpe (GRCh38) for GM12878 or K562 on "
        "ENCODE or 4DN; do not call loops from pairs/hic without new claim freeze."
    )
    report["next_fruit_recommend"] = "C-A2"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n")
    print(f"Wrote {OUT}")
    print("verdict=", report["verdict"])
    print("encode_PLAC_assay=", encode_assay_probes.get("assay_title_PLAC-seq", {}).get("status"))
    print("fourdn_sets=", len([r for r in fourdn_sets if r.get("accession")]))
    print(
        "fourdn_any_bedpe=",
        report["fourdn_any_processed_bedpe"],
        "union_plac_bedpe_hits=",
        len(plac_bedpe_hits),
    )
    return 0 if report["verdict"] == "BLOCKED_DATA" else 0


if __name__ == "__main__":
    raise SystemExit(main())
