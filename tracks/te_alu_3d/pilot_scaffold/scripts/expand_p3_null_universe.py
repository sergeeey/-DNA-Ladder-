#!/usr/bin/env python3
"""Expand SCORED rare Alu/SVA SNV universe for P3 L1/L2 matched-null.

Does NOT touch holdout. Does NOT reshape Stage-3. Does NOT wet-lab.

1. Pull more CTCF×TE gnomAD rare SNVs (prefer frozen-panel TE families)
2. AG-score up to --budget new alleles
3. Merge with Stage-1 SCORED pool → p3_expanded_universe_v1.json
4. Optionally re-run P3 (caller can invoke run_p3_matched_null_panel.py)

Usage (from pilot_scaffold):
  python scripts/expand_p3_null_universe.py --limit 120 --budget 50 --per-peak 3
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.ag_contact_delta import VariantSpec, score_variant_deltas  # noqa: E402
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed  # noqa: E402
from load_project_env import alphagenome_api_key, load_project_env  # noqa: E402
from run_ag_cultivation_r4 import (  # noqa: E402
    CTCF,
    TE,
    _load_bed,
    build_panel,
)

OUT = ROOT.parent / "09_outputs" / "prospective"
STAGE1 = OUT / "stage1_desk_screen_v1.json"
UNIVERSE = OUT / "p3_expanded_universe_v1.json"
RAW_NEW = ROOT / "data" / "cultivation" / "p3_expand_raw_panel.json"


def _pool_row_from_stage(r: dict) -> dict:
    return {
        "variant_id": r["variant_id"],
        "chrom": r.get("chrom", "chr11"),
        "pos": int(r["pos"]),
        "ref": r["ref"],
        "alt": r["alt"],
        "af": r.get("af"),
        "te_family": r.get("te_family"),
        "dist_ctcf": r.get("dist_ctcf"),
        "ag_status": r.get("ag_status"),
        "ag_chip_tf_mae": r.get("ag_chip_tf_mae"),
        "ag_contact_mae": r.get("ag_contact_mae"),
        "ag_primary_score": r.get("ag_primary_score"),
        "pwm_delta_logodds": r.get("pwm_delta_logodds"),
        "pe_desk": r.get("pe_desk"),
        "source": "stage1_pool",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=120, help="raw panel size target")
    ap.add_argument("--budget", type=int, default=50, help="max new AG score calls")
    ap.add_argument("--per-peak", type=int, default=3)
    ap.add_argument("--max-af", type=float, default=0.001)
    ap.add_argument("--max-dist", type=int, default=250)
    ap.add_argument("--reuse-raw", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="build/merge only, skip AG")
    args = ap.parse_args()

    load_project_env()
    assert holdout_is_sealed(), "holdout must stay sealed"
    assert_not_scoring_holdout(OUT / "p3_expand_ok.tsv")

    stage = json.loads(STAGE1.read_text(encoding="utf-8"))
    stage_pool = stage["pool"]
    have = {r["variant_id"] for r in stage_pool}
    prefer = {
        r.get("te_family")
        for r in stage.get("frozen_panel", [])
        if r.get("te_family")
    }
    prefer |= {r.get("te_family") for r in stage_pool if r.get("te_family")}
    prefer.discard(None)

    if args.reuse_raw and RAW_NEW.exists():
        raw = json.loads(RAW_NEW.read_text(encoding="utf-8"))
        print(f"reuse raw n={len(raw)}")
    else:
        print("building expanded gnomAD panel…", flush=True)
        ctcf = _load_bed(CTCF)
        te = _load_bed(TE)
        raw = build_panel(
            ctcf,
            te,
            max_af=args.max_af,
            max_dist=args.max_dist,
            limit=args.limit,
            per_peak_cap=args.per_peak,
            prefer_families=prefer,
        )
        RAW_NEW.parent.mkdir(parents=True, exist_ok=True)
        RAW_NEW.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        print(f"raw panel n={len(raw)} wrote {RAW_NEW}")

    new_candidates = [r for r in raw if r["variant_id"] not in have]
    print(f"new candidates (not in stage1): {len(new_candidates)}")

    key = alphagenome_api_key()
    scored_new: list[dict] = []
    if args.dry_run or not key:
        print("SKIP AG scoring:", "dry-run" if args.dry_run else "no API key")
        for r in new_candidates[: args.budget]:
            scored_new.append({**r, "ag_status": "ABSENT", "source": "p3_expand"})
    else:
        to_score = new_candidates[: args.budget]
        print(f"AG scoring n={len(to_score)} (budget={args.budget})", flush=True)
        for i, r in enumerate(to_score, 1):
            vid = r["variant_id"]
            print(f"  [{i}/{len(to_score)}] {vid}", flush=True)
            assert not any(
                a <= int(r["pos"]) < b
                for a, b, _ in [
                    (5_200_000, 5_300_000, "HBB"),
                    (64_000_000, 68_000_000, "HO"),
                ]
            )
            spec = VariantSpec(r["chrom"], int(r["pos"]), r["ref"], r["alt"])
            try:
                s = score_variant_deltas(spec)
                scored_new.append(
                    {
                        **r,
                        "ag_status": "SCORED",
                        "ag_contact_mae": s.get("contact_mae_all"),
                        "ag_chip_tf_mae": s.get("chip_tf_mae"),
                        "ag_primary_score": s.get("primary_score"),
                        "ag_error": None,
                        "source": "p3_expand",
                    }
                )
            except Exception as exc:
                scored_new.append(
                    {
                        **r,
                        "ag_status": "FAIL",
                        "ag_error": f"{type(exc).__name__}: {exc}",
                        "source": "p3_expand",
                    }
                )
                print("    FAIL", scored_new[-1]["ag_error"])
            time.sleep(0.35)

    universe = [_pool_row_from_stage(r) for r in stage_pool if r.get("ag_status") == "SCORED"]
    n_stage = len(universe)
    for r in scored_new:
        if r.get("ag_status") != "SCORED":
            continue
        if r["variant_id"] in have:
            continue
        universe.append(
            {
                "variant_id": r["variant_id"],
                "chrom": r.get("chrom", "chr11"),
                "pos": int(r["pos"]),
                "ref": r["ref"],
                "alt": r["alt"],
                "af": r.get("af"),
                "te_family": r.get("te_family"),
                "dist_ctcf": r.get("dist_ctcf"),
                "ag_status": "SCORED",
                "ag_chip_tf_mae": r.get("ag_chip_tf_mae"),
                "ag_contact_mae": r.get("ag_contact_mae"),
                "ag_primary_score": r.get("ag_primary_score"),
                "pwm_delta_logodds": None,
                "pe_desk": None,
                "source": "p3_expand",
            }
        )

    doc = {
        "status": "P3_UNIVERSE_EXPANDED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "holdout_sealed": True,
        "n_stage1_scored": n_stage,
        "n_new_attempted": len(scored_new),
        "n_new_scored": sum(1 for r in scored_new if r.get("ag_status") == "SCORED"),
        "n_universe": len(universe),
        "prefer_families": sorted(prefer),
        "budget": args.budget,
        "limit": args.limit,
        "pool": universe,
        "new_attempts": [
            {
                "variant_id": r["variant_id"],
                "ag_status": r.get("ag_status"),
                "te_family": r.get("te_family"),
                "dist_ctcf": r.get("dist_ctcf"),
                "ag_chip_tf_mae": r.get("ag_chip_tf_mae"),
                "ag_contact_mae": r.get("ag_contact_mae"),
                "error": r.get("ag_error"),
            }
            for r in scored_new
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    UNIVERSE.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(UNIVERSE),
                "n_universe": len(universe),
                "n_new_scored": doc["n_new_scored"],
                "n_new_fail": sum(1 for r in scored_new if r.get("ag_status") == "FAIL"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
