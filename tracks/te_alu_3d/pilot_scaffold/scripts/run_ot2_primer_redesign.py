#!/usr/bin/env python3
"""Redesign OT2 (KDM2B) amplicon primers — avoid Alu-like F / polyA.

Writes OT2b candidate, re-runs isPCR for OT2b, updates panel arts.
Does not authorize oligo order.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"

# CRISPOR OT hit (guide match)
OT_SITE = (121_534_383, 121_534_405)  # 1-based incl-ish span from desk panel
CHROM = "chr12"

# Avoid Alu-ish cores in primers
ALU_MOTIFS = (
    "AGTGAGC",
    "AGCCGAG",
    "TGAGCCG",
    "GAGGCTG",
    "GCCTGTA",
    "TTTTTT",
    "AAAAAA",
)

HEADER_RE = re.compile(
    r"(?P<chrom>chr[\w.]+):(?P<a>\d+)(?P<strand>[+-])(?P<b>\d+)(?:</[^>]+>)?\s+(?P<bp>\d+)\s*bp",
    re.I,
)


def fetch_seq(chrom: str, start0: int, end0: int) -> str:
    url = (
        "https://api.genome.ucsc.edu/getData/sequence"
        f"?genome=hg38;chrom={chrom};start={start0};end={end0}"
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        return (json.load(r).get("dna") or "").upper()


def rc(s: str) -> str:
    return s.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def gc(s: str) -> float:
    return 100.0 * (s.count("G") + s.count("C")) / len(s)


def tm_wallace(s: str) -> float:
    return 2 * (s.count("A") + s.count("T")) + 4 * (s.count("G") + s.count("C"))


def bad_primer(s: str) -> bool:
    if len(s) < 18 or len(s) > 25:
        return True
    if re.search(r"[^ACGT]", s):
        return True
    g = gc(s)
    if g < 30 or g > 75:
        return True
    t = tm_wallace(s)
    if t < 52 or t > 68:
        return True
    if any(m in s for m in ALU_MOTIFS):
        return True
    if re.search(r"(A{6}|T{6}|G{6}|C{6})", s):
        return True
    return False


def hg_pcr(fwd: str, rev: str, *, max_size: int = 1200) -> list[tuple]:
    params = {
        "db": "hg38",
        "wp_target": "genome",
        "wp_f": fwd,
        "wp_r": rev,
        "wp_size": str(max_size),
        "wp_perfect": "15",
        "wp_good": "15",
        "boolshad.wp_flipReverse": "0",
        "Submit": "submit",
    }
    url = "https://genome.ucsc.edu/cgi-bin/hgPcr?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", errors="replace")
    return HEADER_RE.findall(html)


def main() -> int:
    # Wide window so primers can sit outside Alu-dense OT neighborhood
    win0 = OT_SITE[0] - 800  # 1-based approx → use as 0-based-ish start
    win1 = OT_SITE[1] + 800
    start0 = win0 - 1
    seq = fetch_seq(CHROM, start0, win1)
    site_lo = OT_SITE[0] - 1 - start0
    site_hi = OT_SITE[1] - start0
    print(json.dumps({"seq_len": len(seq), "site_lo": site_lo, "site_hi": site_hi}))

    cands: list[tuple] = []
    # sample grid — keep OT site inside; polyA in body allowed but flagged
    for i in range(0, max(1, site_lo - 30), 12):
        for j in range(site_hi + 30, len(seq) - 18, 12):
            for plen in (19, 20, 21, 22):
                if i + plen > site_lo or j + plen > len(seq):
                    continue
                amp = (j + plen) - i
                if not (200 <= amp <= 600):
                    continue
                f = seq[i : i + plen]
                r = rc(seq[j : j + plen])
                if bad_primer(f) or bad_primer(r):
                    continue
                body = seq[i + plen : j]
                poly_body = bool(re.search(r"A{8,}|T{8,}", body))
                # prefer primers that start after the long polyA upstream of site
                poly_penalty = 50 if poly_body else 0
                # prefer F not overlapping known Alu cores in window
                score = abs(amp - 300) + abs(tm_wallace(f) - tm_wallace(r)) + poly_penalty
                cands.append((score, i, j, plen, f, r, amp, poly_body))

    cands = sorted(cands)[:60]
    print(json.dumps({"n_cands": len(cands)}))

    chosen = None
    tried = []
    for score, i, j, plen, f, r, amp, poly_body in cands:
        time.sleep(1.0)
        hits = hg_pcr(f, r, max_size=max(900, amp + 300))
        rec = {
            "fwd": f,
            "rev": r,
            "amp_bp": amp,
            "genomic_start0": start0 + i,
            "genomic_end0": start0 + j + plen,
            "polyA_or_T_in_amplicon_body": poly_body,
            "n_hits": len(hits),
            "hits": [{"chrom": h[0], "a": h[1], "strand": h[2], "b": h[3], "bp": h[4]} for h in hits[:5]],
        }
        tried.append(rec)
        print(json.dumps({"try": f, "n_hits": len(hits), "poly_body": poly_body}))
        if len(hits) == 1 and hits[0][0].lower() == "chr12":
            a, b = int(hits[0][1]), int(hits[0][3])
            lo, hi = min(a, b), max(a, b)
            if lo <= OT_SITE[0] <= hi and lo <= OT_SITE[1] <= hi:
                chosen = {**rec, "ispcr_product": hits[0]}
                break
        if len(tried) >= 20:
            break

    out = {
        "status": "OT2_REDESIGN_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "old_ot2": {
            "fwd": "AGCTTGCAGTGAGCCGAGA",
            "rev": "GGGAAGGTGAGTTTCAGTTG",
            "verdict": "ISPCR_NONE_Alu_like_F",
        },
        "ot2b": chosen,
        "tried_n": len(tried),
        "tried": tried,
        "oligo_order": "FORBIDDEN",
    }
    (OUT / "OT2_KDM2B_primer_redesign_v1.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if chosen:
        a = int(chosen["ispcr_product"][1])
        b = int(chosen["ispcr_product"][3])
        lo, hi = min(a, b), max(a, b)
        md = f"""# OT2 (KDM2B) primer redesign v1

