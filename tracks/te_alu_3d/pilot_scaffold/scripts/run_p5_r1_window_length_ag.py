#!/usr/bin/env python3
"""P5 R1 — AG signed CHIP_TF direction across 16kb / 100kb / 500kb.

Pre-registered: 09_outputs/prospective/P5_R1_CLAIM_v1.md
Does not touch holdout. Does not order oligos.
"""

from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT_PS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_PS))

from adapters.ag_contact_delta import VariantSpec  # noqa: E402
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed  # noqa: E402
from load_project_env import alphagenome_api_key, load_project_env  # noqa: E402

OUT = ROOT_PS.parent / "09_outputs" / "prospective"

ALLELES = [
    {"id": "C1", "variant_id": "chr11:62753923:A:G", "role": "TEMPLATE_DEV"},
    {"id": "C2", "variant_id": "chr11:62753923:A:T", "role": "activity_m3"},
    {"id": "C3", "variant_id": "chr11:72434037:C:T", "role": "activity_m3"},
    {"id": "N3", "variant_id": "chr11:108009167:T:C", "role": "matched_negative"},
]

# AG-supported ladder (proxy for 301 / 1kb / 2kb reporter windows)
LENGTHS = [
    ("proxy_short_16kb", "SEQUENCE_LENGTH_16KB"),
    ("proxy_mid_100kb", "SEQUENCE_LENGTH_100KB"),
    ("proxy_long_500kb", "SEQUENCE_LENGTH_500KB"),
]


def _parse(vid: str) -> VariantSpec:
    c, p, r, a = vid.split(":")
    return VariantSpec(c, int(p), r, a)


def score_signed(variant: VariantSpec, sequence_length_key: str) -> dict[str, Any]:
    from alphagenome.data import genome
    from alphagenome.models import dna_client

    key = alphagenome_api_key()
    if not key:
        raise RuntimeError("no ALPHAGENOME_API_KEY")
    model = dna_client.create(key)
    width = getattr(dna_client, sequence_length_key)
    gv = genome.Variant(
        chromosome=variant.chrom,
        position=variant.pos,
        reference_bases=variant.ref,
        alternate_bases=variant.alt,
    )
    interval = gv.reference_interval.resize(width)
    out = model.predict_variant(
        interval=interval,
        variant=gv,
        ontology_terms=None,
        requested_outputs=[
            dna_client.OutputType.CONTACT_MAPS,
            dna_client.OutputType.CHIP_TF,
        ],
    )
    ref_tf = np.asarray(out.reference.chip_tf.values, dtype=np.float64)
    alt_tf = np.asarray(out.alternate.chip_tf.values, dtype=np.float64)
    tf_diff = alt_tf - ref_tf
    ref_cm = np.asarray(out.reference.contact_maps.values, dtype=np.float64)
    alt_cm = np.asarray(out.alternate.contact_maps.values, dtype=np.float64)
    cm_diff = alt_cm - ref_cm
    signed_tf = float(np.mean(tf_diff))
    signed_cm = float(np.mean(cm_diff))
    return {
        "sequence_length_key": sequence_length_key,
        "interval_width_bp": int(interval.end - interval.start),
        "chip_tf_mean_signed": signed_tf,
        "chip_tf_mae": float(np.mean(np.abs(tf_diff))),
        "contact_mean_signed": signed_cm,
        "contact_mae_all": float(np.mean(np.abs(cm_diff))),
        "sign_chip": int(np.sign(signed_tf)) if signed_tf != 0 else 0,
    }


def _sign(x: float, eps: float = 1e-12) -> int:
    if abs(x) < eps:
        return 0
    return 1 if x > 0 else -1


def flips(signs: list[int]) -> list[bool]:
    """Adjacent flips ignoring zeros as inconclusive steps."""
    out = []
    for a, b in zip(signs, signs[1:]):
        if a == 0 or b == 0:
            out.append(False)  # zero = no conclusive flip
        else:
            out.append(a != b)
    return out


def verdict_c1(adj_flips: list[bool]) -> str:
    n = sum(1 for x in adj_flips if x)
    if n >= 2:
        return "R1_HARD"
    if n == 1:
        return "R1_SOFT"
    return "R1_PASS"


