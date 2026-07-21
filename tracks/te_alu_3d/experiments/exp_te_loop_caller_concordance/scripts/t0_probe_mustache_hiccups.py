#!/usr/bin/env python3
"""T0 probe: K562 Mustache vs HiCCUPS processed loop bedpe (C-F1).

Writes data/t0_accession_probe.json. Terminal BLOCKED_DATA if no Mustache bedpe.
Does NOT download bulky files unless a Mustache accession is frozen.
"""

from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent.parent / "data" / "t0_accession_probe.json"
USER_AGENT = "DNA-Ladder-C-F1-T0/1.0"
HICCUPS = "ENCFF693XIL"


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def get_json(url: str, timeout: int = 90) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as resp:
        return json.load(resp)


def file_detail(acc: str) -> dict[str, Any]:
    f = get_json(f"https://www.encodeproject.org/files/{acc}/?format=json")
    aliases = f.get("aliases") or []
    alias_blob = " ".join(aliases).lower()
    caller = "unknown"
    if "mustache" in alias_blob:
        caller = "Mustache"
    elif "hiccups" in alias_blob or "call-hiccups" in alias_blob:
        caller = "HiCCUPS"
    elif "delta" in alias_blob or "call-delta" in alias_blob:
        caller = "DELTA"
    elif "localizer" in alias_blob:
        caller = "localizer"
    return {
        "accession": acc,
        "output_type": f.get("output_type"),
        "file_format": f.get("file_format"),
        "assembly": f.get("assembly"),
        "dataset": f.get("dataset"),
        "preferred_default": f.get("preferred_default"),
        "aliases": aliases,
        "caller_inferred_from_alias": caller,
        "href": f.get("href"),
        "md5sum": f.get("md5sum"),
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    loops_url = (
        "https://www.encodeproject.org/search/?type=File&file_format=bedpe"
        "&biosample_ontology.term_name=K562&assembly=GRCh38&status=released"
        "&output_type=loops&format=json&limit=all"
    )
    data = get_json(loops_url)
    graph = data.get("@graph") or []
    details = []
    for row in graph:
        acc = row.get("accession")
        if not acc:
            continue
        try:
            details.append(file_detail(acc))
        except Exception as exc:  # noqa: BLE001
            details.append({"accession": acc, "error": str(exc)})

    mustache = [
        d
        for d in details
        if d.get("caller_inferred_from_alias") == "Mustache"
        or "mustache" in json.dumps(d).lower()
    ]
    hiccups = [d for d in details if d.get("accession") == HICCUPS]
    # Software object search (may 404 on some portals)
    software_probe: dict[str, Any]
    try:
        soft = get_json(
            "https://www.encodeproject.org/search/?type=Software&format=json"
            "&limit=all&field=name&field=title&field=status"
        )
        must_soft = [
            x
            for x in (soft.get("@graph") or [])
            if "mustache" in json.dumps(x).lower()
        ]
        software_probe = {"ok": True, "n_mustache_software": len(must_soft), "hits": must_soft}
    except Exception as exc:  # noqa: BLE001
        software_probe = {"ok": False, "error": str(exc)}

    verdict = "BLOCKED_DATA" if not mustache else "PASS_FREEZE_CANDIDATE"
    report = {
        "experiment": "exp_te_loop_caller_concordance",
        "candidate_id": "C-F1",
        "probed_at_utc": datetime.now(timezone.utc).isoformat(),
        "hiccups_target": HICCUPS,
        "hiccups_files": hiccups,
        "k562_grch38_loop_bedpe_n": len(details),
        "k562_grch38_loop_bedpe": details,
        "mustache_hits": mustache,
        "software_probe": software_probe,
        "verdict": verdict,
        "note": (
            "No K562 GRCh38 Mustache processed loop bedpe on ENCODE; "
            "HiCCUPS ENCFF693XIL present. Do not substitute DELTA as Mustache."
            if not mustache
            else "Mustache accession(s) found — freeze before ΔJaccard."
        ),
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"verdict": verdict, "n_loops": len(details), "n_mustache": len(mustache), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
