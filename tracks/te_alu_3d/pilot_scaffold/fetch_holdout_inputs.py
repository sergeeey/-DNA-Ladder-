"""Fetch holdout-window inputs WITHOUT scoring (labels stay sealed).

Usage:
  python fetch_holdout_inputs.py          # gnomAD GraphQL for HO windows
  python fetch_holdout_inputs.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT.parent / "07_methods" / "holdout_manifest.yaml"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with MANIFEST.open(encoding="utf-8") as fh:
        man = yaml.safe_load(fh)
    hold = man["holdout"]
    if hold.get("unblind_authorized"):
        print("WARNING: unblind_authorized=true — scoring allowed by protocol")
    else:
        print("SEALED: will fetch only; will NOT score / enrich", flush=True)

    windows = hold["windows"]
    out_dir = ROOT / "data" / "holdout"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "SEALED.txt").write_text(
        "Do not score until holdout.unblind_authorized=true\n"
        f"sealed_at={hold.get('sealed_at')}\n",
        encoding="utf-8",
    )

    if args.dry_run:
        print(json.dumps({"windows": windows, "action": "dry_run_no_fetch"}, indent=2))
        return 0

    # Reuse GraphQL fetcher per window
    from fetch_dual_track_inputs import fetch_gnomad_window

    summary = []
    for w in windows:
        start, end = int(w["start"]), int(w["end"])
        dest_tsv = out_dir / f"gnomad_{w['id']}.tsv"
        dest_vcf = out_dir / f"gnomad_{w['id']}.vcf.gz"
        if dest_tsv.exists() and dest_vcf.exists() and dest_tsv.stat().st_size > 0:
            print(f"skip {w['id']} (already in holdout/)")
            summary.append({"id": w["id"], "tsv": str(dest_tsv), "vcf": str(dest_vcf), "skipped": True})
            continue
        stem = f"holdout/gnomad_{w['id']}"
        print(f"fetch {w['id']} chr11:{start}-{end} -> data/{stem}.*")
        # write directly under data/holdout via prefix path — fetch uses DATA/stem
        # so use stem without nested dir: gnomad_HO_A then move
        local_stem = f"gnomad_{w['id']}"
        vcf = fetch_gnomad_window(
            "chr11",
            start,
            end,
            chunk=10_000,
            out_prefix=local_stem,
            max_attempts=6,
            min_chunk=2000,
            allow_gaps=True,
        )
        data = ROOT / "data"
        src_tsv = data / f"{local_stem}.tsv"
        src_vcf = data / f"{local_stem}.vcf.gz"
        if src_tsv.exists():
            dest_tsv.write_bytes(src_tsv.read_bytes())
            src_tsv.unlink()
        if src_vcf.exists():
            dest_vcf.write_bytes(src_vcf.read_bytes())
            src_vcf.unlink()
        summary.append({"id": w["id"], "tsv": str(dest_tsv), "vcf": str(dest_vcf), "source_vcf": str(vcf)})

    (out_dir / "fetch_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"fetched": summary, "scored": False, "sealed": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
