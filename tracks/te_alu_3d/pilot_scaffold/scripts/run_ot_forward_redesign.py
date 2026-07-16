#!/usr/bin/env python3
"""Redesign OT2b and OT3 forward primers for BLAT-unique singles + isPCR pair OK.

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

TARGETS = [
    {
        "id": "OT2c",
        "replaces": "OT2b",
        "chrom": "chr12",
        "ot_site": (121_534_383, 121_534_405),
        "old_rev": "ATGTTTTCCGGGGTGGGAAGG",  # keep if possible
        "win_pad": 900,
    },
    {
        "id": "OT3b",
        "replaces": "OT3",
        "chrom": "chr1",
        "ot_site": (92_388_950, 92_388_972),  # RPAP2 exon OT from panel ~92388950-72
        "old_rev": "ATTATCGGAGCTTGAACGCG",
        "win_pad": 700,
    },
]

ALU_MOTIFS = ("AGTGAGC", "AGCCGAG", "TGAGCCG", "GAGGCTG", "GCCTGTA", "AGTCCCA", "TTTTTT", "AAAAAA")
HEADER_RE = re.compile(
    r"(?P<chrom>chr[\w.]+):(?P<a>\d+)(?P<strand>[+-])(?P<b>\d+)(?:</[^>]+>)?\s+(?P<bp>\d+)\s*bp",
    re.I,
)
PSL_RE = re.compile(
    r"^(?P<matches>\d+)\t(?P<misMatches>\d+)\t(?P<repMatches>\d+)\t(?P<nCount>\d+)\t"
    r"(?P<qNumInsert>\d+)\t(?P<qBaseInsert>\d+)\t(?P<tNumInsert>\d+)\t(?P<tBaseInsert>\d+)\t"
    r"(?P<strand>[+-])\t(?P<qName>\S+)\t(?P<qSize>\d+)\t(?P<qStart>\d+)\t(?P<qEnd>\d+)\t"
    r"(?P<tName>\S+)\t(?P<tSize>\d+)\t(?P<tStart>\d+)\t(?P<tEnd>\d+)\t",
    re.M,
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
    if not (19 <= len(s) <= 23):
        return True
    if re.search(r"[^ACGT]", s):
        return True
    g = gc(s)
    if g < 35 or g > 70:
        return True
    t = tm_wallace(s)
    if t < 54 or t > 66:
        return True
    if any(m in s for m in ALU_MOTIFS):
        return True
    if re.search(r"(A{5}|T{5}|G{5}|C{5})", s):
        return True
    return False


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", errors="replace")


def blat_n_strong(seq: str) -> int:
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
    text = _get("https://genome.ucsc.edu/cgi-bin/hgBlat?" + params)
    n = 0
    for m in PSL_RE.finditer(text):
        matches = int(m.group("matches"))
        mism = int(m.group("misMatches"))
        qsize = int(m.group("qSize"))
        qstart, qend = int(m.group("qStart")), int(m.group("qEnd"))
        tname = m.group("tName")
        denom = matches + mism
        pct = 100.0 * matches / denom if denom else 0.0
        cov = 100.0 * (qend - qstart) / qsize if qsize else 0.0
        if pct >= 95 and cov >= 90 and tname.startswith("chr"):
            n += 1
    return n


def ispcr(fwd: str, rev: str, max_size: int = 1200) -> list[tuple]:
    params = urllib.parse.urlencode(
        {
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
    )
    html = _get("https://genome.ucsc.edu/cgi-bin/hgPcr?" + params)
    return HEADER_RE.findall(html)


def redesign_one(t: dict) -> dict | None:
    ot0, ot1 = t["ot_site"]
    pad = t["win_pad"]
    start0 = ot0 - pad - 1
    end0 = ot1 + pad
    seq = fetch_seq(t["chrom"], start0, end0)
    site_lo = ot0 - 1 - start0
    site_hi = ot1 - start0

    # Prefer keeping old reverse if it sits in window
    old_rev = t["old_rev"]
    old_rev_rc = rc(old_rev)
    rev_j = seq.find(old_rev_rc)
    rev_candidates: list[tuple[int, str]] = []
    if rev_j >= site_hi:
        rev_candidates.append((rev_j, old_rev))
    # also sample new reverses downstream
    for j in range(site_hi + 40, len(seq) - 20, 18):
        for plen in (20, 21):
            r = rc(seq[j : j + plen])
            if not bad_primer(r):
                rev_candidates.append((j, r))
    # unique by seq
    seen_r = set()
    revs = []
    for j, r in rev_candidates:
        if r in seen_r:
            continue
        seen_r.add(r)
        revs.append((j, r))
        if len(revs) >= 12:
            break

    tried = []
    for i in range(0, max(1, site_lo - 30), 14):
        for plen in (20, 21, 22):
            if i + plen > site_lo:
                continue
            f = seq[i : i + plen]
            if bad_primer(f):
                continue
            time.sleep(0.7)
            n_f = blat_n_strong(f)
            if n_f == 0 or n_f > 3:
                tried.append({"fwd": f, "blat_f": n_f, "status": "skip_blat_f"})
                continue
            for j, r in revs:
                if j <= i + plen:
                    continue
                amp = (j + len(r)) - i  # approx
                # better amp from genomic indices
                amp = (j + len(rc(r))) - i if False else (j + len(r)) - i
                # r was built as rc(seq[j:j+plen_r]); genomic end = j + len(rc(r))? 
                # Actually r = rc(seq[j:j+plen]); genomic segment length = plen = len(r)
                amp_bp = (j + len(r)) - i
                if not (200 <= amp_bp <= 550):
                    continue
                time.sleep(0.9)
                n_r = blat_n_strong(r)
                if n_r == 0 or n_r > 3:
                    continue
                hits = ispcr(f, r, max_size=max(900, amp_bp + 200))
                rec = {
                    "fwd": f,
                    "rev": r,
                    "blat_f": n_f,
                    "blat_r": n_r,
                    "n_ispcr": len(hits),
                    "ispcr": hits[:3],
                    "amp_bp": amp_bp,
                    "genomic_start0": start0 + i,
                    "genomic_end0": start0 + j + len(r),
                }
                tried.append(rec)
                print(json.dumps({"id": t["id"], "fwd": f, "blat_f": n_f, "blat_r": n_r, "ispcr": len(hits)}))
                if len(hits) != 1:
                    continue
                if hits[0][0].lower() != t["chrom"].lower():
                    continue
                a, b = int(hits[0][1]), int(hits[0][3])
                lo, hi = min(a, b), max(a, b)
                if lo <= ot0 <= hi and lo <= ot1 <= hi:
                    return {"chosen": rec, "tried_n": len(tried), "tried_tail": tried[-8:]}
                if len(tried) >= 25:
                    return {"chosen": None, "tried_n": len(tried), "tried_tail": tried[-8:]}
    return {"chosen": None, "tried_n": len(tried), "tried_tail": tried[-8:]}


def main() -> int:
    results = {}
    all_ok = True
    for t in TARGETS:
        print(json.dumps({"start": t["id"]}))
        out = redesign_one(t)
        results[t["id"]] = {"replaces": t["replaces"], "ot_site": t["ot_site"], **(out or {})}
        if not out or not out.get("chosen"):
            all_ok = False

    payload = {
        "status": "OT_FORWARD_REDESIGN_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "label": "OT_F_REDESIGN_PASS" if all_ok else "OT_F_REDESIGN_PARTIAL",
        "oligo_order": "FORBIDDEN",
        "results": results,
    }
    (OUT / "OT_forward_redesign_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    lines = ["# OT forward-primer redesign v1 (BLAT-unique singles)", "", f"**Label:** `{payload['label']}`", "**Oligo order:** FORBIDDEN", ""]
    for tid, block in results.items():
        ch = block.get("chosen")
        lines.append(f"## {tid} (replaces {block.get('replaces')})")
        if not ch:
            lines.append("- **FAILED** in this pass")
        else:
            lines.append(f"- F `{ch['fwd']}` (BLAT n={ch['blat_f']})")
            lines.append(f"- R `{ch['rev']}` (BLAT n={ch['blat_r']})")
            lines.append(f"- isPCR products: **{ch['n_ispcr']}** · amp≈{ch['amp_bp']} bp")
            if ch.get("ispcr"):
                h = ch["ispcr"][0]
                lines.append(f"- product: {h[0]}:{h[1]}-{h[3]} ({h[4]} bp)")
        lines.append("")
    lines.append("JSON: `OT_forward_redesign_v1.json`")
    (OUT / "OT_forward_redesign_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"label": payload["label"], "ok": all_ok}, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
