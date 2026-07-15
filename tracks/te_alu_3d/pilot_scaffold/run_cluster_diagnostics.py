"""Cluster-aware permutation diagnostics on existing HBB scores (development only).

Collapses variants → approximate TE instances (family + 10kb block), then
block-permutes at the TE-instance level. Does NOT authorize enrichment claims.

Usage:
  python run_cluster_diagnostics.py
  python run_cluster_diagnostics.py --estimand T --n-perm 500
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from permutation_test import block_permutation_null, delta_mad

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "09_outputs" / "pilot_chr11"


def _parse_vid(vid: str) -> tuple[str, int]:
    parts = vid.split(":")
    return parts[0], int(parts[1])


def _te_key(vid: str, te_family: str) -> str:
    chrom, pos = _parse_vid(vid)
    block = (pos // 10_000) * 10_000
    fam = te_family or "NA"
    return f"{chrom}:{block}:{fam}"


def _load_scores(path: Path) -> dict[str, dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            by_id[row["variant_id"]] = row
    return by_id


def _load_manifest_a(path: Path, estimand: str) -> list[tuple[str, list[str]]]:
    pairs: list[tuple[str, list[str]]] = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("estimand") != estimand:
                continue
            if row.get("control_level", "A") != "A":
                continue
            ctrls = [c for c in (row.get("control_ids") or "").split(";") if c]
            pairs.append((row["test_variant_id"], ctrls))
    return pairs


def cluster_sets(
    pairs: list[tuple[str, list[str]]],
    scores: dict[str, dict[str, str]],
) -> tuple[list[tuple[float, list[float]]], dict[str, Any]]:
    """Collapse variant-level matched sets → TE-instance level."""
    buckets: dict[str, list[tuple[float, list[float]]]] = defaultdict(list)
    for tid, cids in pairs:
        srow = scores.get(tid)
        if not srow:
            continue
        try:
            te_s = float(srow["score"])
        except (KeyError, ValueError):
            continue
        ctrl_s: list[float] = []
        for cid in cids:
            crow = scores.get(cid)
            if not crow:
                continue
            try:
                ctrl_s.append(float(crow["score"]))
            except (KeyError, ValueError):
                continue
        if not ctrl_s:
            continue
        key = _te_key(tid, srow.get("te_family") or "")
        buckets[key].append((te_s, ctrl_s))

    clustered: list[tuple[float, list[float]]] = []
    for _key, items in buckets.items():
        te_med = statistics.median([t for t, _ in items])
        # pool controls from all variants in the TE copy (dedupe by value list flatten)
        ctrl_all = [c for _, cs in items for c in cs]
        if not ctrl_all:
            continue
        clustered.append((te_med, ctrl_all))

    meta = {
        "n_variant_sets_input": len(pairs),
        "n_TE_clusters": len(clustered),
        "inflation_variants_over_clusters": (
            len(pairs) / max(len(clustered), 1)
        ),
        "cluster_keys_head": list(buckets.keys())[:10],
    }
    return clustered, meta


def run(estimand: str, n_perm: int, seed: int) -> dict[str, Any]:
    scores = _load_scores(OUT / f"disruption_scores_{estimand}.csv")
    pairs = _load_manifest_a(OUT / f"control_manifest_{estimand}.csv", estimand)
    # variant-level sets
    var_sets: list[tuple[float, list[float]]] = []
    for tid, cids in pairs:
        if tid not in scores:
            continue
        te_s = float(scores[tid]["score"])
        ctrl_s = [float(scores[c]["score"]) for c in cids if c in scores]
        if ctrl_s:
            var_sets.append((te_s, ctrl_s))

    clustered, meta = cluster_sets(pairs, scores)
    rng = random.Random(seed)
    var_perm = block_permutation_null(var_sets, n_perm=n_perm, rng=rng)
    cl_perm = block_permutation_null(clustered, n_perm=n_perm, rng=random.Random(seed + 1))

    te_v = [t for t, _ in var_sets]
    ctrl_v = [c for _, cs in var_sets for c in cs]
    te_c = [t for t, _ in clustered]
    ctrl_c = [c for _, cs in clustered for c in cs]

    return {
        "role": "development_diagnostics_only",
        "estimand": estimand,
        "scorer": "ctcf_pwm_delta_v1.1",
        "claim_authorized": False,
        "variant_level": {
            "n_sets": len(var_sets),
            "median_delta": var_perm.get("observed_effect_median_delta"),
            "delta_MAD": var_perm.get("observed_delta_MAD"),
            "perm_p": var_perm.get("perm_p"),
            "raw_delta_MAD_recompute": delta_mad(te_v, ctrl_v) if te_v and ctrl_v else None,
        },
        "TE_instance_cluster": {
            **meta,
            "median_delta": cl_perm.get("observed_effect_median_delta"),
            "delta_MAD": cl_perm.get("observed_delta_MAD"),
            "perm_p": cl_perm.get("perm_p"),
            "raw_delta_MAD_recompute": delta_mad(te_c, ctrl_c) if te_c and ctrl_c else None,
            "n_perm": n_perm,
        },
        "interpretation": (
            "If cluster perm_p stays non-significant while variant N is huge, "
            "variant-level tests were inflated by many SNVs per TE copy."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimand", choices=["T", "C"], default="T")
    ap.add_argument("--n-perm", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    results = {
        "T": run("T", args.n_perm, args.seed),
        "C": run("C", args.n_perm, args.seed + 17),
    }
    out = OUT / "cluster_diagnostics.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
