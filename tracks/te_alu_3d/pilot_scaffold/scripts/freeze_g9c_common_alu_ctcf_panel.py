#!/usr/bin/env python3
"""Freeze G9c multi-chrom common Alu/SVA x CTCF panel BEFORE eQTL peek."""

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
    AF_MIN_G9B,
    CTCF_CTRL_PAD_BP,
    G9C_CHROMS,
    PANEL_CAP,
    SEED_G9C,
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
CTCF = DATA / "ctcf_HUDEP2_peaks_raw.bed"
TE = DATA / "repeatmasker_g9c_alu_sva.bed"
FREEZE = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json.sha256"
PROGRESS = OUT / "g9c_freeze_progress.txt"
AF_MIN = AF_MIN_G9B
SEED = SEED_G9C
CHROMS = set(G9C_CHROMS)

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


def _progress(msg: str) -> None:
    print(msg, flush=True)
    with PROGRESS.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")


def _gnomad_common(chrom: str, start: int, end: int) -> list[dict]:
    api_chrom = chrom.replace("chr", "")
    api_start = max(1, start + 1)
    api_stop = end
    if api_stop < api_start:
        return []
    data = None
    for attempt in range(6):
        try:
            data = _post_graphql(
                GQL, {"chrom": api_chrom, "start": api_start, "stop": api_stop}
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
        if excluded_pos(pos, chrom=chrom):
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
        out.append({"chrom": chrom, "pos": pos, "ref": ref, "alt": alt, "af": af_f})
    return out


def _overlaps(
    ctcf: list[tuple[str, int, int, str]], te: list[tuple[str, int, int, str]]
) -> list[dict]:
    te_by: dict[str, list[tuple[int, int, str]]] = {c: [] for c in CHROMS}
    for ch, s, e, name in te:
        te_by.setdefault(ch, []).append((s, e, name))
    for ch in te_by:
        te_by[ch].sort()
    hits: list[dict] = []
    for ch, cs, ce, _ in ctcf:
        if excluded_pos(cs, chrom=ch) or excluded_pos(ce, chrom=ch):
            continue
        for ts, te_, name in te_by.get(ch, []):
            if te_ <= cs:
                continue
            if ts >= ce:
                break
            os_ = max(cs, ts)
            oe = min(ce, te_)
            if os_ < oe:
                hits.append(
                    {
                        "chrom": ch,
                        "peak_start": cs,
                        "peak_end": ce,
                        "overlap_start": os_,
                        "overlap_end": oe,
                        "te_family": name,
                    }
                )
                break
    return hits


def _ctrl_windows(
    te: list[tuple[str, int, int, str]],
    ctcf: list[tuple[str, int, int, str]],
    *,
    max_windows: int = 800,
) -> list[tuple[str, int, int, str]]:
    ctcf_by: dict[str, list[tuple[int, int, str]]] = {c: [] for c in CHROMS}
    for ch, s, e, name in ctcf:
        ctcf_by.setdefault(ch, []).append((s, e, name))
    windows: list[tuple[str, int, int, str]] = []
    for ch, ts, te_, name in sorted(te, key=lambda x: (x[0], x[1], x[2], x[3])):
        mid = (ts + te_) // 2
        if excluded_pos(mid, chrom=ch):
            continue
        peaks = ctcf_by.get(ch, [])
        if in_expanded_peaks(peaks, mid, CTCF_CTRL_PAD_BP):
            continue
        skip = False
        for cs, ce, _ in peaks:
            if max(ts, cs - CTCF_CTRL_PAD_BP) < min(te_, ce + CTCF_CTRL_PAD_BP):
                skip = True
                break
        if skip:
            continue
        windows.append((ch, ts, te_, name))
        if len(windows) >= max_windows:
            break
    return windows


def main() -> int:
    assert holdout_is_sealed(), "holdout must be SEALED"
    OUT.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text("", encoding="utf-8")
    ctcf = load_bed_intervals(CTCF, chroms=CHROMS)
    te = load_bed_intervals(TE, chroms=CHROMS)
    overlaps = _overlaps(ctcf, te)
    _progress(
        f"chroms={sorted(CHROMS)} ctcf={len(ctcf)} te={len(te)} overlaps={len(overlaps)}"
    )

    case_raw: list[dict] = []
    seen: set[str] = set()
    overlaps_sorted = sorted(
        overlaps,
        key=lambda h: (h["chrom"], h["overlap_start"], h["overlap_end"], h["te_family"]),
    )
    for i, h in enumerate(overlaps_sorted):
        if len(case_raw) >= PANEL_CAP * 2:
            _progress(f"early-stop cases at {i}/{len(overlaps_sorted)}")
            break
        if i % 25 == 0 or i + 1 == len(overlaps_sorted):
            _progress(
                f"case {i + 1}/{len(overlaps_sorted)} n_case_raw={len(case_raw)}"
            )
        ch = h["chrom"]
        for v in _gnomad_common(ch, h["overlap_start"], h["overlap_end"]):
            if interval_contains(ctcf, v["pos"], chrom=ch) is None:
                continue
            te_hit = interval_contains(te, v["pos"], chrom=ch)
            if te_hit is None:
                continue
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in seen:
                continue
            seen.add(vid)
            case_raw.append(
                {
                    **v,
                    "variant_id": vid,
                    "role": "CASE_CTCF_ALU",
                    "te_family": te_hit[3] if len(te_hit) == 4 else te_hit[2],
                    "peak_start": h["peak_start"],
                    "peak_end": h["peak_end"],
                }
            )

    cases = sorted(case_raw, key=lambda v: (v["chrom"], v["pos"], v["ref"], v["alt"]))[
        :PANEL_CAP
    ]
    _progress(f"n_case_raw={len(case_raw)} n_case_capped={len(cases)}")

    windows = _ctrl_windows(te, ctcf)
    _progress(f"ctrl_windows={len(windows)}")
    ctrl_pool: list[dict] = []
    seen_c: set[str] = set()
    for i, (ch, ts, te_, name) in enumerate(windows):
        if len(ctrl_pool) >= PANEL_CAP * 5:
            break
        if i % 40 == 0:
            _progress(f"ctrl {i + 1}/{len(windows)} pool={len(ctrl_pool)}")
        peaks_chr = [(s, e, n) for c, s, e, n in ctcf if c == ch]
        for v in _gnomad_common(ch, ts, te_):
            if in_expanded_peaks(peaks_chr, v["pos"], CTCF_CTRL_PAD_BP):
                continue
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in seen_c or vid in seen:
                continue
            seen_c.add(vid)
            ctrl_pool.append(
                {
                    **v,
                    "variant_id": vid,
                    "role": "CTRL_ALU_NONCTCF",
                    "te_family": name,
                    "peak_start": None,
                    "peak_end": None,
                }
            )

    _progress(f"n_ctrl_pool={len(ctrl_pool)}")
    controls = match_controls_by_af_decile(
        cases,
        ctrl_pool,
        seed=SEED,
        cap=min(len(cases), PANEL_CAP),
        af_min=AF_MIN,
        af_max=AF_MAX,
    )
    for c in controls:
        c["role"] = "CTRL_ALU_NONCTCF"
        c.setdefault(
            "variant_id", variant_id(c["chrom"], c["pos"], c["ref"], c["alt"])
        )
        c.setdefault("peak_start", None)
        c.setdefault("peak_end", None)

    payload = {
        "freeze_id": "g9c_common_alu_ctcf_panel_freeze_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "G9c_common_alu_ctcf_blood_eqtl_CLAIM_v1.md",
        "holdout_sealed": True,
        "chromosomes": list(G9C_CHROMS),
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
    for v in payload["variants"]:
        for bad in ("pvalue", "eqtl_hit", "gene_id", "beta"):
            assert bad not in v

    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    FREEZE.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    FREEZE_SHA.write_text(digest + "\n", encoding="utf-8")
    _progress(f"wrote {FREEZE}")
    _progress(f"sha256 {digest}")
    _progress(f"n_case={len(cases)} n_ctrl={len(controls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
