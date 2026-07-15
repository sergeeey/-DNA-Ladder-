"""Router R4 cultivation pilot: AlphaGenome contact-Δ on NON-holdout candidates.

- Does NOT read or score data/holdout/
- Excludes HBB + sealed HO_A/B/C geography
- Panel: CTCF×Alu/SVA peaks + tiny gnomAD GraphQL (≤2 SNVs per peak)
- Ranks by AG contact MAE; ≤3 shortlist IMMATURE (not G9 / not wet-lab)

Usage:
  # Key from DNA_TE_3DGenome_Context/.env (gitignored) or:
  set ALPHAGENOME_API_KEY=...
  python run_ag_cultivation_r4.py --max-score 6
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from adapters.ag_contact_delta import VariantSpec, score_variant_deltas
from fetch_dual_track_inputs import _post_graphql
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed
from load_project_env import load_project_env

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT.parent / "09_outputs" / "prospective"
CTCF = DATA / "ctcf_HUDEP2_peaks.bed"
TE = DATA / "repeatmasker_chr11_alu_sva.bed"

EXCLUDE = [
    (5_200_000, 5_300_000, "HBB_development"),
    (64_000_000, 68_000_000, "holdout_HO_A_B_C_geography"),
]

GQL = """
query RegionVariants($chrom: String!, $start: Int!, $stop: Int!) {
  region(chrom: $chrom, start: $start, stop: $stop, reference_genome: GRCh38) {
    variants(dataset: gnomad_r4) {
      variant_id
      chrom
      pos
      ref
      alt
      genome { af }
      exome { af }
    }
  }
}
"""


def _excluded(pos: int) -> bool:
    return any(a <= pos < b for a, b, _ in EXCLUDE)


def _load_bed(path: Path) -> list[tuple[int, int, str]]:
    rows: list[tuple[int, int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        p = line.split("\t")
        if p[0] not in ("chr11", "11"):
            continue
        rows.append((int(p[1]), int(p[2]), p[3] if len(p) > 3 else "."))
    return rows


def _peak_te_hits(ctcf, te, pad: int = 250) -> list[dict]:
    hits: list[dict] = []
    for s, e, _ in sorted(ctcf, key=lambda x: -(x[1] - x[0])):
        mid = (s + e) // 2
        if _excluded(mid) or _excluded(s) or _excluded(e):
            continue
        fam = None
        for ts, te_, name in te:
            if ts < e + pad and te_ > s - pad:
                fam = name
                break
        if not fam:
            continue
        hits.append({"start": s, "end": e, "mid": mid, "te_family": fam, "width": e - s})
    return hits


def _gnomad_snvs_around(mid: int, half: int, max_af: float) -> list[dict]:
    start = max(1, mid - half)
    stop = mid + half
    data = None
    for attempt in range(6):
        try:
            data = _post_graphql(GQL, {"chrom": "11", "start": start, "stop": stop})
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise
            time.sleep(1.5 * (attempt + 1))
    if data is None:
        return []
    region = (data.get("data") or {}).get("region") or {}
    out: list[dict] = []
    for v in region.get("variants") or []:
        ref = (v.get("ref") or "").upper()
        alt = (v.get("alt") or "").upper()
        if len(ref) != 1 or len(alt) != 1:
            continue
        pos = int(v["pos"])
        if _excluded(pos):
            continue
        genome = v.get("genome") or {}
        exome = v.get("exome") or {}
        af = genome.get("af")
        if af is None:
            af = exome.get("af")
        try:
            af_f = float(af) if af is not None else None
        except (TypeError, ValueError):
            af_f = None
        if af_f is not None and af_f > max_af:
            continue
        out.append(
            {
                "chrom": "chr11",
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "af": af_f,
                "source": f"gnomad_peak_{mid}",
            }
        )
    return out


def _dist_to_ctcf(pos: int, ctcf) -> int:
    best = 10**12
    for s, e, _ in ctcf:
        best = min(best, abs(pos - s), abs(pos - e), abs(pos - (s + e) // 2))
    return int(best)


def build_panel(ctcf, te, *, max_af: float, max_dist: int, limit: int) -> list[dict]:
    hits = _peak_te_hits(ctcf, te)
    print(f"ctcf_x_te_hits_outside_exclude={len(hits)}")
    panel: list[dict] = []
    seen: set[str] = set()
    per_peak_cap = 2
    for h in hits:
        if len(panel) >= limit:
            break
        print(f"  gnomAD query around {h['mid']} ({h['te_family']})", flush=True)
        try:
            snvs = _gnomad_snvs_around(h["mid"], half=400, max_af=max_af)
        except Exception as exc:
            print(f"  WARN gnomAD: {exc}")
            time.sleep(1.0)
            continue
        local = []
        for r in snvs:
            d = _dist_to_ctcf(r["pos"], ctcf)
            if d > max_dist:
                continue
            r = {
                **r,
                "te_family": h["te_family"],
                "dist_ctcf": d,
                "distance_score": 1.0 / (1.0 + d),
                "peak_mid": h["mid"],
            }
            local.append(r)
        local.sort(key=lambda x: x["dist_ctcf"])
        taken = 0
        for r in local:
            if taken >= per_peak_cap:
                break
            vid = f"{r['chrom']}:{r['pos']}:{r['ref']}:{r['alt']}"
            if vid in seen:
                continue
            seen.add(vid)
            r["variant_id"] = vid
            panel.append(r)
            taken += 1
            if len(panel) >= limit:
                break
        time.sleep(0.6)
    return panel


def main() -> int:
    load_project_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-score", type=int, default=6)
    ap.add_argument("--max-af", type=float, default=0.001)
    ap.add_argument("--max-dist", type=int, default=250)
    args = ap.parse_args()

    assert holdout_is_sealed(), "expected holdout sealed"
    (DATA / "cultivation").mkdir(parents=True, exist_ok=True)
    assert_not_scoring_holdout(DATA / "cultivation" / "ok.tsv")

    ctcf = _load_bed(CTCF)
    te = _load_bed(TE)
    panel = build_panel(
        ctcf, te, max_af=args.max_af, max_dist=args.max_dist, limit=args.max_score
    )
    if not panel:
        print("ERROR: empty panel")
        return 1

    (DATA / "cultivation" / "r4_panel.json").write_text(
        json.dumps(panel, indent=2), encoding="utf-8"
    )
    print(f"scoring n={len(panel)} peaks={len({p.get('peak_mid') for p in panel})}")

    scored: list[dict] = []
    for r in panel:
        assert not _excluded(r["pos"])
        spec = VariantSpec(r["chrom"], r["pos"], r["ref"], r["alt"])
        print("  AG", spec.variant_id, flush=True)
        try:
            s = score_variant_deltas(spec)
            row = {**r, **s, "status": "SCORED", "error": None}
        except Exception as exc:
            row = {
                **r,
                "variant_id": spec.variant_id,
                "primary_score": math.nan,
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
            }
        scored.append(row)

    ok = [x for x in scored if x.get("status") == "SCORED"]
    ok.sort(key=lambda x: float(x.get("primary_score") or 0.0), reverse=True)
    shortlist = ok[:3]
    for i, x in enumerate(shortlist, 1):
        x["shortlist_rank"] = i
        x["decision"] = "IMMATURE"
        x["g9_frozen"] = False

    slim = [{k: v for k, v in x.items() if k != "biosample_channels"} for x in scored]
    report = {
        "status": "R4_PILOT_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "holdout_sealed": True,
        "scored_holdout": False,
        "exclude_windows": [{"start": a, "end": b, "reason": r} for a, b, r in EXCLUDE],
        "n_scored": len(scored),
        "n_ok": len(ok),
        "n_peaks_in_panel": len({p.get("peak_mid") for p in panel}),
        "shortlist": [
            {
                "rank": x.get("shortlist_rank"),
                "variant_id": x.get("variant_id"),
                "primary_score": x.get("primary_score"),
                "contact_mae_all": x.get("contact_mae_all"),
                "contact_mae_heme_proxy": x.get("contact_mae_heme_proxy"),
                "chip_tf_mae": x.get("chip_tf_mae"),
                "dist_ctcf": x.get("dist_ctcf"),
                "te_family": x.get("te_family"),
                "af": x.get("af"),
                "peak_mid": x.get("peak_mid"),
                "decision": x.get("decision"),
            }
            for x in shortlist
        ],
        "all_scores": slim,
        "next": [
            "Desk G3/G4 for shortlist alleles (non-holdout)",
            "Do not unblind HO_* / do not wet-lab",
        ],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "ag_cultivation_r4_report.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    out_tsv = OUT / "ag_cultivation_r4_scores.tsv"
    fields = [
        "variant_id",
        "pos",
        "ref",
        "alt",
        "af",
        "te_family",
        "peak_mid",
        "dist_ctcf",
        "distance_score",
        "primary_score",
        "contact_mae_all",
        "contact_mae_heme_proxy",
        "chip_tf_mae",
        "status",
        "source",
        "error",
    ]
    with out_tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        for x in slim:
            w.writerow(x)

    lines = [
        "# AlphaGenome R4 cultivation shortlist (non-holdout)",
        "",
        f"**Date:** {report['timestamp'][:10]}  ",
        "**Geography:** chr11 outside HBB + HO_A/B/C  ",
        "**Holdout:** SEALED / not scored  ",
        "**Decision:** IMMATURE (≤3) — not G9 freeze, not wet-lab GO",
        "",
        "| Rank | Variant | AG contact MAE | CHIP_TF MAE | dist CTCF | TE | AF |",
        "|-----:|---------|---------------:|------------:|----------:|----|----|",
    ]
    for x in shortlist:
        lines.append(
            f"| {x.get('shortlist_rank')} | `{x.get('variant_id')}` | "
            f"{float(x.get('primary_score') or 0):.4f} | "
            f"{float(x.get('chip_tf_mae') or 0):.4f} | "
            f"{x.get('dist_ctcf')} | {x.get('te_family')} | {x.get('af')} |"
        )
    lines += [
        "",
        "## Explicit non-claims",
        "- Not confirmatory enrichment / not 3D disruption / not holdout unblind",
        "",
        f"Artifacts: `{out_json.name}`, `{out_tsv.name}`",
        "",
    ]
    (OUT / "ag_cultivation_r4_shortlist.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"shortlist": report["shortlist"], "out": str(out_json)}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
