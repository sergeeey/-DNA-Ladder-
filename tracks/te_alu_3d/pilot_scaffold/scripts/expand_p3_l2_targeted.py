#!/usr/bin/env python3
"""Targeted AG expand for P3 L2: same 5 Mb blocks as frozen alleles.

Scores leftover raw-panel alleles that share TE clade + CTCF bin + 5 Mb block
with at least one frozen candidate, plus optional neighborhood gnomAD dig.

Does not touch holdout / Stage-3 / wet-lab.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.ag_contact_delta import VariantSpec, score_variant_deltas
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed
from load_project_env import alphagenome_api_key, load_project_env
from run_ag_cultivation_r4 import (
    CTCF,
    TE,
    EXCLUDE,
    _excluded,
    _dist_to_ctcf,
    _gnomad_snvs_around,
    _load_bed,
    _peak_te_hits,
)

OUT = ROOT.parent / "09_outputs" / "prospective"
STAGE1 = OUT / "stage1_desk_screen_v1.json"
UNIVERSE = OUT / "p3_expanded_universe_v1.json"
RAW = ROOT / "data" / "cultivation" / "p3_expand_raw_panel.json"
BLOCK_MB = 5


def clade(fam: str | None) -> str:
    if not fam:
        return "other"
    f = fam.upper()
    if f.startswith("ALUY"):
        return "AluY"
    if f.startswith("ALUS"):
        return "AluS"
    if f.startswith("ALUJ"):
        return "AluJ"
    if f.startswith("FLAM"):
        return "FLAM"
    if f.startswith("FRAM"):
        return "FRAM"
    return "other"


def cbin(d) -> str:
    try:
        return "zero" if int(d) == 0 else "near"
    except Exception:
        return "unk"


def block(pos: int) -> int:
    return int(pos) // (BLOCK_MB * 1_000_000)


def main() -> int:
    load_project_env()
    assert holdout_is_sealed()
    assert_not_scoring_holdout(OUT / "p3_target_ok.tsv")
    key = alphagenome_api_key()
    if not key:
        raise SystemExit("no AG key")

    stage = json.loads(STAGE1.read_text(encoding="utf-8"))
    uni = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    have = {r["variant_id"] for r in uni["pool"]}

    # target keys from frozen (non-P1)
    targets = []
    for fr in stage["frozen_panel"]:
        vid = fr["variant_id"]
        if str(vid).startswith("P1_"):
            continue
        parts = vid.split(":")
        pos = int(parts[1])
        fam = fr.get("te_family")
        # prefer stage pool metadata
        for r in stage["pool"]:
            if r["variant_id"] == vid:
                fam = r.get("te_family") or fam
                break
        targets.append(
            {
                "variant_id": vid,
                "pos": pos,
                "te_family": fam,
                "clade": clade(fam),
                "cbin": "zero",  # most frozen are dist 0
                "block": block(pos),
            }
        )

    target_keys = {(t["clade"], t["cbin"], t["block"]) for t in targets}
    print("target L2 keys", sorted(target_keys))

    # candidates from leftover raw
    raw = json.loads(RAW.read_text(encoding="utf-8")) if RAW.exists() else []
    cands = []
    for r in raw:
        if r["variant_id"] in have:
            continue
        key_t = (clade(r.get("te_family")), cbin(r.get("dist_ctcf")), block(r["pos"]))
        if key_t in target_keys:
            cands.append(r)

    # dig neighborhood gnomAD around frozen peaks for same clade TE hits
    ctcf = _load_bed(CTCF)
    te = _load_bed(TE)
    hits = _peak_te_hits(ctcf, te)
    for t in targets:
        near = [h for h in hits if abs(h["mid"] - t["pos"]) <= 1_500_000 and clade(h.get("te_family")) == t["clade"]]
        for h in near[:8]:
            if _excluded(h["mid"]):
                continue
            try:
                snvs = _gnomad_snvs_around(h["mid"], half=500, max_af=0.001)
            except Exception as exc:
                print("WARN", h["mid"], exc)
                continue
            time.sleep(0.5)
            for s in snvs:
                d = _dist_to_ctcf(s["pos"], ctcf)
                if d > 250:
                    continue
                if _excluded(s["pos"]):
                    continue
                if clade(h["te_family"]) != t["clade"]:
                    continue
                if cbin(d) != t["cbin"] or block(s["pos"]) != t["block"]:
                    continue
                vid = f"{s['chrom']}:{s['pos']}:{s['ref']}:{s['alt']}"
                if vid in have or any(c["variant_id"] == vid for c in cands):
                    continue
                cands.append(
                    {
                        **s,
                        "variant_id": vid,
                        "te_family": h["te_family"],
                        "dist_ctcf": d,
                        "peak_mid": h["mid"],
                        "source": "p3_l2_targeted",
                    }
                )

    # dedupe
    seen = set()
    uniq = []
    for r in cands:
        if r["variant_id"] in seen:
            continue
        seen.add(r["variant_id"])
        uniq.append(r)
    cands = uniq
    print(f"L2-targeted candidates to score: {len(cands)}")

    budget = 40
    to_score = cands[:budget]
    scored = []
    for i, r in enumerate(to_score, 1):
        print(f"  [{i}/{len(to_score)}] {r['variant_id']}", flush=True)
        spec = VariantSpec(r["chrom"], int(r["pos"]), r["ref"], r["alt"])
        try:
            s = score_variant_deltas(spec)
            scored.append(
                {
                    **r,
                    "ag_status": "SCORED",
                    "ag_chip_tf_mae": s.get("chip_tf_mae"),
                    "ag_contact_mae": s.get("contact_mae_all"),
                    "ag_primary_score": s.get("primary_score"),
                }
            )
        except Exception as exc:
            print("   FAIL", exc)
            scored.append({**r, "ag_status": "FAIL", "ag_error": str(exc)})
        time.sleep(0.35)

    n_add = 0
    for r in scored:
        if r.get("ag_status") != "SCORED":
            continue
        if r["variant_id"] in have:
            continue
        uni["pool"].append(
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
                "source": "p3_l2_targeted",
            }
        )
        have.add(r["variant_id"])
        n_add += 1

    uni["status"] = "P3_UNIVERSE_EXPANDED_L2_TARGETED"
    uni["timestamp"] = datetime.now(timezone.utc).isoformat()
    uni["n_universe"] = len(uni["pool"])
    uni["n_l2_targeted_added"] = n_add
    uni["n_l2_targeted_attempted"] = len(to_score)
    UNIVERSE.write_text(json.dumps(uni, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"added": n_add, "n_universe": uni["n_universe"]}, indent=2))
    return 0


if __name__ == "__main__":
    # fix typo in clade helper if any
    raise SystemExit(main())