**Date:** 2026-07-16
**Status:** `OT2B_DESK_READY`
**Old OT2:** ISPCR_NONE (Alu-like F `AGCTTGCAGTGAGCCGAGA`)
**New ID:** **OT2b**
**Oligo order:** FORBIDDEN until A1 GO + optional NCBI Primer-BLAST

## OT2b

| Field | Value |
|-------|-------|
| Forward | `{chosen['fwd']}` |
| Reverse | `{chosen['rev']}` |
| isPCR product | chr12:{lo}-{hi} ({chosen['amp_bp']} bp design / {chosen['ispcr_product'][4]} bp reported) |
| Covers OT site | chr12:{OT_SITE[0]}-{OT_SITE[1]} |
| UCSC products | **1** |

## What this does NOT mean

- Not wet PCR validation
- Not A1 GO
- Not NCBI Primer-BLAST complete

JSON: `OT2_KDM2B_primer_redesign_v1.json`
"""
        label = "OT2B_READY"
    else:
        md = f"""# OT2 (KDM2B) primer redesign v1

**Date:** 2026-07-16
**Status:** `OT2_REDESIGN_FAILED_DESK`
**Tried:** {len(tried)} candidates (Alu/polyA filters + UCSC isPCR)
**Result:** no single-product pair covering KDM2B OT site in this pass

## Next options

1. Manual Primer3 + NCBI Primer-BLAST on chr12:{OT_SITE[0]-500}-{OT_SITE[1]+500}
2. Drop KDM2B from minimum OT panel (keep as watchlist only) — requires claim amendment
3. Use longer amplicon / different flanking unique sequence

JSON: `OT2_KDM2B_primer_redesign_v1.json`
"""
        label = "OT2_REDESIGN_FAILED"

    (OUT / "OT2_KDM2B_primer_redesign_v1.md").write_text(md, encoding="utf-8")
    print(json.dumps({"label": label, "chosen": bool(chosen)}, indent=2))
    return 0 if chosen else 1


if __name__ == "__main__":
    raise SystemExit(main())
