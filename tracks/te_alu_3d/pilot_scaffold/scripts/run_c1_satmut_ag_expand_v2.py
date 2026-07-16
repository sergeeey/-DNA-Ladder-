#!/usr/bin/env python3
"""P2 expand: all A→G + random 100 AG scores for C1 301 bp satmut.

Reuses v1 AG scores. Same S1/S2/S3 as C1_saturation_mutagenesis_v1.
Claim: 09_outputs/prospective/P2_SATMUT_EXPAND_CLAIM_v1.md
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PS = ROOT / "pilot_scaffold"
sys.path.insert(0, str(PS))

from adapters.ag_contact_delta import VariantSpec, score_variant_deltas  # noqa: E402
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed  # noqa: E402
from load_project_env import alphagenome_api_key, load_project_env  # noqa: E402

OUT = ROOT / "09_outputs" / "prospective"
DATA = PS / "data" / "cultivation"
FA = DATA / "c1_reporter_minimal_301bp_REF.fa"
V1 = OUT / "C1_saturation_mutagenesis_v1.json"

C1_POS = 62753923
C1_REF = "A"
C1_ALT = "G"
WIN_START1 = 62753773
WIN_END1 = 62754073
SEED = 20260716


def load_ref_seq() -> str:
    lines = FA.read_text(encoding="utf-8").splitlines()
    return "".join(lines[1:]).upper().replace("U", "T")


def all_subst(seq: str) -> list[dict]:
    bases = ["A", "C", "G", "T"]
    out = []
    for i, ref in enumerate(seq):
        pos = WIN_START1 + i
        for alt in bases:
            if alt == ref:
                continue
            out.append(
                {
                    "pos": pos,
                    "ref": ref,
                    "alt": alt,
                    "idx": i,
                    "is_c1": pos == C1_POS and ref == C1_REF and alt == C1_ALT,
                    "variant_id": f"chr11:{pos}:{ref}:{alt}",
                }
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--random-n", type=int, default=100)
    ap.add_argument("--skip-ag", action="store_true")
    ap.add_argument("--max-new", type=int, default=0, help="cap new AG calls (0=no cap)")
    args = ap.parse_args()

    load_project_env()
    assert holdout_is_sealed()
    assert_not_scoring_holdout(OUT / "p2_satmut_ok.tsv")
    if not args.skip_ag and not alphagenome_api_key():
        raise SystemExit("no ALPHAGENOME_API_KEY")

    seq = load_ref_seq()
    assert len(seq) == 301, len(seq)
    variants = all_subst(seq)
    by_id = {v["variant_id"]: v for v in variants}

    prior = json.loads(V1.read_text(encoding="utf-8"))
    prior_ag = {v["variant_id"]: v for v in prior.get("variants_ag") or []}
    print(f"prior AG scored={len(prior_ag)}", flush=True)

    # reuse prior into working dict
    scored: dict[str, dict] = {}
    for vid, row in prior_ag.items():
        if row.get("ag_status") != "SCORED":
            continue
        base = by_id.get(vid, row)
        merged = {**base, **row, "ag_status": "SCORED", "source": "v1_reuse"}
        scored[vid] = merged

    atog_need = [
        v
        for v in variants
        if v["ref"] == "A" and v["alt"] == "G" and v["variant_id"] not in scored
    ]
    other_pool = [
        v
        for v in variants
        if not (v["ref"] == "A" and v["alt"] == "G") and v["variant_id"] not in scored
    ]
    rng = random.Random(SEED)
    rng.shuffle(other_pool)
    random_need = other_pool[: args.random_n]

    to_score = atog_need + random_need
    # dedupe preserve order
    seen = set()
    uniq = []
    for v in to_score:
        if v["variant_id"] in seen:
            continue
        seen.add(v["variant_id"])
        uniq.append(v)
    to_score = uniq
    if args.max_new and len(to_score) > args.max_new:
        # prioritize all A→G first
        atog_ids = {v["variant_id"] for v in atog_need}
        atog_first = [v for v in to_score if v["variant_id"] in atog_ids]
        rest = [v for v in to_score if v["variant_id"] not in atog_ids]
        to_score = (atog_first + rest)[: args.max_new]

    print(
        f"need A>G={len(atog_need)} random={len(random_need)} "
        f"to_score={len(to_score)}",
        flush=True,
    )

    n_ok = n_fail = 0
    if not args.skip_ag:
        for i, v in enumerate(to_score, 1):
            vid = v["variant_id"]
            print(f"AG [{i}/{len(to_score)}] {vid}", flush=True)
            try:
                s = score_variant_deltas(VariantSpec("chr11", v["pos"], v["ref"], v["alt"]))
                row = {
                    **v,
                    "ag_chip_tf_mae": s.get("chip_tf_mae"),
                    "ag_contact_mae": s.get("contact_mae_all"),
                    "ag_primary": s.get("primary_score"),
                    "ag_status": "SCORED",
                    "source": "v2_expand",
                }
                scored[vid] = row
                n_ok += 1
            except Exception as exc:
                n_fail += 1
                print(f"  FAIL {type(exc).__name__}: {exc}")
            time.sleep(0.35)

    scored_list = list(scored.values())
    c1 = next(v for v in scored_list if v.get("is_c1"))
    chips = sorted(
        [
            (float(v["ag_chip_tf_mae"]), v["variant_id"], bool(v.get("is_c1")))
            for v in scored_list
            if v.get("ag_chip_tf_mae") is not None
        ],
        reverse=True,
    )
    c1_chip = float(c1["ag_chip_tf_mae"])
    rank = 1 + sum(1 for s, _, _ in chips if s > c1_chip)
    pct = rank / len(chips)
    n_near = sum(1 for s, _, is_c1 in chips if (not is_c1) and s >= 0.9 * c1_chip)
    other_atog = [
        float(v["ag_chip_tf_mae"])
        for v in scored_list
        if v.get("ref") == "A"
        and v.get("alt") == "G"
        and not v.get("is_c1")
        and v.get("ag_chip_tf_mae") is not None
    ]
    mean_ag = sum(other_atog) / len(other_atog) if other_atog else None

    kills = []
    if pct > 0.05:
        kills.append("S1_not_top5pct")
    if n_near >= 20:
        kills.append("S2_many_near_peers")
    if mean_ag is not None and mean_ag >= c1_chip:
        kills.append("S3_AtoG_composition")

    overall = "ALLELE_LEAN_RETAINED" if not kills else "UNRESOLVED_OR_WINDOW_ARTIFACT"
    stats = {
        "n_ag_scored": len(chips),
        "n_prior_reuse": sum(1 for v in scored_list if v.get("source") == "v1_reuse"),
        "n_new_ok": n_ok,
        "n_new_fail": n_fail,
        "n_AtoG_scored_incl_c1": 1 + len(other_atog),
        "n_AtoG_other": len(other_atog),
        "c1_chip_tf": c1_chip,
        "c1_contact": float(c1.get("ag_contact_mae") or 0),
        "c1_rank": rank,
        "c1_percentile_from_top": pct,
        "n_within_90pct_c1": n_near,
        "mean_other_AtoG_chip": mean_ag,
        "top5": [{"chip": a, "id": b, "is_c1": c} for a, b, c in chips[:5]],
        "seed_random": SEED,
        "random_n_requested": args.random_n,
    }

    report = {
        "status": "C1_SATMUT_EXPAND_V2_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claim": "P2_SATMUT_EXPAND_CLAIM_v1.md",
        "window": f"chr11:{WIN_START1}-{WIN_END1}",
        "n_all_subst": len(variants),
        "pre_registered": {
            "kill_S1": "C1 not in top 5% by chip_tf among AG-scored set",
            "kill_S2": ">=20 subst with chip_tf >= 0.9 * C1",
            "kill_S3": "mean A>G chip_tf in window >= C1 chip_tf",
            "primary_metric": "ag_chip_tf_mae",
            "expand": "all A→G + random 100; reuse v1",
        },
        "overall": overall,
        "kills": kills,
        "stats": stats,
        "variants_ag": scored_list,
    }
    out_json = OUT / "C1_saturation_mutagenesis_v2.json"
    out_json.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    md_lines = [
        "# C1 saturation mutagenesis v2 (expand AG)",
        "",
        f"**Overall:** `{overall}`  ",
        f"**Kills:** {kills or 'none'}  ",
        f"**AG scored:** {stats['n_ag_scored']} / {len(variants)} possible "
        f"(reuse {stats['n_prior_reuse']} + new {stats['n_new_ok']})",
        f"**A→G covered:** {stats['n_AtoG_scored_incl_c1']} / 60 sites (incl. C1)",
        "",
        "## Claim",
        "",
        "`P2_SATMUT_EXPAND_CLAIM_v1.md` — same S1/S2/S3 as v1; expanded universe.",
        "",
        "## Stats",
        "",
        "```json",
        json.dumps(stats, indent=2),
        "```",
        "",
        "## Plain language",
        "",
        "Добавили все остальные A→G в окне 301 bp и 100 случайных замен. "
        "Если C1 всё ещё редкий выброс на этом фоне — аллельный lean держится; "
        "если толпа соседей или средний A→G догоняет — это артефакт окна.",
        "",
        "## What this does NOT mean",
        "",
        "- Not wet-lab proof",
        "- Not full 903 AG",
        "- Not holdout / Stage-3 / oligo GO",
        "",
        f"JSON: `{out_json.name}`",
        "",
    ]
    (OUT / "C1_saturation_mutagenesis_v2.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(json.dumps({"overall": overall, "kills": kills, "stats": stats}, indent=2))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
