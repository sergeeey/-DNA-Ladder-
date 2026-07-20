#!/usr/bin/env python3
"""T0 accession probe for C-A1 (Pol II ChIA-PET vs Hi-C loops, K562).

Queries the ENCODE REST API for processed loop/bedpe files only.
Does NOT download large binaries — metadata JSON only.

Writes: ../data/t0_accession_probe.json (relative to this script).
"""

from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENCODE = "https://www.encodeproject.org"
OUT = Path(__file__).resolve().parent.parent / "data" / "t0_accession_probe.json"

# Early notes / placeholders — verify, do not trust blindly
PLACEHOLDER_CHECK = ["ENCSR000BZZ", "ENCSR444WCX"]

USER_AGENT = "DNA-Ladder-T0-probe/1.0 (desk metadata only; no bulk download)"


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


def experiment_summary(acc: str) -> dict[str, Any]:
    d = encode_get(f"/experiments/{acc}/", {"format": "json"})
    if d.get("_error"):
        return {"accession": acc, "exists": False, "error": d}
    target = d.get("target")
    if isinstance(target, dict):
        target_label = target.get("label")
    else:
        target_label = target
    return {
        "accession": acc,
        "exists": True,
        "status": d.get("status"),
        "assay_title": d.get("assay_title"),
        "assay_term_name": d.get("assay_term_name"),
        "target_label": target_label,
        "biosample_summary": d.get("biosample_summary"),
        "description": (d.get("description") or "")[:240],
        "href": f"{ENCODE}/experiments/{acc}/",
    }


