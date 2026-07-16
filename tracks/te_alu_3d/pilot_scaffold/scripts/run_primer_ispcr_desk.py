#!/usr/bin/env python3
"""Desk in-silico PCR uniqueness for OT amplicon primer pairs (UCSC hgPcr).

Does not authorize oligo order. Complements (does not replace) NCBI Primer-BLAST.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"

PAIRS = [
    {
        "id": "OT0",
        "locus": "C1_on_target",
        "expected_chrom": "chr11",
        "expected_start": 62_753_823,
        "expected_end": 62_754_058,
        "fwd": "TTTCTCCTAGGTCACACCCA",
        "rev": "TTAGGGAGTTCTCGAAGTGG",
        "flag": "edit_verify",
    },
    {
        "id": "OT1",
        "locus": "RADIL_exon",
        "expected_chrom": "chr7",
        "expected_start": 4_805_443,
        "expected_end": 4_805_729,
        "fwd": "AGGTCCCCAGGAGAGAGGT",
        "rev": "TCTTGTCACCCAGATGAGCT",
        "flag": "priority_watch",
    },
    {
        "id": "OT2",
        "locus": "KDM2B_intron_DEPRECATED",
        "expected_chrom": "chr12",
        "expected_start": 121_534_283,
        "expected_end": 121_534_502,
        "fwd": "AGCTTGCAGTGAGCCGAGA",
        "rev": "GGGAAGGTGAGTTTCAGTTG",
        "flag": "DEPRECATED_Alu_like_ISPCR_NONE",
        "skip": True,
    },
    {
        "id": "OT2b",
        "locus": "KDM2B_intron",
        "expected_chrom": "chr12",
        "expected_start": 121_534_219,
        "expected_end": 121_534_516,
        "fwd": "GGCACTTGTAGTCCCAGCTAC",
        "rev": "ATGTTTTCCGGGGTGGGAAGG",
        "flag": "redesign_v1_polyA_in_body",
    },
    {
        "id": "OT3",
        "locus": "RPAP2_exon",
        "expected_chrom": "chr1",
        "expected_start": 92_388_850,
        "expected_end": 92_389_070,
        "fwd": "CGGTTCTATGCTCACAGTGT",
        "rev": "ATTATCGGAGCTTGAACGCG",
        "flag": "",
    },
    {
        "id": "OT4",
        "locus": "UPF3A_intron",
        "expected_chrom": "chr13",
        "expected_start": 114_290_091,
        "expected_end": 114_290_332,
        "fwd": "TGAGCCAGAGTTCATGGTCA",
        "rev": "TTGGAACTGAGAACCCCTGA",
        "flag": "",
    },
]

# fasta header like: >chr11:62753823+62754058 236bp TTTC... TTAA...
HEADER_RE = re.compile(
    r"(?P<chrom>chr[\w.]+):(?P<a>\d+)(?P<strand>[+-])(?P<b>\d+)(?:</[^>]+>)?\s+(?P<bp>\d+)\s*bp",
    re.I,
)


def hg_pcr(fwd: str, rev: str, *, max_size: int = 1000, perfect: int = 15, good: int = 15) -> str:
    params = {
        "org": "Human",
        "db": "hg38",
        "wp_target": "genome",
        "wp_f": fwd,
        "wp_r": rev,
        "wp_size": str(max_size),
        "wp_perfect": str(perfect),
        "wp_good": str(good),
        "boolshad.wp_flipReverse": "0",
        "Submit": "submit",
    }
    url = "https://genome.ucsc.edu/cgi-bin/hgPcr?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_products(html: str) -> list[dict]:
    products = []
    # Headers live inside <PRE> as: >...<A>chr11:start+end</A> Nbp FWD REV
    for m in HEADER_RE.finditer(html):
        a, b = int(m.group("a")), int(m.group("b"))
        start, end = min(a, b), max(a, b)
        products.append(
            {
                "chrom": m.group("chrom"),
                "start": start,
                "end": end,
                "strand": m.group("strand"),
                "bp": int(m.group("bp")),
            }
        )
    uniq = []
    seen = set()
    for p in products:
        key = (p["chrom"], p["start"], p["end"], p["strand"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def overlaps(p: dict, chrom: str, start: int, end: int, pad: int = 50) -> bool:
    if p["chrom"].lower() != chrom.lower():
        return False
    return not (p["end"] < start - pad or p["start"] > end + pad)


def label_pair(pair: dict, products: list[dict], err: str | None) -> str:
    if err:
        return "ISPCR_FAIL"
    if not products:
        return "ISPCR_NONE"
    if len(products) >= 2:
        return "ISPCR_MULTI"
    p0 = products[0]
    ok_loc = overlaps(p0, pair["expected_chrom"], pair["expected_start"], pair["expected_end"])
    exp_len = pair["expected_end"] - pair["expected_start"] + 1
    len_ok = abs(p0["bp"] - exp_len) <= 40
    flag = pair.get("flag") or ""
    if ok_loc and len_ok and "polyA" not in flag:
        return "ISPCR_PASS"
    if ok_loc:
        return "ISPCR_WARN"
    return "ISPCR_WARN"


def panel_label(rows: list[dict]) -> str:
    labs = [r["label"] for r in rows if not str(r["label"]).startswith("ISPCR_SKIP")]
    if any(x == "ISPCR_FAIL" for x in labs):
        return "PRIMER_DESK_BLOCKED" if all(x == "ISPCR_FAIL" for x in labs) else "PRIMER_DESK_GAPS"
    if any(x in ("ISPCR_MULTI", "ISPCR_NONE") for x in labs):
        return "PRIMER_DESK_REDESIGN"
    if any(x == "ISPCR_WARN" for x in labs):
        return "PRIMER_DESK_GAPS"
    return "PRIMER_DESK_PASS"


def main() -> int:
    rows = []
    for pair in PAIRS:
        if pair.get("skip"):
            rows.append(
                {
                    **{k: v for k, v in pair.items() if k != "skip"},
                    "n_products": None,
                    "products": [],
                    "label": "ISPCR_SKIP_DEPRECATED",
                    "error": None,
                }
            )
            continue
        err = None
        products: list[dict] = []
        try:
            html = hg_pcr(pair["fwd"], pair["rev"])
            products = parse_products(html)
        except Exception as exc:  # noqa: BLE001
            err = str(exc)
        lab = label_pair(pair, products, err)
        rows.append(
            {
                **{k: v for k, v in pair.items() if k != "skip"},
                "n_products": len(products),
                "products": products,
                "label": lab,
                "error": err,
                "manual_primer_blast_url": (
                    "https://www.ncbi.nlm.nih.gov/tools/primer-blast/"
                    "?LINK_LOC=BlastHomeAd"
                ),
                "ucsc_ispcr_hint": f"hg38 F={pair['fwd']} R={pair['rev']}",
            }
        )

    label = panel_label(rows)
    payload = {
        "status": "PRIMER_ISPCR_DESK_COMPLETE",
        "label": label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "PRIMER_ISPCR_CLAIM_v1.md",
        "engine": "UCSC_hgPcr_hg38",
        "ncbi_primer_blast": "STILL_RECOMMENDED_MANUAL_CONFIRM",
        "oligo_order": "FORBIDDEN",
        "rows": rows,
    }
    (OUT / "PRIMER_ISPCR_desk_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    table = []
    for r in rows:
        locs = "; ".join(f"{p['chrom']}:{p['start']}-{p['end']}({p['bp']}bp)" for p in r["products"]) or "—"
        table.append(
            f"| {r['id']} | {r['locus']} | **{r['label']}** | {r['n_products']} | {locs} | {r.get('flag') or '—'} |"
        )

    md = f"""# Primer in-silico PCR desk v1

