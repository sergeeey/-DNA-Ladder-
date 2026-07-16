#!/usr/bin/env python3
"""Desk primer genomic uniqueness via UCSC BLAT (hg38 PSL), NCBI optional.

Does not authorize oligo order. Complements UCSC isPCR pair check.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"

PRIMERS = [
    {"pair": "OT0", "role": "fwd", "seq": "TTTCTCCTAGGTCACACCCA"},
    {"pair": "OT0", "role": "rev", "seq": "TTAGGGAGTTCTCGAAGTGG"},
    {"pair": "OT1", "role": "fwd", "seq": "AGGTCCCCAGGAGAGAGGT"},
    {"pair": "OT1", "role": "rev", "seq": "TCTTGTCACCCAGATGAGCT"},
    {"pair": "OT2c", "role": "fwd", "seq": "CTCGAGAGCTGAGGTGGGAA"},
    {"pair": "OT2c", "role": "rev", "seq": "ATCTCTAGCTGTTTGTGTGG"},
    {"pair": "OT3b", "role": "fwd", "seq": "TAGCCCACAGAGGGTTAGCC"},
    {"pair": "OT3b", "role": "rev", "seq": "ATTATCGGAGCTTGAACGCG"},
    {"pair": "OT4", "role": "fwd", "seq": "TGAGCCAGAGTTCATGGTCA"},
    {"pair": "OT4", "role": "rev", "seq": "TTGGAACTGAGAACCCCTGA"},
]

UA = {"User-Agent": "Mozilla/5.0"}
# PSL line starts with integers
PSL_RE = re.compile(
    r"^(?P<matches>\d+)\t(?P<misMatches>\d+)\t(?P<repMatches>\d+)\t(?P<nCount>\d+)\t"
    r"(?P<qNumInsert>\d+)\t(?P<qBaseInsert>\d+)\t(?P<tNumInsert>\d+)\t(?P<tBaseInsert>\d+)\t"
    r"(?P<strand>[+-])\t(?P<qName>\S+)\t(?P<qSize>\d+)\t(?P<qStart>\d+)\t(?P<qEnd>\d+)\t"
    r"(?P<tName>\S+)\t(?P<tSize>\d+)\t(?P<tStart>\d+)\t(?P<tEnd>\d+)\t",
    re.M,
)


def _get(url: str, timeout: int = 120) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def ucsc_blat_psl(seq: str) -> dict:
    params = urllib.parse.urlencode(
        {
            "org": "Human",
            "db": "hg38",
            "type": "DNA",
            "sort": "query,score",
            "output": "psl",
            "userSeq": seq,
        }
    )
    url = "https://genome.ucsc.edu/cgi-bin/hgBlat?" + params
    try:
        text = _get(url, timeout=120)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "engine": "ucsc_hgBlat_hg38"}

    hits = []
    for m in PSL_RE.finditer(text):
        matches = int(m.group("matches"))
        mism = int(m.group("misMatches"))
        qsize = int(m.group("qSize"))
        qstart = int(m.group("qStart"))
        qend = int(m.group("qEnd"))
        tname = m.group("tName")
        tstart = int(m.group("tStart"))
        tend = int(m.group("tEnd"))
        denom = matches + mism
        pct_id = 100.0 * matches / denom if denom else 0.0
        cov = 100.0 * (qend - qstart) / qsize if qsize else 0.0
        if pct_id >= 95 and cov >= 90 and tname.startswith("chr"):
            hits.append(
                {
                    "chrom": tname,
                    "start": tstart,
                    "end": tend,
                    "strand": m.group("strand"),
                    "pct_identity": round(pct_id, 1),
                    "query_coverage": round(cov, 1),
                    "matches": matches,
                    "mismatches": mism,
                }
            )
    return {
        "ok": True,
        "engine": "ucsc_hgBlat_hg38_psl",
        "hits": hits,
        "n_strong": len(hits),
    }


def label_primer(n_strong: int | None, ok: bool) -> str:
    if not ok or n_strong is None:
        return "BLAST_FAIL"
    if n_strong <= 3:
        return "BLAST_OK"
    if n_strong <= 10:
        return "BLAST_WARN"
    return "BLAST_MULTI"


def panel_label(rows: list[dict]) -> str:
    labs = [r["label"] for r in rows]
    if labs.count("BLAST_FAIL") >= max(1, len(labs) // 2):
        return "NCBI_DESK_BLOCKED"
    if any(x == "BLAST_MULTI" for x in labs):
        return "NCBI_DESK_REDESIGN"
    if any(x in ("BLAST_WARN", "BLAST_FAIL") for x in labs):
        return "NCBI_DESK_GAPS"
    return "NCBI_DESK_PASS"


def main() -> int:
    rows = []
    for p in PRIMERS:
        time.sleep(0.8)
        res = ucsc_blat_psl(p["seq"])
        n = res.get("n_strong") if res.get("ok") else None
        lab = label_primer(n, bool(res.get("ok")))
        rows.append(
            {
                **p,
                "label": lab,
                "n_strong_hits": n,
                "top_hits": (res.get("hits") or [])[:8],
                "engine": res.get("engine"),
                "error": res.get("error"),
            }
        )
        print(
            json.dumps(
                {
                    "pair": p["pair"],
                    "role": p["role"],
                    "label": lab,
                    "n": n,
                    "top": [
                        f"{h['chrom']}:{h['start']}-{h['end']}"
                        for h in (res.get("hits") or [])[:3]
                    ],
                }
            )
        )

    label = panel_label(rows)
    # rename panel labels for honesty (BLAT primary)
    label_map = {
        "NCBI_DESK_PASS": "PRIMER_BLAT_DESK_PASS",
        "NCBI_DESK_GAPS": "PRIMER_BLAT_DESK_GAPS",
        "NCBI_DESK_REDESIGN": "PRIMER_BLAT_DESK_REDESIGN",
        "NCBI_DESK_BLOCKED": "PRIMER_BLAT_DESK_BLOCKED",
    }
    label = label_map.get(label, label)

    payload = {
        "status": "PRIMER_BLAT_DESK_COMPLETE",
        "label": label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "PRIMER_NCBI_BLAST_CLAIM_v1.md",
        "engine_primary": "ucsc_hgBlat_hg38_psl",
        "ncbi_note": "NCBI Primer-BLAST UI / blastn-short skipped or flaky (502); BLAT used as desk uniqueness",
        "oligo_order": "FORBIDDEN",
        "rows": rows,
    }
    (OUT / "PRIMER_NCBI_BLAST_desk_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    table = []
    for r in rows:
        tops = "; ".join(
            f"{h['chrom']}:{h['start']}-{h['end']} ({h['pct_identity']}%)"
            for h in (r.get("top_hits") or [])[:3]
        ) or "—"
        table.append(
            f"| {r['pair']} | {r['role']} | `{r['seq']}` | **{r['label']}** | "
            f"{r['n_strong_hits'] if r['n_strong_hits'] is not None else '—'} | {tops} |"
        )

    md = f"""# Primer genomic uniqueness desk v1 (UCSC BLAT)

**Date:** 2026-07-16
**Status:** `PRIMER_BLAT_DESK_COMPLETE`
**Claim:** `PRIMER_NCBI_BLAST_CLAIM_v1.md`
**Label:** **`{label}`**
**Engine:** UCSC hgBlat hg38 (PSL) — NCBI blastn-short was flaky (HTTP 502)
**Oligo order:** FORBIDDEN

## Results (per primer)

| Pair | Role | Sequence | Label | n strong | Top hits |
|------|------|----------|-------|---------:|----------|
{chr(10).join(table)}

## Reading

- Strong hit: ≥95% identity and ≥90% query coverage on a `chr*` target
- Complements UCSC **isPCR** (pair products already checked)
- Interactive NCBI Primer-BLAST UI remains optional lab SOP confirm

## Plain language

Одиночные праймеры прогнаны через BLAT по hg38. Это desk-уникальность, не заказ олиго.

Full dump: `PRIMER_NCBI_BLAST_desk_v1.json`
"""
    (OUT / "PRIMER_NCBI_BLAST_desk_v1.md").write_text(md, encoding="utf-8")
    print(json.dumps({"label": label, "n_rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
