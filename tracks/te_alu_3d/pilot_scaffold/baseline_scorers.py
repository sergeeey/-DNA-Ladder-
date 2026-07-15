"""Transparent comparator baselines for ARCHCODE-PROSPECTIVE (not primary scorers).

- motif_only: CTCF PWM Δ mapped to [0,1] WITHOUT peak boost
- distance_only: 1 / (1 + dist_to_CTCF_peak)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from build_matched_controls import _dist_to_nearest
from ctcf_pwm_scorer import ctcf_pwm_disruption
from qc_filters import VariantRecord


def motif_only_score(
    v: VariantRecord,
    *,
    fasta_path: Path | None,
    peaks_path: Path,
) -> dict[str, Any]:
    """Motif-only comparator: map positive Δlog-odds to [0,1]; no peak boost."""
    out: dict[str, Any] = {
        "variant_id": v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}",
        "baseline": "motif_only",
        "score": None,
        "delta_logodds": None,
        "ok": False,
    }
    if fasta_path is None or not Path(fasta_path).exists():
        out["error"] = "missing_fasta"
        return out
    raw = ctcf_pwm_disruption(
        v.chrom,
        v.pos,
        v.ref,
        v.alt,
        fasta_path=Path(fasta_path),
        peaks_path=peaks_path,
    )
    if raw.get("error"):
        out["error"] = raw["error"]
        out["delta_logodds"] = raw.get("delta_logodds")
        return out
    delta = float(raw.get("delta_logodds") or 0.0)
    # Pure motif map — ignore peak proximity adjustments from ctcf_pwm_disruption
    if delta >= 0:
        score = 1.0 - math.exp(-0.5 * delta)
    else:
        score = 0.5 * math.exp(0.5 * delta)
    out["delta_logodds"] = delta
    out["score"] = float(max(0.0, min(1.0, score)))
    out["ok"] = True
    out["method"] = "motif_only_ctcf_pwm_no_peak_boost"
    return out


def distance_only_score(
    v: VariantRecord,
    *,
    peaks_path: Path,
) -> dict[str, Any]:
    """Distance-only comparator: closer to CTCF peak → higher score."""
    dist = _dist_to_nearest(v.chrom, v.pos, peaks_path)
    if dist >= 10**8:
        score = 0.0
        dist_out: int | None = None
    else:
        score = 1.0 / (1.0 + float(dist))
        dist_out = int(dist)
    return {
        "variant_id": v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}",
        "baseline": "distance_only",
        "score": float(score),
        "dist_ctcf": dist_out,
        "ok": True,
        "method": "inv_one_plus_dist",
    }


def score_variant_baselines(
    v: VariantRecord,
    *,
    fasta_path: Path | None,
    peaks_path: Path,
) -> dict[str, Any]:
    m = motif_only_score(v, fasta_path=fasta_path, peaks_path=peaks_path)
    d = distance_only_score(v, peaks_path=peaks_path)
    return {
        "variant_id": m["variant_id"],
        "motif_only": m.get("score"),
        "motif_only_ok": m.get("ok"),
        "motif_delta_logodds": m.get("delta_logodds"),
        "motif_error": m.get("error"),
        "distance_only": d.get("score"),
        "dist_ctcf": d.get("dist_ctcf"),
        "role": "comparator_not_primary",
    }
