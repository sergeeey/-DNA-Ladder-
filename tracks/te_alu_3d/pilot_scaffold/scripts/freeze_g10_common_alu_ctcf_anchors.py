#!/usr/bin/env python3
"""G10: freeze common Alu∩CTCF anchors (new slots, not Stage-3 A754/A518)."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))

import freeze_stage3_architecture_anchors as s3  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"
G9C_FREEZE = PROSPECTIVE / "g9c_common_alu_ctcf_panel_freeze_v1.json"
G9C_SHA = PROSPECTIVE / "g9c_common_alu_ctcf_panel_freeze_v1.json.sha256"
CLAIM = PROSPECTIVE / "G10_common_alu_ctcf_indep_hic_CLAIM_v1.md"
CACHE_DIR = PROSPECTIVE / "g10_anchor_cache"
OUT_JSON = PROSPECTIVE / "g10_common_alu_ctcf_anchor_freeze_v1.json"
OUT_SHA = PROSPECTIVE / "g10_common_alu_ctcf_anchor_freeze_v1.json.sha256"

STAGE3_POS = {518_575, 75_445_532}
N_SLOTS = 4


def _verify_g9c() -> dict:
    text = G9C_FREEZE.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    expected = G9C_SHA.read_text(encoding="utf-8").strip().split()[0]
    if digest != expected:
        raise RuntimeError(f"g9c freeze hash mismatch: {digest} != {expected}")
    return json.loads(text)


def select_g10_slots(g9c: dict) -> list[dict]:
    """Deterministic selection per G10 CLAIM §3."""
    rows: list[dict] = []
    for v in g9c["variants"]:
        if v["role"] != "CASE_CTCF_ALU" or v["chrom"] != "chr11":
            continue
        pos = int(v["pos"])
        if pos in STAGE3_POS:
            continue
        if 5_200_000 <= pos < 5_300_000 or 64_000_000 <= pos < 68_000_000:
            continue
        rows.append(v)
    rows.sort(key=lambda x: (int(x["pos"]), x["ref"], x["alt"]))
    seen_peaks: set[tuple[int, int]] = set()
    picked: list[dict] = []
    for v in rows:
        peak = (int(v["peak_start"]), int(v["peak_end"]))
        if peak in seen_peaks:
            continue
        seen_peaks.add(peak)
        picked.append(v)
        if len(picked) >= N_SLOTS:
            break
    if len(picked) < N_SLOTS:
        raise RuntimeError(f"need {N_SLOTS} unique peaks, got {len(picked)}")
    slots = []
    for i, v in enumerate(picked, start=1):
        slots.append(
            {
                "slot_id": f"G10_{i:02d}",
                "candidate_id": f"C{v['pos']}",
                "variant": v["variant_id"],
                "chrom": "chr11",
                "chrom_num": "11",
                "pos_1based": int(v["pos"]),
                "g9c_peak_start": int(v["peak_start"]),
                "g9c_peak_end": int(v["peak_end"]),
                "af": float(v["af"]),
            }
        )
    return slots


def main(offline: bool = False) -> None:
    s3.USED_CACHE_FILES.clear()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    s3.assert_no_holdout_path(s3.CTCF_BED)
    g9c = _verify_g9c()
    g9c_sha = G9C_SHA.read_text(encoding="utf-8").strip().split()[0]
    slots_spec = select_g10_slots(g9c)
    print("[INFO] selected slots:")
    for s in slots_spec:
        print(f"  {s['slot_id']} {s['variant']} peak={s['g9c_peak_start']}-{s['g9c_peak_end']}")

    # Point Stage-3 helpers at G10 cache
    ensembl_release = s3.get_ensembl_release(CACHE_DIR, offline)
    print(f"[INFO] Ensembl release: {ensembl_release}")

    slots_out = []
    for slot in slots_spec:
        print(f"\n[SLOT] {slot['slot_id']} — {slot['variant']}")
        out = None
        last_err: Exception | None = None
        for attempt in range(1, 6):
            try:
                out = s3.freeze_slot(slot, CACHE_DIR, offline)
                break
            except Exception as exc:  # noqa: BLE001 — Ensembl 503/timeouts
                last_err = exc
                wait = 5 * attempt
                print(f"       attempt {attempt}/5 failed: {exc!r}; sleep {wait}s")
                import time

                time.sleep(wait)
        if out is None:
            raise RuntimeError(f"freeze_slot failed for {slot['slot_id']}: {last_err}")
        out["af"] = slot["af"]
        out["g9c_peak_start"] = slot["g9c_peak_start"]
        out["g9c_peak_end"] = slot["g9c_peak_end"]
        print(f"       status={out['status']}")
        slots_out.append(out)

    payload = {
        "freeze_version": "g10_common_alu_ctcf_anchor_freeze_v1",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "ensembl_release": ensembl_release,
        "claim": CLAIM.name,
        "g9c_freeze_sha256": g9c_sha,
        "ctcf_bed_source": str(s3.CTCF_BED),
        "holdout": "SEALED",
        "stage3_excluded_pos": sorted(STAGE3_POS),
        "n_slots": len(slots_out),
        "source_sha256": {
            "g9c_freeze": g9c_sha,
            "ctcf_bed": s3.sha256_file(s3.CTCF_BED),
            "claim": s3.sha256_file(CLAIM),
        },
        "cache_sha256": {
            path.name: s3.sha256_file(path) for path in sorted(s3.USED_CACHE_FILES)
        },
        "slots": slots_out,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    digest = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()
    OUT_SHA.write_text(digest + "\n", encoding="utf-8")
    print(f"\n[OK] {OUT_JSON.name} sha256={digest}")
    for s in slots_out:
        print(f"  {s['slot_id']} {s['status']}")


if __name__ == "__main__":
    offline = "--offline" in sys.argv
    main(offline=offline)
