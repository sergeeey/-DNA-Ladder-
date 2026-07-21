#!/usr/bin/env python3
"""Fetch C-E1 non-HBB / non-holdout rare-SNV panel (chr11 CTCF neighborhoods).

Real data only: gnomAD GraphQL r4 + local Alu/SVA rmsk + Hoffman umap (already on disk).
Does NOT touch sealed holdout dumps. Does NOT score PWM (match-before-PWM lock).
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT.parents[1] / "pilot_scaffold"))

from c_e1_lib import (  # noqa: E402
    MAX_AF,
    RNG_SEED,
    excluded_pos,
    is_snv,
    load_ctcf_peaks,
    load_te_bed,
    merge_intervals,
    sample_intervals,
    te_overlap_at,
)
from fetch_dual_track_inputs import _post_graphql  # noqa: E402

INP = ROOT / "data" / "input"
OUT_PANEL = INP / "rare_snv_panel_chr11_nonhbb.jsonl"
OUT_META = INP / "fetch_meta.json"

CTCF = INP / "ctcf_HUDEP2_peaks.bed"
TE = INP / "repeatmasker_chr11_alu_sva.bed"
UMAP = INP / "k100.Umap.MultiTrackMappability.bw"

# Desk tractability: sample CTCF neighborhoods (claim desk; no bulk gnomAD)
MAX_PEAKS = 250
PEAK_PAD = 250
GQL_CHUNK = 8000
MAX_ATTEMPTS = 12

GQL = """
query RegionVariants($chrom: String!, $start: Int!, $stop: Int!) {
  region(chrom: $chrom, start: $start, stop: $stop, reference_genome: GRCh38) {
    variants(dataset: gnomad_r4) {
      variant_id
      chrom
      pos
      ref
      alt
      genome { af filters }
      exome { af filters }
    }
  }
}
"""


def fetch_region(start1: int, stop1: int) -> list[dict]:
    """Fetch gnomAD variants for 1-based inclusive region on chr11."""
    rows: list[dict] = []
    pos = start1
    cur = GQL_CHUNK
    while pos <= stop1:
        stop = min(pos + cur - 1, stop1)
        attempt = 0
        data = None
        while True:
            attempt += 1
            try:
                data = _post_graphql(
                    GQL, {"chrom": "11", "start": pos, "stop": stop}, timeout=180
                )
                break
            except (urllib.error.HTTPError, TimeoutError, urllib.error.URLError) as exc:
                code = getattr(exc, "code", None)
                if attempt >= MAX_ATTEMPTS:
                    if cur > 2000:
                        cur = max(2000, cur // 2)
                        attempt = 0
                        stop = min(pos + cur - 1, stop1)
                        print(f"  shrink chunk -> {cur}", flush=True)
                        continue
                    raise
                wait = min(45, 3 * attempt)
                print(f"  retry {attempt} ({code or type(exc).__name__}) wait {wait}s", flush=True)
                time.sleep(wait)
        assert data is not None
        if data.get("errors"):
            print("  API errors:", data["errors"][:1], flush=True)
        variants = (((data.get("data") or {}).get("region") or {}).get("variants")) or []
        print(f"  gnomAD 11:{pos}-{stop} n={len(variants)}", flush=True)
        for v in variants:
            genome = v.get("genome") or {}
            exome = v.get("exome") or {}
            af = genome.get("af")
            if af is None:
                af = exome.get("af")
            if af is None:
                continue
            ref = v.get("ref") or ""
            alt = v.get("alt")
            if isinstance(alt, list):
                alt = alt[0] if alt else ""
            if not is_snv(ref, str(alt)):
                continue
            if float(af) > MAX_AF:
                continue
            pos_i = int(v["pos"])
            if excluded_pos(pos_i):
                continue
            filt = genome.get("filters") or exome.get("filters") or []
            if isinstance(filt, list) and filt:
                # Drop explicit non-PASS filter sets; empty / PASS kept
                if "PASS" not in filt:
                    continue
            rows.append(
                {
                    "variant_id": v.get("variant_id") or f"11-{pos_i}-{ref}-{alt}",
                    "chrom": "chr11",
                    "pos": pos_i,
                    "ref": ref.upper(),
                    "alt": str(alt).upper(),
                    "af": float(af),
                }
            )
        pos = stop + 1
        cur = GQL_CHUNK
        time.sleep(0.15)
    return rows


def main() -> int:
    INP.mkdir(parents=True, exist_ok=True)
    if not UMAP.exists():
        print("BLOCKED_DATA: umap missing", UMAP, flush=True)
        return 2
    if not CTCF.exists() or not TE.exists():
        print("BLOCKED_DATA: CTCF or TE bed missing", flush=True)
        return 2

    peaks = load_ctcf_peaks(CTCF, pad=PEAK_PAD)
    sampled = sample_intervals(peaks, MAX_PEAKS, seed=RNG_SEED)
    merged = merge_intervals(sampled)
    print(
        f"peaks_allowed_sampled={len(sampled)} merged_windows={len(merged)}",
        flush=True,
    )

    te_idx = load_te_bed(TE)
    seen: dict[str, dict] = {}
    for chrom, s0, e0 in merged:
        # bed 0-based half-open → gnomAD 1-based inclusive
        start1, stop1 = s0 + 1, e0
        print(f"window {chrom}:{start1}-{stop1}", flush=True)
        for row in fetch_region(start1, stop1):
            te_name = te_overlap_at(row["chrom"], row["pos"], te_idx)
            row["te_overlap"] = te_name is not None
            row["te_name"] = te_name
            seen[row["variant_id"]] = row

    rows = list(seen.values())
    n_te = sum(1 for r in rows if r["te_overlap"])
    n_non = len(rows) - n_te
    with OUT_PANEL.open("w", encoding="utf-8") as fh:
        for r in sorted(rows, key=lambda x: x["pos"]):
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")

    meta = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "source": "gnomAD GraphQL r4",
        "scope": "chr11 CTCF±250bp neighborhoods; exclude HBB+HO geography",
        "max_af": MAX_AF,
        "max_peaks": MAX_PEAKS,
        "n_peaks_sampled": len(sampled),
        "n_merged_windows": len(merged),
        "n_rare_snv": len(rows),
        "n_te_alu_sva": n_te,
        "n_non_te": n_non,
        "panel_path": str(OUT_PANEL.relative_to(ROOT)),
        "umap_path": str(UMAP.name),
        "seed": RNG_SEED,
        "holdout": "SEALED_excluded",
        "hbb": "excluded",
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2), flush=True)
    if len(rows) < 50 or n_te < 10 or n_non < 10:
        print("WARN: thin panel — may be underpowered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
