"""Unpack AlphaGenome CHIP_TF / CONTACT channels for C1 (chr11:62753923:A:G).

Does not score holdout. Auth via ALPHAGENOME_API_KEY.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "09_outputs" / "prospective"


def main() -> int:
    from load_project_env import alphagenome_api_key, load_project_env
    from alphagenome.data import genome
    from alphagenome.models import dna_client

    load_project_env()
    key = alphagenome_api_key()
    if not key:
        raise SystemExit("Set ALPHAGENOME_API_KEY in .env or environment")

    model = dna_client.create(key)
    variant = genome.Variant(
        chromosome="chr11", position=62753923, reference_bases="A", alternate_bases="G"
    )
    interval = variant.reference_interval.resize(dna_client.SEQUENCE_LENGTH_100KB)
    out = model.predict_variant(
        interval=interval,
        variant=variant,
        ontology_terms=None,
        requested_outputs=[dna_client.OutputType.CHIP_TF, dna_client.OutputType.CONTACT_MAPS],
    )

    ref = np.asarray(out.reference.chip_tf.values, dtype=np.float64)
    alt = np.asarray(out.alternate.chip_tf.values, dtype=np.float64)
    diff = alt - ref
    md = out.reference.chip_tf.metadata
    length, n_tracks = diff.shape
    center = length // 2
    half = 16
    sl = slice(max(0, center - half), min(length, center + half + 1))

    track_mae = np.mean(np.abs(diff), axis=0)
    track_mae_local = np.mean(np.abs(diff[sl, :]), axis=0)
    track_mean_local = np.mean(diff[sl, :], axis=0)
    track_max_abs_local = np.max(np.abs(diff[sl, :]), axis=0)

    top_idx = np.argsort(-track_mae_local)[:30]
    chip_rows = []
    for rank, i in enumerate(top_idx, 1):
        meta = {
            c: (
                None
                if isinstance(md.iloc[int(i)][c], float) and np.isnan(md.iloc[int(i)][c])
                else str(md.iloc[int(i)][c])
            )
            for c in md.columns
        }
        chip_rows.append(
            {
                "rank": rank,
                "track_index": int(i),
                "mae_local": float(track_mae_local[i]),
                "mean_signed_local": float(track_mean_local[i]),
                "max_abs_local": float(track_max_abs_local[i]),
                "mae_global": float(track_mae[i]),
                "metadata": meta,
            }
        )

    # Aggregate by TF name / biosample when columns exist
    def pick(meta: dict, keys: list[str]) -> str:
        for k in keys:
            if meta.get(k):
                return str(meta[k])
        return ""

    by_tf: dict[str, list[float]] = {}
    for r in chip_rows:
        tf = pick(
            r["metadata"],
            ["Target", "target", "tf_name", "name", "Assay title"],
        )
        by_tf.setdefault(tf or f"track_{r['track_index']}", []).append(r["mae_local"])
    tf_agg = sorted(
        (
            {"label": k, "n_top30": len(v), "mean_mae_local": float(np.mean(v)), "max_mae_local": float(np.max(v))}
            for k, v in by_tf.items()
        ),
        key=lambda x: -x["max_mae_local"],
    )

    crm = np.asarray(out.reference.contact_maps.values, dtype=np.float64)
    cam = np.asarray(out.alternate.contact_maps.values, dtype=np.float64)
    cmd = cam - crm
    cmd_md = out.reference.contact_maps.metadata
    c_mae = np.mean(np.abs(cmd), axis=(0, 1))
    contact_rows = []
    for rank, i in enumerate(np.argsort(-c_mae)[:12], 1):
        contact_rows.append(
            {
                "rank": rank,
                "track_index": int(i),
                "mae": float(c_mae[i]),
                "biosample_name": str(cmd_md.iloc[int(i)].get("biosample_name", "")),
                "name": str(cmd_md.iloc[int(i)].get("name", "")),
                "ontology_curie": str(cmd_md.iloc[int(i)].get("ontology_curie", "")),
            }
        )

    # Mechanistic lean from top TF labels
    top_labels = " ".join(r["metadata"].get("name", "") or "" for r in chip_rows[:10]).upper()
    ctcfish = any(x in top_labels for x in ("CTCF", "RAD21", "SMC3", "SMC1"))
    activityish = any(
        x in top_labels for x in ("H3K27AC", "H3K4ME", "POLR2", "EP300", "CREBBP", "ATAC")
    )
    if ctcfish and not activityish:
        lean = "M1_lean_CTCF_cohesin_channels"
    elif activityish and not ctcfish:
        lean = "M3_lean_activity_channels"
    elif ctcfish and activityish:
        lean = "MIXED_M1_M3_channels"
    else:
        lean = "UNCLEAR_inspect_top_tracks"

    report = {
        "status": "C1_CHANNEL_UNPACK_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "C1",
        "variant_id": "chr11:62753923:A:G",
        "interval_width_bp": int(interval.end - interval.start),
        "chip_tf_shape": [int(length), int(n_tracks)],
        "local_window_bins": {"center": center, "half_width": half},
        "summary_chip_tf_mae_global": float(np.mean(np.abs(diff))),
        "summary_chip_tf_mae_local": float(np.mean(np.abs(diff[sl, :]))),
        "mechanism_channel_lean": lean,
        "chip_tf_top30_local_mae": chip_rows,
        "chip_tf_label_aggregate_top30": tf_agg[:20],
        "contact_maps_top12_mae": contact_rows,
        "metadata_columns": list(md.columns),
        "holdout_scored": False,
        "next": [
            "If lean M1: prioritize CTCF occupancy assay in G5 design",
            "If lean M3: reporter/activity competitor mandatory before architecture claim",
            "Still need HUDEP-2 G4; no wet-lab GO",
        ],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "c1_chip_tf_channel_unpack.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def short_label(meta: dict) -> str:
        name = meta.get("name") or meta.get("Target") or meta.get("Assay title") or "?"
        bio = meta.get("biosample_name") or meta.get("Biosample term name") or ""
        return f"{name} @ {bio}".strip(" @")

    lines = [
        "# C1 CHIP_TF / contact channel unpack",
        "",
        f"**Variant:** `chr11:62753923:A:G` (C1)  ",
        f"**Date:** {report['timestamp'][:10]}  ",
        f"**Window:** {report['interval_width_bp']} bp  ",
        f"**Channel lean:** `{lean}`  ",
        "**Holdout:** not scored",
        "",
        "## Top CHIP_TF tracks (local ±16 bins MAE)",
        "",
        "| Rank | Local MAE | Signed mean | Label |",
        "|-----:|----------:|------------:|-------|",
    ]
    for r in chip_rows[:15]:
        lines.append(
            f"| {r['rank']} | {r['mae_local']:.4f} | {r['mean_signed_local']:+.4f} | "
            f"{short_label(r['metadata'])} |"
        )
    lines += [
        "",
        "## Top contact-map channels (global MAE)",
        "",
        "| Rank | MAE | Biosample | Acc |",
        "|-----:|----:|-----------|-----|",
    ]
    for r in contact_rows[:8]:
        lines.append(
            f"| {r['rank']} | {r['mae']:.4f} | {r['biosample_name']} | {r['name']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        f"- Mechanism channel lean: **{lean}**",
        "- Complements G2 Arm B (AG ≫ motif): TF/contact channels say *what* AG is moving.",
        "- Still **IMMATURE**: proxy G4 only; no HUDEP-2 contact; no G9.",
        "",
        f"Artifact: `{out_json.name}`",
        "",
    ]
    (OUT / "c1_chip_tf_channel_unpack.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "lean": lean,
                "top5": [
                    {
                        "rank": r["rank"],
                        "mae_local": r["mae_local"],
                        "label": short_label(r["metadata"]),
                    }
                    for r in chip_rows[:5]
                ],
                "out": str(out_json),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