def list_loopish_files(experiment_acc: str) -> list[dict[str, Any]]:
    d = encode_get(
        "/search/",
        {
            "type": "File",
            "dataset": f"/experiments/{experiment_acc}/",
            "format": "json",
            "limit": "all",
        },
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
        # Prefer processed call formats; still record hic/pairs for transparency
        out.append(
            {
                "accession": f.get("accession"),
                "file_format": f.get("file_format"),
                "file_type": f.get("file_type"),
                "output_type": f.get("output_type"),
                "assembly": f.get("assembly"),
                "status": f.get("status"),
                "href": f.get("href"),
                "cloud_metadata": bool(f.get("cloud_metadata")),
                "file_size": f.get("file_size"),
                "dataset": f.get("dataset"),
                "processed_loop_like": fmt in {"bedpe", "bed", "bigbed", "biginteract", "tsv"}
                and "loop" in out_type,
            }
        )
    return out


def search_experiments(search_term: str, limit: int = 15) -> list[dict[str, Any]]:
    d = encode_get(
        "/search/",
        {
            "type": "Experiment",
            "searchTerm": search_term,
            "status": "released",
            "format": "json",
            "limit": str(limit),
        },
    )
    if d.get("_error"):
        return [{"_error": d, "searchTerm": search_term}]
    rows = []
    for e in d.get("@graph", []):
        rows.append(
            {
                "accession": e.get("accession"),
                "assay_title": e.get("assay_title"),
                "assay_term_name": e.get("assay_term_name"),
                "biosample_summary": e.get("biosample_summary"),
                "description": (e.get("description") or "")[:200],
                "href": f"{ENCODE}/experiments/{e.get('accession')}/",
            }
        )
    return rows


def search_loop_files(search_term: str, limit: int = 30) -> list[dict[str, Any]]:
    d = encode_get(
        "/search/",
        {
            "type": "File",
            "searchTerm": search_term,
            "file_format": "bedpe",
            "status": "released",
            "format": "json",
            "limit": str(limit),
        },
    )
    if d.get("_error"):
        return [{"_error": d, "searchTerm": search_term}]
    rows = []
    for f in d.get("@graph", []):
        rows.append(
            {
                "accession": f.get("accession"),
                "file_format": f.get("file_format"),
                "output_type": f.get("output_type"),
                "assembly": f.get("assembly"),
                "status": f.get("status"),
                "dataset": f.get("dataset"),
                "href": f.get("href"),
                "full_href": ENCODE + (f.get("href") or ""),
            }
        )
    return rows


def classify_pol2_usable(files: list[dict[str, Any]]) -> dict[str, Any]:
    processed = [
        f
        for f in files
        if isinstance(f, dict)
        and f.get("processed_loop_like")
        and f.get("status") in {"released", "archived"}
    ]
    bedpe = [f for f in processed if (f.get("file_format") or "").lower() == "bedpe"]
    return {
        "has_processed_loop_like": bool(processed),
        "has_bedpe": bool(bedpe),
        "n_processed_loop_like": len(processed),
        "n_bedpe": len(bedpe),
        "bedpe_accessions": [f.get("accession") for f in bedpe],
        "processed_accessions": [f.get("accession") for f in processed],
    }


def main() -> int:
    report: dict[str, Any] = {
        "probe": "t0_probe_encode_accessions",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "encode_base": ENCODE,
        "note": "Metadata only — no large file downloads",
        "placeholder_checks": {},
        "pol2_chia_pet_k562": {},
        "hic_k562_loops": {},
        "usable_processed_bedpe_pol2": "uncertain",
        "usable_processed_bedpe_hic": "uncertain",
    }

    print("=== Placeholder accession checks ===")
    for acc in PLACEHOLDER_CHECK:
        summary = experiment_summary(acc)
        files = list_loopish_files(acc) if summary.get("exists") else []
        report["placeholder_checks"][acc] = {
            "experiment": summary,
            "loopish_files": files,
            "note": (
                "WRONG_TARGET_ESR1_not_POLR2A"
                if summary.get("exists") and summary.get("target_label") == "ESR1"
                else (
                    "NOT_FOUND"
                    if not summary.get("exists")
                    else "EXISTS_REVIEW_TARGET"
                )
            ),
        }
        print(
            acc,
            "exists=",
            summary.get("exists"),
            "target=",
            summary.get("target_label"),
            "assay=",
            summary.get("assay_title"),
        )

    print("\n=== Pol II / POLR2A ChIA-PET K562 search ===")
    pol2_exps = search_experiments("POLR2A ChIA-PET K562", limit=20)
    # Also RNAPII naming
    pol2_exps_b = search_experiments("RNAPII ChIA-PET K562", limit=10)
    seen = {e.get("accession") for e in pol2_exps if "accession" in e}
    for e in pol2_exps_b:
        if e.get("accession") not in seen:
            pol2_exps.append(e)

    pol2_detail = []
    for e in pol2_exps:
        acc = e.get("accession")
        if not acc or e.get("_error"):
            continue
        # Keep ChIA-PET-ish only
        title = (e.get("assay_title") or "") + " " + (e.get("assay_term_name") or "")
        if "ChIA-PET" not in title and "chia-pet" not in title.lower():
            # still record briefly
            continue
        files = list_loopish_files(acc)
        usable = classify_pol2_usable(files)
        row = {"experiment": e, "loopish_files": files, "usable": usable}
        pol2_detail.append(row)
        print(
            acc,
            e.get("assay_title"),
            "bedpe=",
            usable["has_bedpe"],
            usable["bedpe_accessions"][:5],
        )

    report["pol2_chia_pet_k562"] = {
        "search_hits": pol2_exps,
        "experiments_with_files": pol2_detail,
    }

    print("\n=== Hi-C K562 loop bedpe search ===")
    hic_files = search_loop_files("K562 Hi-C loops", limit=40)
    # Filter to loops output when possible
    hic_loops = [
        f
        for f in hic_files
        if isinstance(f, dict)
        and not f.get("_error")
        and "loop" in (f.get("output_type") or "").lower()
    ]
    report["hic_k562_loops"] = {
        "bedpe_search_hits": hic_files,
        "loop_output_files": hic_loops,
    }
    for f in hic_loops[:15]:
        print(
            f.get("accession"),
            f.get("output_type"),
            f.get("assembly"),
            f.get("dataset"),
            f.get("full_href"),
        )

    # Usability verdict
    any_pol2_bedpe = any(
        row["usable"]["has_bedpe"] for row in pol2_detail if "usable" in row
    )
    any_pol2_processed = any(
        row["usable"]["has_processed_loop_like"] for row in pol2_detail if "usable" in row
    )
    if any_pol2_bedpe:
        report["usable_processed_bedpe_pol2"] = "yes"
    elif any_pol2_processed:
        report["usable_processed_bedpe_pol2"] = "uncertain"  # bed/tsv loops, not bedpe
    else:
        report["usable_processed_bedpe_pol2"] = "no"

    if hic_loops:
        report["usable_processed_bedpe_hic"] = "yes"
    elif any(isinstance(f, dict) and f.get("accession") for f in hic_files):
        report["usable_processed_bedpe_hic"] = "uncertain"
    else:
        report["usable_processed_bedpe_hic"] = "no"

    # Recommended shortlist for claim.md VERIFY block
    recommended = {"pol2_chia_pet": [], "hic_loops": []}
    for row in pol2_detail:
        if row["usable"].get("has_bedpe"):
            recommended["pol2_chia_pet"].append(
                {
                    "experiment": row["experiment"].get("accession"),
                    "bedpe": row["usable"].get("bedpe_accessions"),
                    "href": row["experiment"].get("href"),
                }
            )
    for f in hic_loops[:10]:
        recommended["hic_loops"].append(
            {
                "file": f.get("accession"),
                "dataset": f.get("dataset"),
                "assembly": f.get("assembly"),
                "href": f.get("full_href"),
            }
        )
    report["recommended_shortlist"] = recommended

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT}")
    print(
        "usable_processed_bedpe_pol2=",
        report["usable_processed_bedpe_pol2"],
        "usable_processed_bedpe_hic=",
        report["usable_processed_bedpe_hic"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