def main() -> int:
    load_project_env()
    assert holdout_is_sealed()
    assert_not_scoring_holdout(OUT / "p5_r1_ok.tsv")
    if not alphagenome_api_key():
        raise SystemExit("no AG key")

    results = []
    for alle in ALLELES:
        spec = _parse(alle["variant_id"])
        print(f"== {alle['id']} {spec.variant_id}", flush=True)
        windows = {}
        for wname, lkey in LENGTHS:
            print(f"  {wname} ({lkey})", flush=True)
            try:
                s = score_signed(spec, lkey)
                s["status"] = "OK"
            except Exception as exc:
                s = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
                print("   FAIL", s["error"])
            windows[wname] = s
            time.sleep(0.35)

        ordered = [windows[n].get("chip_tf_mean_signed") for n, _ in LENGTHS]
        signs = [
            _sign(v) if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else 0
            for v in ordered
        ]
        adj = flips(signs)
        row = {
            **alle,
            "windows": windows,
            "signs_chip_tf": {
                LENGTHS[i][0]: signs[i] for i in range(len(LENGTHS))
            },
            "adjacent_flips": {
                "short_to_mid": adj[0] if len(adj) > 0 else None,
                "mid_to_long": adj[1] if len(adj) > 1 else None,
            },
            "n_adjacent_flips": int(sum(1 for x in adj if x)),
        }
        if alle["id"] == "C1":
            row["verdict"] = verdict_c1(adj)
        elif alle["id"] == "N3":
            mags = [
                abs(windows[n].get("chip_tf_mean_signed") or 0)
                for n, _ in LENGTHS
                if windows[n].get("status") == "OK"
            ]
            row["verdict"] = (
                "N3_UNSTABLE"
                if sum(1 for x in adj if x) >= 1 and (max(mags) if mags else 0) > 0.05
                else "N3_OK_OR_MILD"
            )
        else:
            row["verdict"] = (
                "FLIP_NOTED" if sum(1 for x in adj if x) else "STABLE_NOTED"
            )
        results.append(row)

    c1 = next(r for r in results if r["id"] == "C1")
    branch_b = {
        "R1_HARD": "Branch B exploratory only — AG activity sign not length-stable",
        "R1_SOFT": "Branch B conditional — one adjacent AG context flip; disclose",
        "R1_PASS": "AG context-length proxy does not kill Branch B primary",
    }[c1["verdict"]]

    doc = {
        "status": "P5_R1_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claim": "P5_R1_CLAIM_v1.md",
        "proxy_note": "AG lengths 16kb/100kb/500kb stand in for reporter 301/1kb/2kb",
        "holdout_sealed": True,
        "c1_verdict": c1["verdict"],
        "branch_b_consequence": branch_b,
        "results": results,
    }
    out_json = OUT / "P5_R1_window_length_ag_v1.json"
    out_json.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")

    lines = [
        "# P5 R1 — AG context-length sign stability",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Status:** `{doc['status']}`",
        f"**Claim:** `P5_R1_CLAIM_v1.md`",
        f"**C1 verdict:** **`{c1['verdict']}`**",
        f"**Branch B:** {branch_b}",
        "",
        "## Proxy",
        "",
        "Reporter windows 301/1kb/2kb are **not** AG-native.",
        "Used `16kb / 100kb / 500kb` `predict_variant` lengths instead.",
        "",
        "## Results (signed mean CHIP_TF)",
        "",
        "| Allele | 16kb | 100kb | 500kb | flips | Verdict |",
        "|--------|-----:|------:|------:|------:|---------|",
    ]
    for r in results:
        vals = []
        for n, _ in LENGTHS:
            w = r["windows"][n]
            if w.get("status") != "OK":
                vals.append("FAIL")
            else:
                vals.append(f"{w['chip_tf_mean_signed']:+.4f}")
        lines.append(
            f"| {r['id']} | {vals[0]} | {vals[1]} | {vals[2]} | "
            f"{r['n_adjacent_flips']} | **{r['verdict']}** |"
        )

    lines += [
        "",
        "## Plain language",
        "",
        "Проверяем, меняет ли AlphaGenome **знак** эффекта ALT vs REF, "
        "когда контекст узкий / средний / широкий. "
        "Если знак прыгает на обеих ступеньках у C1 — reporter Branch B "
        "нельзя считать устойчивым к длине даже на desk-прокси.",
        "",
        "## What this does NOT mean",
        "",
        "- Not wet transfection of 301 bp constructs",
        "- Not holdout / Stage-3 change / oligo GO",
        "- MAE magnitude alone cannot pass R1 — sign ladder is primary",
        "",
    ]
    out_md = OUT / "P5_R1_window_length_ag_v1.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"c1_verdict": c1["verdict"], "wrote": str(out_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
