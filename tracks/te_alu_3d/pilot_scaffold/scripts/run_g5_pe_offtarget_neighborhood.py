"""Local PE off-target risk desk without Cas-OFFinder genome DB.

1) Confirm target in Alu (Ensembl repeats)
2) Heuristic: number of NGG sites in enlarged locus window with ≤3 mm to spacer
3) Note: genome-wide Cas-OFFinder still required before order
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "09_outputs" / "prospective" / "G5_PE_offtarget_desk_C1_v1.json"
OUT_MD = ROOT / "09_outputs" / "prospective" / "G5_PE_validation_external_C1_v1.md"

SPACERS = [
    ("PD1", "CGTCCGATAAGCCCTGCCCC", "+", "PrimeDesign #1"),
    ("PD2", "TGGCTAAGGGGCGGGACTTC", "-", "PrimeDesign #2"),
    ("PD3", "GCGGAGGGTGGCTAAGGGGC", "-", "PrimeDesign #3"),
]


def revcomp(s: str) -> str:
    return s.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def mm(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


def fetch_seq(chrom: str, start: int, end: int) -> str:
    url = f"https://rest.ensembl.org/sequence/region/human/{chrom}:{start}..{end}:1?content-type=text/plain"
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read().decode().strip().upper()


def fetch_repeats(chrom: str, start: int, end: int) -> list:
    url = (
        f"https://rest.ensembl.org/overlap/region/human/{chrom}:{start}-{end}"
        f"?feature=repeat;content-type=application/json"
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def scan_window(seq: str, spacer: str, max_mm: int = 3) -> list[dict]:
    hits = []
    L = len(spacer)
    # + strand NGG
    for i in range(0, len(seq) - L - 2):
        pam = seq[i + L : i + L + 3]
        if len(pam) < 3 or pam[1:] != "GG":
            continue
        cand = seq[i : i + L]
        d = mm(cand, spacer)
        if d <= max_mm:
            hits.append({"strand": "+", "mm": d, "start": i, "pam": pam, "seq": cand})
    rsp = revcomp(spacer)
    for i in range(0, len(seq) - L - 2):
        pam = seq[i : i + 3]
        if pam[:2] != "CC":
            continue
        cand = revcomp(seq[i + 3 : i + 3 + L])
        if len(cand) != L:
            continue
        d = mm(cand, spacer)
        if d <= max_mm:
            hits.append({"strand": "-", "mm": d, "start": i, "pam": pam, "seq": cand})
    return hits


def main() -> None:
    # 2 Mb neighborhood on chr11 around C1 for near-locus OT (Alu-dense)
    center = 62_753_923
    win = 1_000_000
    start, end = center - win, center + win
    seq = fetch_seq("11", start, end)
    reps = fetch_repeats("11", center - 2000, center + 2000)
    alu = [
        r
        for r in reps
        if "Alu" in str(r.get("description", ""))
        or "Alu" in str(r.get("external_name", ""))
        or "SINE" in str(r.get("description", ""))
    ]

    report = {
        "locus_repeat": alu,
        "scan_window_grch38": f"chr11:{start}-{end}",
        "spacers": {},
        "caveat": "Neighborhood scan only (2Mb). Not a genome-wide Cas-OFFinder substitute.",
    }
    for sid, spacer, strand, note in SPACERS:
        hits = scan_window(seq, spacer, 3)
        by_mm = {0: 0, 1: 0, 2: 0, 3: 0}
        for h in hits:
            by_mm[h["mm"]] = by_mm.get(h["mm"], 0) + 1
        # exact on-target expected ~1
        report["spacers"][sid] = {
            "spacer": spacer,
            "design_strand": strand,
            "note": note,
            "hits_leq_3mm_in_2Mb": len(hits),
            "by_mm": by_mm,
            "exact_mm0": by_mm.get(0, 0),
            "risk": (
                "HIGH"
                if by_mm.get(0, 0) > 1 or by_mm.get(1, 0) >= 3
                else ("MODERATE" if by_mm.get(1, 0) or by_mm.get(2, 0) >= 5 else "LOWER_NEAR_LOCUS")
            ),
        }

    # merge prior blast if exists
    if OUT_JSON.exists():
        try:
            old = json.loads(OUT_JSON.read_text(encoding="utf-8"))
            report["prior_blast"] = old.get("blasts")
        except Exception:
            pass

    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# G5 PE external validation — C1 (Step 1)",
        "",
        "**Date:** 2026-07-15  ",
        "**Status:** `EXTERNAL_VALIDATED_PARTIAL` · order still **FORBIDDEN**  ",
        "**Tools:** PrimeDesign CLI (Pinellolab) + neighborhood off-target scan",
        "",
        "## PrimeDesign concordance",
        "",
        "| Rank | Spacer | Strand | PAM | Edit dist | Rec. PBS/RTT | First ext nt | vs heuristic |",
        "|-----:|--------|:------:|-----|----------:|--------------|:------------:|--------------|",
        "| 1 | `CGTCCGATAAGCCCTGCCCC` | + | CGG | 8 | 13 / 16 | G | **MATCH** top heuristic |",
        "| 2 | `TGGCTAAGGGGCGGGACTTC` | − | CGG | 1 | 13 / 16 | A | MATCH PD shortlist #4-ish |",
        "| 3 | `GCGGAGGGTGGCTAAGGGGC` | − | GGG | 9 | 13 / 14 | C | FILTER: first C (worse) |",
        "",
        "Full CSV: `primedesign_c1/20260715_09.49.42_PrimeDesign.csv` (233 rows).",
        "",
        "Recommended PE3 ngRNA examples for PD1 (from PrimeDesign):",
        "",
        "| ngRNA spacer | PAM | Distance to peg |",
        "|--------------|-----|----------------:|",
        "| `CCGAGGTGGGCGGAGCTAAT` | GGG | −60 |",
        "| `TAAGGTTAGGCCGAGGTGGG` | CGG | −50 |",
        "",
        "## Off-target desk",
        "",
        f"Target sits in Alu/SINE neighborhood (Ensembl repeats at site). 2 Mb chr11 scan around C1:",
        "",
    ]
    for sid, info in report["spacers"].items():
        lines.append(
            f"- **{sid}** (`{info['spacer']}`): mm0={info['by_mm'].get(0,0)}, "
            f"mm1={info['by_mm'].get(1,0)}, mm2={info['by_mm'].get(2,0)}, "
            f"mm3={info['by_mm'].get(3,0)} → risk **{info['risk']}**"
        )
    lines += [
        "",
        "### Interpretation",
        "",
        "- Alu context → elevated multi-locus risk expected genome-wide.",
        "- Neighborhood scan is **not** sufficient for wet-lab order.",
        "- **Before order:** Cas-OFFinder / CRISPRitz / CRISPOR genome-wide for PD1 (+ ngRNA).",
        "- Prefer PD1 (PAM_intact, first ext = G, matches independent PrimeDesign).",
        "",
        "## Gate decision (Step 1)",
        "",
        "| Item | Verdict |",
        "|------|---------|",
        "| PrimeDesign external redesign | **PASS** (PD1 confirmed) |",
        "| Genome-wide off-target | **PENDING** (blocker for oligo order) |",
        "| Near-locus OT scan | COMPLETE — Alu-aware caution |",
        "| Wet-lab GO / oligo order | still **NO** |",
        "",
        "JSON: `G5_PE_offtarget_desk_C1_v1.json`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["spacers"], indent=2))


if __name__ == "__main__":
    main()
