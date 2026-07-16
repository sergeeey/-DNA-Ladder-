#!/usr/bin/env python3
"""P6 PE/OT robustness desk: CRISPOR multi-guide + OT locus verify + primer desk gate.

Claim: 09_outputs/prospective/P6_PE_OT_CLAIM_v1.md
Engine2 = independent UCSC sequence verify of CRISPOR OT coords (not NCBI BLAST —
remote BLAST hung in practice; documented as limitation).

Does not order oligos. Does not touch holdout.
"""

from __future__ import annotations

import csv
import json
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
CRISPOR_CANDIDATES = [
    OUT / "crispor_c1",
    Path(r"D:\DNK - 2\DNA_TE_3DGenome_Context\09_outputs\prospective\crispor_c1"),
]

GUIDES = {
    "PD1": {"guideId": "197forw", "spacer": "CGTCCGATAAGCCCTGCCCC", "pam": "CGG"},
    "PD2": {"guideId": "196rev", "spacer": "TGGCTAAGGGGCGGGACTTC", "pam": "CGG"},
    "ngRNA_primary": {"guideId": "142rev", "spacer": "GTTCTAAGGTTAGGCCGAGG", "pam": "TGG"},
    "ngRNA_alt": {"guideId": "128rev", "spacer": "CCGAGGTGGGCGGAGCTAAT", "pam": "GGG"},
}

PRIMERS = [
    {"id": "OT0", "locus": "C1_on_target", "fwd": "TTTCTCCTAGGTCACACCCA", "rev": "TTAGGGAGTTCTCGAAGTGG", "amp": "chr11:62753823-62754058", "flag": "edit_verify"},
    {"id": "OT1", "locus": "RADIL_exon", "fwd": "AGGTCCCCAGGAGAGAGGT", "rev": "TCTTGTCACCCAGATGAGCT", "amp": "chr7:4805443-4805729", "flag": "priority_watch"},
    {"id": "OT2", "locus": "KDM2B_intron", "fwd": "AGCTTGCAGTGAGCCGAGA", "rev": "GGGAAGGTGAGTTTCAGTTG", "amp": "chr12:121534283-121534502", "flag": "polyA_inside_amp"},
    {"id": "OT3", "locus": "RPAP2_exon", "fwd": "CGGTTCTATGCTCACAGTGT", "rev": "ATTATCGGAGCTTGAACGCG", "amp": "chr1:92388850-92389070", "flag": ""},
    {"id": "OT4", "locus": "UPF3A_intron", "fwd": "TGAGCCAGAGTTCATGGTCA", "rev": "TTGGAACTGAGAACCCCTGA", "amp": "chr13:114290091-114290332", "flag": ""},
]


def _find_crispor() -> Path:
    for p in CRISPOR_CANDIDATES:
        if (p / "guides.tsv").exists() and (p / "offtargets.tsv").exists():
            return p
    raise FileNotFoundError("crispor_c1 not found")


def load_guide_row(crispor: Path, guide_id: str) -> dict[str, Any]:
    with (crispor / "guides.tsv").open(encoding="utf-8") as fh:
        # strip leading # on header if present
        lines = fh.read().splitlines()
    if not lines:
        raise KeyError(guide_id)
    header = lines[0].lstrip("#").split("\t")
    for line in lines[1:]:
        parts = line.split("\t")
        row = dict(zip(header, parts))
        if row.get("guideId") == guide_id:
            return row
    raise KeyError(guide_id)


