#!/usr/bin/env python3
"""Freeze G12b: CTCF∩Alu cases (from G9c) vs CTCF∩non-Alu controls."""

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
    G9C_CHROMS,
    PANEL_CAP,
    excluded_pos,
    interval_contains,
    load_bed_intervals,
    match_controls_by_af_decile,
    variant_id,
)

DATA = ROOT / "data"
OUT = ROOT.parent / "09_outputs" / "prospective"
CTCF = DATA / "ctcf_HUDEP2_peaks_raw.bed"
TE = DATA / "repeatmasker_g9c_alu_sva.bed"
G9C_FREEZE = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json"
G9C_SHA = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json.sha256"
FREEZE = OUT / "g12b_ctcf_alu_vs_nonalu_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g12b_ctcf_alu_vs_nonalu_panel_freeze_v1.json.sha256"
PROGRESS = OUT / "g12b_freeze_progress.txt"
SEED = 20260724
CHROMS = set(G9C_CHROMS)
AF_MIN = AF_MIN_G9B

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


def _peak_has_te(
    chrom: str, start: int, end: int, te_by: dict[str, list[tuple[int, int, str]]]
) -> bool:
    for ts, te_, _ in te_by.get(chrom, []):
        if te_ <= start:
            continue
        if ts >= end:
            break
        if max(start, ts) < min(end, te_):
            return True
    return False


def main() -> int:
    assert holdout_is_sealed()
    OUT.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text("", encoding="utf-8")

    g9c_text = G9C_FREEZE.read_text(encoding="utf-8")
    g9c_sha = hashlib.sha256(g9c_text.encode("utf-8")).hexdigest()
    expected = G9C_SHA.read_text(encoding="utf-8").strip().split()[0]
    if g9c_sha != expected:
        raise RuntimeError("g9c freeze hash mismatch")
    g9c = json.loads(g9c_text)
    cases = [dict(v) for v in g9c["variants"] if v["role"] == "CASE_CTCF_ALU"]
    for v in cases:
        v["role"] = "CASE_CTCF_ALU"
    _progress(f"reused g9c cases n={len(cases)}")

    ctcf = load_bed_intervals(CTCF, chroms=CHROMS)
    te = load_bed_intervals(TE, chroms=CHROMS)
    te_by: dict[str, list[tuple[int, int, str]]] = {c: [] for c in CHROMS}
    for ch, s, e, name in te:
        te_by.setdefault(ch, []).append((s, e, name))
    for ch in te_by:
        te_by[ch].sort()

    non_te_peaks = [
        (ch, s, e, name)
        for ch, s, e, name in sorted(ctcf, key=lambda x: (x[0], x[1], x[2]))
        if ch in CHROMS
        and not excluded_pos(s, chrom=ch)
        and not excluded_pos(e - 1, chrom=ch)
        and not _peak_has_te(ch, s, e, te_by)
    ]
    _progress(f"ctcf={len(ctcf)} non_te_peaks={len(non_te_peaks)}")

    ctrl_pool: list[dict] = []
    seen = {variant_id(v["chrom"], v["pos"], v["ref"], v["alt"]) for v in cases}
    for i, (ch, s, e, _) in enumerate(non_te_peaks):
        if len(ctrl_pool) >= PANEL_CAP * 5:
            _progress(f"early-stop ctrl pool at peak {i}")
            break
        if i % 50 == 0:
            _progress(f"ctrl peak {i}/{len(non_te_peaks)} pool={len(ctrl_pool)}")
        for v in _gnomad_common(ch, s, e):
            if interval_contains(ctcf, v["pos"], chrom=ch) is None:
                continue
            if interval_contains(te, v["pos"], chrom=ch) is not None:
                continue
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in seen:
                continue
            seen.add(vid)
            ctrl_pool.append(
                {
                    **v,
                    "role": "CTRL_CTCF_NONALU",
                    "variant_id": vid,
                    "peak_start": s,
                    "peak_end": e,
                }
            )

    ctrls = match_controls_by_af_decile(
        cases,
        ctrl_pool,
        seed=SEED,
        cap=PANEL_CAP,
        af_min=AF_MIN,
        af_max=AF_MAX,
    )
    for v in ctrls:
        v["role"] = "CTRL_CTCF_NONALU"
        v["variant_id"] = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])

    payload = {
        "freeze_id": "g12b_ctcf_alu_vs_nonalu_panel_freeze_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "G12b_ctcf_alu_vs_nonalu_dnase_CLAIM_v1.md",
        "g9c_freeze_sha256": g9c_sha,
        "chromosomes": list(G9C_CHROMS),
        "af_band": [AF_MIN, AF_MAX],
        "seed": SEED,
        "panel_cap": PANEL_CAP,
        "n_case": len(cases),
        "n_ctrl": len(ctrls),
        "n_ctrl_pool": len(ctrl_pool),
        "n_non_te_ctcf_peaks": len(non_te_peaks),
        "holdout_sealed": True,
        "variants": cases + ctrls,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    FREEZE.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    FREEZE_SHA.write_text(digest + "\n", encoding="utf-8")
    _progress(f"DONE n_case={len(cases)} n_ctrl={len(ctrls)} sha={digest}")
    if len(cases) < 30 or len(ctrls) < 30:
        _progress("WARNING underpowered freeze")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
