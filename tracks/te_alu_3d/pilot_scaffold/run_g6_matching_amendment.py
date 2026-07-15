"""Desk: GC matching already in g6_gc_matching.json; add K562 ATAC peak overlap for C1/N/C3."""

from __future__ import annotations

import gzip
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "cultivation"
OUT = ROOT.parent / "09_outputs" / "prospective"

SITES = {
    "C1": 62753923,
    "N1": 35821778,
    "N2": 35822097,
    "N3": 108009167,
    "C3": 72434037,
}


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    search = (
        "https://www.encodeproject.org/search/"
        "?type=File&file_format=bed&output_type=replicated+peaks&assembly=GRCh38"
        "&biosample_ontology.term_name=K562&assay_title=ATAC-seq"
        "&status=released&format=json&limit=10"
    )
    files = get_json(search).get("@graph") or []
    if not files:
        search = (
            "https://www.encodeproject.org/search/"
            "?type=File&file_format=bed&assembly=GRCh38"
            "&biosample_ontology.term_name=K562&assay_title=ATAC-seq"
            "&status=released&format=json&limit=10"
        )
        files = [
            f
            for f in (get_json(search).get("@graph") or [])
            if "peak" in str(f.get("output_type", "")).lower()
        ]
    pick = next((f for f in files if f.get("preferred_default")), None)
    if pick is None and files:
        pick = sorted(files, key=lambda x: x.get("file_size") or 10**18)[0]
    if pick is None:
        raise SystemExit("no K562 ATAC bed found")

    acc = pick["accession"]
    dest = DATA / f"{acc}_K562_ATAC.bed.gz"
    if not dest.exists() or dest.stat().st_size < 1000:
        href = "https://www.encodeproject.org" + pick["href"]
        print("download", acc)
        req = urllib.request.Request(href, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180) as r, dest.open("wb") as out:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                out.write(chunk)

    # load chr11 peaks only
    peaks: list[tuple[int, int]] = []
    opener = gzip.open if dest.suffix == ".gz" or dest.name.endswith(".gz") else open
    with opener(dest, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#") or line.startswith("track"):
                continue
            p = line.split("\t")
            if len(p) < 3:
                continue
            if p[0] not in ("chr11", "11"):
                continue
            peaks.append((int(p[1]), int(p[2])))
    peaks.sort()
    print("chr11_atac_peaks", len(peaks))

    def in_peak(pos: int, pad: int = 0) -> tuple[bool, int]:
        best = 10**12
        hit = False
        for s, e in peaks:
            if s - pad <= pos < e + pad:
                hit = True
            best = min(best, abs(pos - s), abs(pos - e), abs(pos - (s + e) // 2))
        return hit, int(best)

    gc_doc = json.loads((OUT / "g6_gc_matching.json").read_text(encoding="utf-8"))
    access_rows = []
    for name, pos in SITES.items():
        hit0, d0 = in_peak(pos, 0)
        hit250, d250 = in_peak(pos, 250)
        access_rows.append(
            {
                "id": name,
                "pos": pos,
                "in_K562_ATAC_peak": hit0,
                "within_250bp_ATAC": hit250,
                "dist_ATAC_peak": d0,
            }
        )

    # matching grade vs C1
    c1 = next(r for r in access_rows if r["id"] == "C1")
    for r in access_rows:
        r["access_match_vs_C1"] = (
            "MATCH"
            if r["in_K562_ATAC_peak"] == c1["in_K562_ATAC_peak"]
            else "MISMATCH"
        )

    # GC match grades
    gc_by = {}
    for r in gc_doc["rows"]:
        gc_by[(r["id"], r["window"])] = r
    gc_grades = []
    for name in SITES:
        if name == "C1":
            continue
        d100 = abs(gc_by[(name, "w201")]["gc_delta_vs_C1"])
        d1k = abs(gc_by[(name, "w2001")]["gc_delta_vs_C1"])
        # thresholds desk: |ΔGC|<=0.05 tight; <=0.10 ok; else poor
        grade = (
            "TIGHT"
            if d100 <= 0.05 and d1k <= 0.05
            else "OK"
            if d100 <= 0.10 and d1k <= 0.12
            else "POOR"
        )
        gc_grades.append(
            {
                "id": name,
                "abs_delta_gc_201": d100,
                "abs_delta_gc_2001": d1k,
                "gc_match_grade": grade,
            }
        )

    report = {
        "status": "G6_MATCHING_AMENDMENT_COMPLETE",
        "atac_file": acc,
        "atac_path": str(dest.relative_to(ROOT)),
        "caveat": "K562 ATAC proxy — not HUDEP-2",
        "access_rows": access_rows,
        "gc_grades": gc_grades,
        "neutral_recommendation": [],
    }
    # Prefer neutrals with OK/TIGHT GC and same ATAC membership as C1
    for g in gc_grades:
        if not g["id"].startswith("N"):
            continue
        ar = next(r for r in access_rows if r["id"] == g["id"])
        keep = g["gc_match_grade"] in {"TIGHT", "OK"} and ar["access_match_vs_C1"] == "MATCH"
        report["neutral_recommendation"].append(
            {
                "id": g["id"],
                "keep_as_matched_neutral": keep,
                "gc_match_grade": g["gc_match_grade"],
                "access_match_vs_C1": ar["access_match_vs_C1"],
                "in_K562_ATAC_peak": ar["in_K562_ATAC_peak"],
            }
        )

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "g6_matching_amendment.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# G6 matching amendment — GC + K562 ATAC",
        "",
        f"**ATAC:** ENCODE `{acc}` (K562 proxy, not HUDEP-2)  ",
        "**GC:** Ensembl windows ±100 bp / ±1 kb  ",
        "**panel_frozen:** still false",
        "",
        "## GC vs C1",
        "",
        "| ID | |ΔGC| ±100bp | |ΔGC| ±1kb | Grade |",
        "|----|------------:|-----------:|-------|",
    ]
    lines.append(
        f"| C1 | 0 | 0 | reference (GC±100={gc_doc['c1_gc']['w201']:.3f}) |"
    )
    for g in gc_grades:
        lines.append(
            f"| {g['id']} | {g['abs_delta_gc_201']:.3f} | {g['abs_delta_gc_2001']:.3f} | {g['gc_match_grade']} |"
        )
    lines += [
        "",
        "## K562 ATAC overlap",
        "",
        "| ID | In peak | ≤250bp | Dist | vs C1 |",
        "|----|---------|--------|-----:|-------|",
    ]
    for r in access_rows:
        lines.append(
            f"| {r['id']} | {r['in_K562_ATAC_peak']} | {r['within_250bp_ATAC']} | "
            f"{r['dist_ATAC_peak']} | {r['access_match_vs_C1']} |"
        )
    lines += [
        "",
        "## Neutral keep/drop (desk)",
        "",
    ]
    for n in report["neutral_recommendation"]:
        flag = "KEEP" if n["keep_as_matched_neutral"] else "DROP/REPLACE"
        lines.append(
            f"- **{n['id']}**: {flag} (GC {n['gc_match_grade']}, ATAC {n['access_match_vs_C1']})"
        )
    lines += [
        "",
        "## ARCHCODE hunt",
        "",
        "- Local workspace / common user paths: **ABSENT**",
        "- Unlock still needs binary/repo path or continue AlphaGenome-only",
        "",
        f"Artifact: `{out_json.name}`",
        "",
    ]
    (OUT / "g6_matching_amendment.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"neutral_recommendation": report["neutral_recommendation"], "out": str(out_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