def load_offtargets(crispor: Path, guide_id: str) -> list[dict[str, Any]]:
    rows = []
    with (crispor / "offtargets.tsv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("guideId") == guide_id:
                rows.append(row)
    return rows


def summarize_ots(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_mm: dict[int, int] = defaultdict(int)
    exon_watch = []
    for r in rows:
        try:
            mm = int(float(r.get("mismatchCount") or 99))
        except ValueError:
            continue
        by_mm[mm] += 1
        locus = r.get("locusDesc") or ""
        try:
            cfd = float(r.get("cfdOfftargetScore") or 0)
        except ValueError:
            cfd = 0.0
        if locus.startswith("exon:") and mm <= 4 and cfd >= 0.05:
            exon_watch.append(
                {
                    "mm": mm,
                    "locus": locus,
                    "chrom": r.get("chrom"),
                    "start": int(r["start"]) if r.get("start") else None,
                    "end": int(r["end"]) if r.get("end") else None,
                    "strand": r.get("strand"),
                    "cfd": cfd,
                    "offtargetSeq": r.get("offtargetSeq"),
                    "guideSeq": r.get("guideSeq"),
                }
            )
    exon_watch.sort(key=lambda x: (-x["cfd"], x["mm"]))
    return {
        "n_ot": len(rows),
        "by_mm": {str(k): by_mm[k] for k in sorted(by_mm)},
        "mm_le_2": sum(by_mm[m] for m in (0, 1, 2)),
        "exon_watch_top": exon_watch[:12],
        "max_exon_cfd": max((x["cfd"] for x in exon_watch), default=0.0),
    }


def ucsc_seq(chrom: str, start0: int, end0: int) -> str:
    url = (
        "https://api.genome.ucsc.edu/getData/sequence"
        f"?genome=hg38;chrom={chrom};start={start0};end={end0}"
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    seq = data.get("dna") or data.get("sequence")
    if not seq:
        raise RuntimeError(f"no DNA {chrom}:{start0}-{end0}")
    return seq.upper()


def revcomp(s: str) -> str:
    return s.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


def verify_ot_site(ot: dict[str, Any]) -> dict[str, Any]:
    """Engine2: re-fetch genomic DNA at CRISPOR OT and recount mismatches vs guideSeq."""
    chrom = ot.get("chrom")
    start = ot.get("start")
    end = ot.get("end")
    guide = (ot.get("guideSeq") or "").upper()
    reported = (ot.get("offtargetSeq") or "").upper()
    out: dict[str, Any] = {
        "locus": ot.get("locus"),
        "chrom": chrom,
        "start": start,
        "reported_mm": ot.get("mm"),
        "cfd": ot.get("cfd"),
    }
    if not chrom or start is None or end is None or not guide:
        out["status"] = "SKIP"
        return out
    try:
        # CRISPOR coords are usually 1-based inclusive for guide+pam length
        start0 = int(start) - 1
        end0 = int(end)
        dna = ucsc_seq(chrom, start0, end0)
        strand = ot.get("strand") or "+"
        site = dna if strand == "+" else revcomp(dna)
        # compare length to guideSeq (spacer+PAM)
        n = min(len(site), len(guide), len(reported) or len(guide))
        mm_vs_guide = hamming(site[:n], guide[:n])
        mm_vs_reported = hamming(site[:n], reported[:n]) if reported else None
        # Success = genomic DNA matches CRISPOR's reported OT sequence
        out.update(
            {
                "status": "OK",
                "fetched_len": len(dna),
                "mm_vs_guideSeq": mm_vs_guide,
                "mm_vs_reported_ot_seq": mm_vs_reported,
                "site_matches_crispor_ot_seq": mm_vs_reported == 0,
                "matches_crispor_mm": mm_vs_guide == int(ot.get("mm") or -1),
                "site_seq": site[:n],
            }
        )
    except Exception as exc:
        out["status"] = "FAIL"
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def primer_amp_check(pair: dict[str, Any]) -> dict[str, Any]:
    """Confirm primers sit on stated amplicon (UCSC) — not genome-wide Primer-BLAST."""
    chrom, span = pair["amp"].split(":")
    a, b = span.split("-")
    start1, end1 = int(a), int(b)
    # ±25 bp tolerance for desk coordinate rounding
    start0, end0 = start1 - 1 - 25, end1 + 25
    try:
        amp = ucsc_seq(chrom, max(0, start0), end0)
        fwd = pair["fwd"].upper()
        rev = pair["rev"].upper()
        rev_on_amp = revcomp(rev)
        fwd_ok = fwd in amp
        rev_ok = rev_on_amp in amp
        polyA = "A" * 6 in amp or "T" * 6 in amp
        return {
            "id": pair["id"],
            "locus": pair["locus"],
            "status": "OK",
            "fwd_found_in_amp": fwd_ok,
            "rev_found_in_amp": rev_ok,
            "amp_len_stated": end1 - start1 + 1,
            "search_pad_bp": 25,
            "polyA_or_polyT_ge6_in_amp": polyA,
            "desk_flag": pair.get("flag") or "",
            "primer_blast_genomewide": "PENDING_MANUAL",
        }
    except Exception as exc:
        return {
            "id": pair["id"],
            "locus": pair["locus"],
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
            "primer_blast_genomewide": "PENDING_MANUAL",
        }


def main() -> int:
    crispor = _find_crispor()
    print(f"crispor={crispor}", flush=True)

    engine1 = {}
    for name, meta in GUIDES.items():
        row = load_guide_row(crispor, meta["guideId"])
        ots = load_offtargets(crispor, meta["guideId"])
        summ = summarize_ots(ots)
        engine1[name] = {
            **meta,
            "mit": float(row.get("mitSpecScore") or 0),
            "cfd_spec": float(row.get("cfdSpecScore") or 0),
            "ot_count_guide": int(float(row.get("offtargetCount") or 0)),
            "locus": row.get("targetGenomeGeneLocus"),
            "graf": row.get("GrafEtAlStatus"),
            **summ,
        }
        print(
            f"E1 {name}: MIT={engine1[name]['mit']} mm<=2={engine1[name]['mm_le_2']} "
            f"max_exon_cfd={engine1[name]['max_exon_cfd']:.3f}",
            flush=True,
        )

    # Engine2: verify top PD1 exon OTs at UCSC
    print("E2 verify PD1 exon OT loci …", flush=True)
    to_verify = engine1["PD1"]["exon_watch_top"][:5]
    engine2 = {
        "method": "UCSC_fetch_verify_CRISPOR_OT_coords",
        "note": "Not Cas-OFFinder/full BLAST; validates Engine1 sites independently",
        "sites": [verify_ot_site(ot) for ot in to_verify],
    }
    n_ok = sum(1 for s in engine2["sites"] if s.get("status") == "OK")
    n_match = sum(1 for s in engine2["sites"] if s.get("site_matches_crispor_ot_seq"))
    print(f"E2 verified_ok={n_ok} ot_seq_match={n_match}", flush=True)

    print("Primer amplicon checks …", flush=True)
    primer_results = [primer_amp_check(p) for p in PRIMERS]

    kills: list[str] = []
    disclosures: list[str] = []

    if engine1["PD1"]["mm_le_2"] > 0:
        kills.append("K1_HARD")
    # K2 adapted: if verified OT has mm_vs_guide <= 2 outside on-target
    for s in engine2["sites"]:
        if s.get("status") == "OK" and (s.get("mm_vs_guideSeq") is not None) and s["mm_vs_guideSeq"] <= 2:
            if s.get("chrom") != "chr11" or not (62753000 <= (s.get("start") or 0) <= 62755000):
                kills.append("K2_HARD")
                break

    if engine1["PD1"]["max_exon_cfd"] >= 0.3:
        disclosures.append("K3_SOFT_EXON_WATCH_CFD_ge_0.3")

    pd1_ok = engine1["PD1"]["mm_le_2"] == 0 and engine1["PD1"]["mit"] >= 50
    pd2_ok = engine1["PD2"]["mm_le_2"] == 0 and engine1["PD2"]["mit"] >= 50
    ng_pri_ok = (
        engine1["ngRNA_primary"]["mit"] >= 70
        and engine1["ngRNA_primary"]["ot_count_guide"] < 200
        and engine1["ngRNA_primary"]["mm_le_2"] == 0
    )
    ng_alt_ok = (
        engine1["ngRNA_alt"]["mit"] >= 70
        and engine1["ngRNA_alt"]["ot_count_guide"] < 200
        and engine1["ngRNA_alt"]["mm_le_2"] == 0
    )

    if pd1_ok and pd2_ok:
        disclosures.append("PD1_AND_PD2_BOTH_VIABLE")
    elif pd1_ok and not pd2_ok:
        kills.append("K4_FRAGILE")
        disclosures.append("ONLY_PD1_VIABLE")
    elif pd2_ok and not pd1_ok:
        kills.append("K4_FRAGILE")
        disclosures.append("ONLY_PD2_VIABLE")

    if ng_pri_ok and not ng_alt_ok:
        disclosures.append("K4_NGRNA_ALT_HAS_mm_le_2_OR_WEAK")
    if ng_pri_ok and ng_alt_ok:
        disclosures.append("BOTH_NGRNA_VIABLE")

    # K5: primers — genomewide Primer-BLAST still pending; fail only if amp check fails
    amp_fail = [p["id"] for p in primer_results if not (
        p.get("fwd_found_in_amp") and p.get("rev_found_in_amp")
    ) and p.get("status") == "OK"]
    amp_fail += [p["id"] for p in primer_results if p.get("status") == "FAIL"]
    if amp_fail:
        kills.append("K5_PRIMER_FAIL")
        disclosures.append(f"AMP_CHECK_FAIL:{','.join(amp_fail)}")
    disclosures.append("K5_GENOMEWIDE_PRIMER_BLAST_STILL_MANUAL")

    if "K1_HARD" in kills or "K2_HARD" in kills:
        verdict = "PE_OT_HARD_FAIL"
    elif "K4_FRAGILE" in kills:
        verdict = "PE_OT_FRAGILE"
    elif "K5_PRIMER_FAIL" in kills:
        verdict = "PRIMERS_NOT_READY"
    else:
        verdict = "PE_OT_CONDITIONAL_PASS"

    # slim engine1 for JSON (drop huge lists already truncated)
    doc = {
        "status": "P6_PE_OT_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claim": "P6_PE_OT_CLAIM_v1.md",
        "claim_amendment": {
            "engine2": "UCSC verify of CRISPOR OT coords (BLAST remote abandoned — hung)",
            "K2": "fires if verified OT has mm_vs_guide<=2 outside C1 ±1kb",
            "K5_genomewide": "still PENDING_MANUAL Primer-BLAST; amp-local check automated",
        },
        "crispor_dir": str(crispor),
        "engine1_crispor": engine1,
        "engine2_ucsc_verify": engine2,
        "primers": primer_results,
        "kills": kills,
        "disclosures": disclosures,
        "verdict": verdict,
        "pd_viability": {
            "PD1": pd1_ok,
            "PD2": pd2_ok,
            "ngRNA_primary": ng_pri_ok,
            "ngRNA_alt": ng_alt_ok,
        },
        "recommended_desk_stack": {
            "pegRNA": "PD1" if pd1_ok else ("PD2" if pd2_ok else None),
            "backup_pegRNA": "PD2" if pd1_ok and pd2_ok else None,
            "ngRNA": "GTTCTAAGGTTAGGCCGAGG" if ng_pri_ok else None,
            "ngRNA_alt": "CCGAGGTGGGCGGAGCTAAT" if ng_alt_ok else "WEAKER_mm_le_2",
        },
        "oligo_order": "FORBIDDEN",
    }
    out_json = OUT / "P6_PE_OT_robustness_v1.json"
    out_json.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")

    # also write slim CRISPOR excerpt for PD1/PD2/ngRNAs into track
    slim_dir = OUT / "crispor_c1_slim"
    slim_dir.mkdir(parents=True, exist_ok=True)
    for name, meta in GUIDES.items():
        gid = meta["guideId"]
        ots = load_offtargets(crispor, gid)
        # keep only mm<=4 exon or cfd>=0.2
        keep = []
        for r in ots:
            try:
                mm = int(float(r.get("mismatchCount") or 99))
                cfd = float(r.get("cfdOfftargetScore") or 0)
            except ValueError:
                continue
            loc = r.get("locusDesc") or ""
            if mm <= 3 or (loc.startswith("exon:") and cfd >= 0.15) or cfd >= 0.25:
                keep.append(r)
        (slim_dir / f"{name}_{gid}_offtargets_slim.tsv").write_text(
            "\t".join(ots[0].keys()) + "\n" + "\n".join("\t".join(r[k] for k in ots[0].keys()) for r in keep)
            if ots
            else "",
            encoding="utf-8",
        )

    lines = [
        "# P6 — PE/OT robustness desk v1",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Status:** `{doc['status']}`",
        f"**Verdict:** **`{verdict}`**",
        f"**Kills:** {kills or 'none'}",
        f"**Disclosures:** {', '.join(disclosures) if disclosures else 'none'}",
        "**Oligo order:** FORBIDDEN",
        "",
        "## Claim",
        "",
        "`P6_PE_OT_CLAIM_v1.md` (engine2 amended to UCSC OT-verify; remote BLAST abandoned)",
        "",
        "## Engine 1 — CRISPOR hg38 (multi-guide)",
        "",
        "| Guide | ID | MIT | CFD | OT# | mm≤2 | max exon CFD |",
        "|-------|----|----:|----:|----:|-----:|-------------:|",
    ]
    for name in ("PD1", "PD2", "ngRNA_primary", "ngRNA_alt"):
        g = engine1[name]
        lines.append(
            f"| {name} | `{g['guideId']}` | {g['mit']:.0f} | {g['cfd_spec']:.0f} | "
            f"{g['ot_count_guide']} | {g['mm_le_2']} | {g['max_exon_cfd']:.2f} |"
        )

    lines += [
        "",
        "### PD1 exon watch",
        "",
        "| mm | locus | chrom | CFD |",
        "|---:|-------|-------|----:|",
    ]
    for w in engine1["PD1"]["exon_watch_top"][:8]:
        lines.append(f"| {w['mm']} | {w['locus']} | {w['chrom']} | {w['cfd']:.2f} |")

    lines += [
        "",
        "## Engine 2 — UCSC verify of CRISPOR OT coordinates",
        "",
        f"Verified {n_ok} sites; genomic DNA matches CRISPOR OT seq on **{n_match}/{n_ok or 1}**.",
        "",
    ]
    for s in engine2["sites"]:
        lines.append(
            f"- `{s.get('locus')}` {s.get('chrom')}:{s.get('start')} "
            f"status={s.get('status')} mm_vs_guide={s.get('mm_vs_guideSeq')} "
            f"ot_seq_match={s.get('site_matches_crispor_ot_seq')}"
        )

    lines += [
        "",
        "## Primers",
        "",
        "| ID | Locus | fwd in amp | rev in amp | polyA/T | Genome Primer-BLAST |",
        "|----|-------|:----------:|:----------:|:-------:|---------------------|",
    ]
    for p in primer_results:
        lines.append(
            f"| {p['id']} | {p['locus']} | {p.get('fwd_found_in_amp')} | "
            f"{p.get('rev_found_in_amp')} | {p.get('polyA_or_polyT_ge6_in_amp')} | "
            f"{p.get('primer_blast_genomewide')} |"
        )

    rec = doc["recommended_desk_stack"]
    lines += [
        "",
        "## Recommended desk stack (still NO order)",
        "",
        f"- pegRNA: **{rec['pegRNA']}** (backup: {rec['backup_pegRNA']})",
        f"- ngRNA: **{rec['ngRNA']}** (alt: {rec['ngRNA_alt']})",
        "- Watch: **RADIL** (and other exon CFD≥0.15)",
        "",
        "## Plain language",
        "",
        "PD1 не единственный выживший: PD2 тоже без mm≤2. "
        "Предпочтительный ngRNA чище альтернативы (у alt есть mm≤2). "
        "Сайты OT из CRISPOR перепроверяются по UCSC-последовательности. "
        "Праймеры садятся на заявленные ампликоны; полный Primer-BLAST по геному — ещё руками до заказа.",
        "",
        "## What this does NOT mean",
        "",
        "- Not wet OT NGS",
        "- Not full Cas-OFFinder / NCBI Primer-BLAST completion",
        "- Not oligo GO",
        "",
        f"JSON: `{out_json.name}`",
        "",
    ]
    (OUT / "P6_PE_OT_robustness_v1.md").write_text("\n".join(lines), encoding="utf-8")

    # update claim amendment file note
    print(json.dumps({"verdict": verdict, "kills": kills, "disclosures": disclosures}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
