#!/usr/bin/env python3
"""Freeze G9 common Alu/SVA x CTCF panel BEFORE any eQTL peek.

Writes g9_common_alu_ctcf_panel_freeze_v1.json (+ sha256).
No eQTL fields allowed in the freeze artifact.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))

from fetch_dual_track_inputs import _post_graphql  # noqa: E402
from holdout_guard import holdout_is_sealed  # noqa: E402
from g9_eqtl_lib import (  # noqa: E402
    AF_MAX,
    AF_MIN,
    CTCF_CTRL_PAD_BP,
    PANEL_CAP,
    SEED,
    cap_sorted,
    excluded_pos,
    in_expanded_peaks,
    interval_contains,
    load_bed_intervals,
    match_controls_by_af_decile,
    variant_id,
)

DATA = ROOT / "data"
OUT = ROOT.parent / "09_outputs" / "prospective"
CTCF = DATA / "ctcf_HUDEP2_peaks.bed"
TE = DATA / "repeatmasker_chr11_alu_sva.bed"
FREEZE = OUT / "g9_common_alu_ctcf_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g9_common_alu_ctcf_panel_freeze_v1.json.sha256"

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


def _gnomad_common_in_interval(start: int, end: int) -> list[dict]:
    """Fetch common SNVs with pos in (start, end] on chr11."""
    api_start = max(1, start + 1)
    api_stop = end
    if api_stop < api_start:
        return []
    data = None
    for attempt in range(6):
        try:
            data = _post_graphql(
                GQL, {"chrom": "11", "start": api_start, "stop": api_stop}
            )
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
        if excluded_pos(pos):
            continue
        if not (start < pos <= end):
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
        if af_f is None or af_f < AF_MIN or af_f > AF_MAX:
            continue
        out.append(
            {
                "chrom": "chr11",
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "af": af_f,
            }
        )
    return out


def _peak_te_overlaps(
    ctcf: list[tuple[int, int, str]], te: list[tuple[int, int, str]]
) -> list[dict]:
    hits: list[dict] = []
    for cs, ce, _ in ctcf:
        mid = (cs + ce) // 2
        if excluded_pos(mid) or excluded_pos(cs) or excluded_pos(ce):
            continue
        for ts, te_, name in te:
            # overlap of intervals
            os_ = max(cs, ts)
            oe = min(ce, te_)
            if os_ < oe:
                hits.append(
                    {
                        "peak_start": cs,
                        "peak_end": ce,
                        "te_start": ts,
                        "te_end": te_,
                        "overlap_start": os_,
                        "overlap_end": oe,
                        "te_family": name,
                    }
                )
                break
    return hits


def _sample_alu_control_windows(
    te: list[tuple[int, int, str]],
    ctcf: list[tuple[int, int, str]],
    *,
    max_windows: int = 400,
) -> list[tuple[int, int, str]]:
    """Alu/SVA intervals away from CTCF±pad, deterministic order."""
    windows: list[tuple[int, int, str]] = []
    for ts, te_, name in sorted(te, key=lambda x: (x[0], x[1], x[2])):
        mid = (ts + te_) // 2
        if excluded_pos(mid) or excluded_pos(ts) or excluded_pos(te_):
            continue
        if in_expanded_peaks(ctcf, mid, CTCF_CTRL_PAD_BP):
            continue
        # also skip if interval overlaps expanded CTCF
        skip = False
        for cs, ce, _ in ctcf:
            if max(ts, cs - CTCF_CTRL_PAD_BP) < min(te_, ce + CTCF_CTRL_PAD_BP):
                skip = True
                break
        if skip:
            continue
        windows.append((ts, te_, name))
        if len(windows) >= max_windows:
            break
    return windows


def main() -> int:
    assert holdout_is_sealed(), "holdout must be SEALED"
    ctcf = load_bed_intervals(CTCF)
    te = load_bed_intervals(TE)
    overlaps = _peak_te_overlaps(ctcf, te)
    print(f"ctcf_x_alu_overlaps={len(overlaps)}", flush=True)

    case_raw: list[dict] = []
    seen_case: set[str] = set()
    # Deterministic order; stop GraphQL once we have enough raw cases to fill cap.
    overlaps_sorted = sorted(
        overlaps, key=lambda h: (h["overlap_start"], h["overlap_end"], h["te_family"])
    )
    for i, h in enumerate(overlaps_sorted):
        if len(case_raw) >= PANEL_CAP * 2:
            print(f"  early-stop cases at overlap {i}/{len(overlaps_sorted)}", flush=True)
            break
        print(
            f"  case query {i + 1}/{len(overlaps_sorted)} "
            f"{h['overlap_start']}-{h['overlap_end']} ({h['te_family']})",
            flush=True,
        )
        for v in _gnomad_common_in_interval(h["overlap_start"], h["overlap_end"]):
            # double-check both memberships
            if interval_contains(ctcf, v["pos"]) is None:
                continue
            te_hit = interval_contains(te, v["pos"])
            if te_hit is None:
                continue
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in seen_case:
                continue
            seen_case.add(vid)
            case_raw.append(
                {
                    **v,
                    "variant_id": vid,
                    "role": "CASE_CTCF_ALU",
                    "te_family": te_hit[2],
                    "peak_start": h["peak_start"],
                    "peak_end": h["peak_end"],
                }
            )

    cases = cap_sorted(case_raw, PANEL_CAP)
    # re-attach fields after cap (cap_sorted keeps dicts)
    print(f"n_case_raw={len(case_raw)} n_case_capped={len(cases)}", flush=True)

    ctrl_windows = _sample_alu_control_windows(te, ctcf)
    print(f"ctrl_windows={len(ctrl_windows)}", flush=True)
    ctrl_pool: list[dict] = []
    seen_ctrl: set[str] = set()
    for i, (ts, te_, name) in enumerate(ctrl_windows):
        if len(ctrl_pool) >= PANEL_CAP * 5:
            break
        print(f"  ctrl query {i + 1}/{len(ctrl_windows)} {ts}-{te_}", flush=True)
        for v in _gnomad_common_in_interval(ts, te_):
            if in_expanded_peaks(ctcf, v["pos"], CTCF_CTRL_PAD_BP):
                continue
            te_hit = interval_contains(te, v["pos"])
            if te_hit is None:
                continue
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in seen_ctrl or vid in seen_case:
                continue
            seen_ctrl.add(vid)
            ctrl_pool.append(
                {
                    **v,
                    "variant_id": vid,
                    "role": "CTRL_ALU_NONCTCF",
                    "te_family": te_hit[2],
                    "peak_start": None,
                    "peak_end": None,
                }
            )

    print(f"n_ctrl_pool={len(ctrl_pool)}", flush=True)
    controls = match_controls_by_af_decile(
        cases, ctrl_pool, seed=SEED, cap=min(len(cases), PANEL_CAP)
    )
    for c in controls:
        c["role"] = "CTRL_ALU_NONCTCF"
        c.setdefault("variant_id", variant_id(c["chrom"], c["pos"], c["ref"], c["alt"]))
        c.setdefault("peak_start", None)
        c.setdefault("peak_end", None)

    payload = {
        "freeze_id": "g9_common_alu_ctcf_panel_freeze_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "G9_common_alu_ctcf_blood_eqtl_CLAIM_v1.md",
        "holdout_sealed": True,
        "af_band": [AF_MIN, AF_MAX],
        "panel_cap": PANEL_CAP,
        "ctcf_ctrl_pad_bp": CTCF_CTRL_PAD_BP,
        "seed": SEED,
        "n_case": len(cases),
        "n_ctrl": len(controls),
        "n_case_raw_before_cap": len(case_raw),
        "n_ctrl_pool": len(ctrl_pool),
        "n_ctcf_alu_overlaps": len(overlaps),
        "variants": cases + controls,
        "eqtl_fields_forbidden": True,
    }
    # sanity: no eQTL keys
    for v in payload["variants"]:
        for bad in ("pvalue", "eqtl_hit", "gene_id", "beta"):
            assert bad not in v, f"eQTL leak in freeze: {bad}"

    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    FREEZE.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    FREEZE_SHA.write_text(digest + "\n", encoding="utf-8")
    print(f"wrote {FREEZE}")
    print(f"sha256 {digest}")
    print(f"n_case={len(cases)} n_ctrl={len(controls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
