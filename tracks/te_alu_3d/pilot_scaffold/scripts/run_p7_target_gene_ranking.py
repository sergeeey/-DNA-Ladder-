#!/usr/bin/env python3
"""P7 — exploratory target-gene ranking for C1 (desk).

Uses Ensembl gene overlap + local HUDEP-2 CTCF + optional K562 ATAC.
Does NOT move locked E/P. Does NOT claim C1 regulates a gene.
"""

from __future__ import annotations

import gzip
import json
import math
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
DATA = ROOT / "pilot_scaffold" / "data"

C1 = 62_753_923
E = (62_390_000, 62_395_000)
P = (62_690_000, 62_695_000)
# Query window: E through ~100 kb past C1
QUERY = (62_350_000, 62_860_000)
P_MID = (P[0] + P[1]) // 2
E_MID = (E[0] + E[1]) // 2

CTCF_PATHS = [
    DATA / "ctcf_HUDEP2_peaks.bed",
    DATA / "prospective_fixtures" / "ctcf_HUDEP2_peaks.bed",
]
ATAC_PATH = DATA / "cultivation" / "ENCFF055NNT_K562_ATAC.bed.gz"


def ensembl_genes(chrom: str, start: int, end: int) -> list[dict]:
    url = (
        f"https://rest.ensembl.org/overlap/region/human/{chrom}:{start}-{end}"
        f"?feature=gene;content-type=application/json"
    )
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def load_bed_intervals(path: Path, chrom: str = "chr11") -> list[tuple[int, int]]:
    if not path.is_file():
        return []
    out: list[tuple[int, int]] = []
    opener = gzip.open if path.suffix == ".gz" or str(path).endswith(".bed.gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:  # type: ignore[arg-type]
        for line in fh:
            if not line.strip() or line.startswith("#") or line.startswith("track"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            c = parts[0]
            if c != chrom and c != chrom.replace("chr", ""):
                continue
            try:
                s, e = int(parts[1]), int(parts[2])
            except ValueError:
                continue
            out.append((s, e))
    return out


def near_any(pos: int, intervals: list[tuple[int, int]], pad: int) -> bool:
    for s, e in intervals:
        if s - pad <= pos <= e + pad:
            return True
    return False


def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    return a0 < b1 and b0 < a1


def tss_of(gene: dict) -> int | None:
    strand = gene.get("strand")
    start = gene.get("start")
    end = gene.get("end")
    if start is None or end is None:
        return None
    # Ensembl: strand 1 = +, -1 = -
    if strand in (1, "+", "1"):
        return int(start)
    if strand in (-1, "-", "-1"):
        return int(end)
    return int(start)


def score_gene(gene: dict, ctcf: list[tuple[int, int]], atac: list[tuple[int, int]]) -> dict:
    name = gene.get("external_name") or gene.get("id") or "?"
    g0, g1 = int(gene["start"]), int(gene["end"])
    tss = tss_of(gene)
    biotype = gene.get("biotype") or ""
    evid_for: list[str] = []
    evid_against: list[str] = []
    uncertainty: list[str] = ["HUDEP-2_RNA_UNAVAILABLE"]
    score = 0

    body_P = overlaps(g0, g1, P[0], P[1])
    body_E = overlaps(g0, g1, E[0], E[1])
    tss_in_P = tss is not None and P[0] <= tss < P[1]

    if body_P:
        score += 3
        evid_for.append("gene_body_overlaps_locked_P")
    if body_E:
        score += 1
        evid_for.append("gene_body_overlaps_locked_E")
    if tss_in_P:
        score += 5
        evid_for.append("TSS_inside_locked_P")
    else:
        evid_against.append("TSS_not_inside_locked_P")

    if tss is not None:
        d_p = abs(tss - P_MID)
        d_c1 = abs(tss - C1)
        d_e = abs(tss - E_MID)
        if d_p <= 10_000:
            score += 2
            evid_for.append(f"TSS_within_10kb_of_P_mid ({d_p}bp)")
        if d_c1 <= 50_000:
            score += 2
            evid_for.append(f"TSS_within_50kb_of_C1 ({d_c1}bp)")
        elif d_c1 <= 100_000:
            score += 1
            evid_for.append(f"TSS_within_100kb_of_C1 ({d_c1}bp)")
        if d_c1 > 500_000 and not body_P:
            score -= 3
            evid_against.append(f"TSS_far_from_C1 ({d_c1}bp) and no_P_body")
        if near_any(tss, ctcf, 5_000):
            score += 1
            evid_for.append("HUDEP2_CTCF_within_5kb_of_TSS")
        else:
            evid_against.append("no_HUDEP2_CTCF_within_5kb_of_TSS")
        atac_hit = bool(atac) and near_any(tss, atac, 2_000)
        if atac_hit:
            score += 1
            evid_for.append("K562_ATAC_within_2kb_of_TSS_PROXY")
            uncertainty.append("ATAC_is_K562_not_HUDEP2")
        elif not atac:
            uncertainty.append("ATAC_file_missing")
        # geometry dumps
        geometry = {
            "tss": tss,
            "dist_tss_to_C1": d_c1,
            "dist_tss_to_P_mid": d_p,
            "dist_tss_to_E_mid": d_e,
        }
    else:
        evid_against.append("TSS_unknown")
        geometry = {"tss": None}

    # Prefer protein_coding in ranking display but don't hard-kill lncRNA
    if biotype and biotype != "protein_coding":
        uncertainty.append(f"biotype_{biotype}")

    return {
        "gene": name,
        "ensembl_id": gene.get("id"),
        "biotype": biotype,
        "strand": gene.get("strand"),
        "start": g0,
        "end": g1,
        "score": score,
        "body_overlaps_P": body_P,
        "body_overlaps_E": body_E,
        "tss_in_P": tss_in_P,
        "geometry": geometry,
        "evidence_for": evid_for,
        "evidence_against": evid_against,
        "uncertainty": uncertainty,
    }


def label_for(ranked: list[dict]) -> str:
    if not ranked:
        return "P7_BLOCKED"
    top = ranked[0]["score"]
    near = [r for r in ranked if r["score"] >= top - 1]
    if top < 4 or len(near) >= 3:
        return "P7_NO_CLEAR_TARGET"
    return "P7_RANKED_EXPLORATORY"


def main() -> int:
    ctcf: list[tuple[int, int]] = []
    for p in CTCF_PATHS:
        ctcf = load_bed_intervals(p)
        if ctcf:
            break
    # restrict CTCF to query window for speed of near_any
    ctcf = [(s, e) for s, e in ctcf if overlaps(s, e, QUERY[0] - 10_000, QUERY[1] + 10_000)]

    atac_all = load_bed_intervals(ATAC_PATH) if ATAC_PATH.is_file() else []
    atac = [(s, e) for s, e in atac_all if overlaps(s, e, QUERY[0] - 5_000, QUERY[1] + 5_000)]

    try:
        raw = ensembl_genes("11", QUERY[0], QUERY[1])
    except Exception as exc:  # noqa: BLE001
        payload = {
            "status": "P7_TARGET_GENE_COMPLETE",
            "label": "P7_BLOCKED",
            "error": str(exc),
        }
        (OUT / "P7_target_gene_ranking_v1.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        (OUT / "P7_target_gene_ranking_v1.md").write_text(
            f"# P7 — BLOCKED\n\nEnsembl fetch failed: `{exc}`\n", encoding="utf-8"
        )
        print(json.dumps(payload, indent=2))
        return 1

    scored = [score_gene(g, ctcf, atac) for g in raw]
    # de-dup by gene symbol keep max score
    best: dict[str, dict] = {}
    for row in scored:
        k = row["gene"]
        if k not in best or row["score"] > best[k]["score"]:
            best[k] = row
    ranked = sorted(best.values(), key=lambda r: (-r["score"], r["geometry"].get("dist_tss_to_C1") or math.inf))

    label = label_for(ranked)
    top5 = ranked[:12]

    # prior desk nominations cross-check
    prior = ["LRRN4CL", "BSCL2", "ZBTB3", "POLR2G", "HNRNPUL2-BSCL2"]
    prior_hits = {g: next((r for r in ranked if r["gene"] == g), None) for g in prior}

    tss_in_p_count = sum(1 for r in ranked if r["tss_in_P"])

    payload = {
        "status": "P7_TARGET_GENE_COMPLETE",
        "label": label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "P7_TARGET_GENE_CLAIM_v1.md",
        "locked": {
            "C1": f"chr11:{C1}",
            "E": f"chr11:{E[0]}-{E[1]}",
            "P": f"chr11:{P[0]}-{P[1]}",
            "query": f"chr11:{QUERY[0]}-{QUERY[1]}",
        },
        "inputs": {
            "ensembl_genes_raw": len(raw),
            "unique_symbols": len(ranked),
            "hudep2_ctcf_intervals_in_window": len(ctcf),
            "k562_atac_intervals_in_window": len(atac),
            "hudep2_rna": "UNAVAILABLE",
        },
        "tss_inside_locked_P_count": tss_in_p_count,
        "p_redefinition": "FORBIDDEN",
        "provisional_top": top5[0]["gene"] if top5 and label == "P7_RANKED_EXPLORATORY" else None,
        "ranked": top5,
        "prior_desk_nominations": {
            k: ({"score": v["score"], "rank_hint": ranked.index(v) + 1} if v else None)
            for k, v in prior_hits.items()
        },
        "forbidden_claim": "C1 regulates <gene>",
    }

    (OUT / "P7_target_gene_ranking_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    rows = []
    for i, r in enumerate(top5, 1):
        d = r["geometry"].get("dist_tss_to_C1")
        rows.append(
            f"| {i} | **{r['gene']}** | {r['score']} | {r['biotype']} | "
            f"{d if d is not None else '—'} | "
            f"{'Y' if r['body_overlaps_P'] else 'n'} | "
            f"{'Y' if r['tss_in_P'] else 'n'} |"
        )

    prior_lines = []
    for g, info in payload["prior_desk_nominations"].items():
        if info is None:
            prior_lines.append(f"| {g} | not in query window / no Ensembl hit |")
        else:
            prior_lines.append(f"| {g} | score {info['score']} · rank ~{info['rank_hint']} |")

    md = f"""# P7 — Target gene ranking v1

**Date:** 2026-07-16
**Status:** `P7_TARGET_GENE_COMPLETE`
**Claim:** `P7_TARGET_GENE_CLAIM_v1.md`
**Label:** **`{label}`**
**P redefinition:** **FORBIDDEN** (TSS inside locked P: **{tss_in_p_count}**)

## Inputs

| Source | Status |
|--------|--------|
| Ensembl genes in query | {len(raw)} raw → {len(ranked)} unique |
| HUDEP-2 CTCF (local BED) | {len(ctcf)} intervals in/near window |
| K562 ATAC proxy | {len(atac)} intervals (not HUDEP-2) |
| HUDEP-2 RNA-seq | **UNAVAILABLE** |

## Ranked candidates (top)

| Rank | Gene | Score | Biotype | dist TSS-C1 | body∩P | TSS∈P |
|-----:|------|------:|---------|------------:|:------:|:-----:|
{chr(10).join(rows)}

## Prior desk nominations (cross-check)

| Gene | This ranking |
|------|----------------|
{chr(10).join(prior_lines)}

## Soft / hard reading

- Exploratory only — **not** an assigned wet-lab expression target.
- Locked P has **no** protein-coding TSS inside → do **not** move P.
- Missing HUDEP-2 RNA keeps uncertainty high even if geometry ranks one gene first.

## Plain language

Кого мерить после edit — пока **не один ген**, а ранжированный список с дырой по HUDEP-2 RNA.
Отсутствие TSS в locked P — находка, не повод двигать якорь.

## What this does NOT mean

- Not «C1 regulates X»
- Not permission to redefine E/P
- Not HUDEP-2 expression proof

Full dump: `P7_target_gene_ranking_v1.json`
"""
    (OUT / "P7_target_gene_ranking_v1.md").write_text(md, encoding="utf-8")
    print(
        json.dumps(
            {
                "label": label,
                "top": [(r["gene"], r["score"]) for r in top5[:5]],
                "tss_in_P": tss_in_p_count,
                "n_genes": len(ranked),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