**Date:** 2026-07-16
**Status:** `PRIMER_ISPCR_DESK_COMPLETE`
**Claim:** `PRIMER_ISPCR_CLAIM_v1.md`
**Label:** **`{label}`**
**Engine:** UCSC hgPcr hg38
**Oligo order:** FORBIDDEN
**NCBI Primer-BLAST:** still recommended as human confirm before A1 order

## Results

| ID | Locus | Label | n products | Products | Flag |
|----|-------|-------|----------:|----------|------|
{chr(10).join(table)}

## Reading

- **ISPCR_PASS** — single product at expected locus
- **ISPCR_WARN** — single product with soft mismatch and/or polyA flag (OT2)
- **ISPCR_MULTI / NONE** — redesign before order
- UCSC isPCR ≠ full NCBI Primer-BLAST sensitivity

## Manual confirm slots (optional)

| ID | NCBI Primer-BLAST done? | Notes |
|----|:-----------------------:|-------|
| OT0 | ☐ | |
| OT1 | ☐ | RADIL |
| OT2 | ☐ | polyA — redesign if PCR poor |
| OT3 | ☐ | |
| OT4 | ☐ | |

## Plain language

Проверили, не даёт ли пара праймеров кучу продуктов по hg38. Это desk-фильтр до A1, не разрешение заказывать олиго.

## What this does NOT mean

- Not A1 GO
- Not wet PCR validation
- Not replacement for NCBI Primer-BLAST if lab SOP requires it

Full dump: `PRIMER_ISPCR_desk_v1.json`
"""
    (OUT / "PRIMER_ISPCR_desk_v1.md").write_text(md, encoding="utf-8")
    print(json.dumps({"label": label, "rows": [(r["id"], r["label"], r["n_products"]) for r in rows]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
