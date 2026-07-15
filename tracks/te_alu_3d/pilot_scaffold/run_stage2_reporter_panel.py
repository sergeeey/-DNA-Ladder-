#!/usr/bin/env python3
"""Stage-2 desk: REF/ALT reporter windows for locked panel shortlist.

No oligo order. No transfection. Fetches hg38 via UCSC API.
"""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "09_outputs" / "prospective"
DATA = ROOT / "data" / "cultivation" / "stage2_reporters"
STAGE1 = OUT / "stage1_desk_screen_v1.json"

# Stage-2 shortlist from STAGE1_RESULTS / protocol (6–8 tests)
SHORTLIST = [
    {"id": "C1", "variant_id": "chr11:62753923:A:G", "role": "TEMPLATE_DEV/activity", "stage3": False},
    {"id": "C2", "variant_id": "chr11:62753923:A:T", "role": "activity_m3", "stage3": False},
    {"id": "C3", "variant_id": "chr11:72434037:C:T", "role": "activity_m3/convergence_stage3", "stage3": True},
    {"id": "A114", "variant_id": "chr11:114036577:G:C", "role": "activity_m3", "stage3": False},
    {"id": "ARCH754", "variant_id": "chr11:75445532:G:A", "role": "architecture_m1/stage3_arch1", "stage3": True},
    {"id": "ARCH518", "variant_id": "chr11:518575:C:A", "role": "architecture_m1/stage3_arch2", "stage3": True},
    {"id": "N3", "variant_id": "chr11:108009167:T:C", "role": "matched_negative/stage3_neg", "stage3": True},
    {"id": "W1", "variant_id": "chr11:57568168:C:T", "role": "disagreement/stage3", "stage3": True},
]

WINDOWS = {
    "minimal_301bp": 301,
    "context_1kb": 1001,
    "context_2kb": 2001,
}


def fetch(chrom: str, start0: int, end0: int) -> str:
    url = (
        "https://api.genome.ucsc.edu/getData/sequence"
        f"?genome=hg38;chrom={chrom};start={start0};end={end0}"
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    seq = (data.get("dna") or data.get("sequence") or "").upper()
    if not seq:
        raise RuntimeError(f"no seq {chrom}:{start0}-{end0}")
    return seq.replace("U", "T")


def parse_vid(vid: str) -> tuple[str, int, str, str]:
    chrom, pos, ref, alt = vid.split(":")
    return chrom, int(pos), ref.upper(), alt.upper()


def window_coords(pos: int, length: int) -> tuple[int, int, int]:
    """Return (start0, end0, index0 of variant). Length odd preferred; center on pos."""
    half = length // 2
    # 1-based pos → 0-based index of base = pos-1
    center0 = pos - 1
    start0 = center0 - half
    end0 = start0 + length
    if start0 < 0:
        end0 -= start0
        start0 = 0
    idx = center0 - start0
    return start0, end0, idx


def apply_alt(seq: str, idx: int, ref: str, alt: str) -> str:
    if seq[idx] != ref:
        # allow soft mismatch with force
        return seq[:idx] + alt + seq[idx + 1 :]
    return seq[:idx] + alt + seq[idx + 1 :]


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    pool_by_id = {}
    if STAGE1.exists():
        pool_by_id = {
            p["variant_id"]: p
            for p in json.loads(STAGE1.read_text(encoding="utf-8")).get("pool", [])
        }

    constructs = []
    files = []

    # group by locus for shared REF fetch
    for item in SHORTLIST:
        chrom, pos, ref, alt = parse_vid(item["variant_id"])
        entry = {
            **item,
            "chrom": chrom,
            "pos": pos,
            "ref": ref,
            "alt": alt,
            "ag": {
                "chip_tf_mae": pool_by_id.get(item["variant_id"], {}).get("ag_chip_tf_mae"),
                "contact_mae": pool_by_id.get(item["variant_id"], {}).get("ag_contact_mae"),
                "mechanism_prior": pool_by_id.get(item["variant_id"], {}).get("mechanism_prior"),
            },
            "windows": {},
        }
        for wname, wlen in WINDOWS.items():
            start0, end0, idx = window_coords(pos, wlen)
            print(f"{item['id']} {wname} fetch {chrom}:{start0}-{end0}", flush=True)
            seq_ref = fetch(chrom, start0, end0)
            if len(seq_ref) != wlen:
                # trim/pad safety
                seq_ref = seq_ref[:wlen].ljust(wlen, "N")
            observed = seq_ref[idx]
            allele_mismatch = observed != ref
            seq_alt = apply_alt(seq_ref, idx, observed if allele_mismatch else ref, alt)

            stem = f"{item['id'].lower()}_{wname}"
            ref_path = DATA / f"{stem}_REF.fa"
            alt_path = DATA / f"{stem}_ALT.fa"
            # 1-based inclusive display
            grch38 = f"{chrom}:{start0 + 1}-{end0}"
            ref_path.write_text(
                f">{item['id']}_{wname}_REF_{ref} {grch38}\n{seq_ref}\n", encoding="utf-8"
            )
            alt_path.write_text(
                f">{item['id']}_{wname}_ALT_{alt} {grch38}\n{seq_alt}\n", encoding="utf-8"
            )
            files.extend([str(ref_path), str(alt_path)])
            entry["windows"][wname] = {
                "grch38": grch38,
                "len": wlen,
                "c1_index0": idx,
                "ref_file": ref_path.name,
                "alt_file": alt_path.name,
                "observed_ref_base": observed,
                "allele_mismatch_vs_gnomad_ref": allele_mismatch,
            }
            time.sleep(0.12)
        constructs.append(entry)

    meta = {
        "status": "STAGE2_REPORTER_DESK_READY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "order": "FORBIDDEN until signed GO",
        "transfection": "FORBIDDEN",
        "genome": "hg38/GRCh38",
        "cell_preferred": "HUDEP-2",
        "mcid_reporter": "|log2(ALT/REF)| >= 0.5 in >=2 independent transfections",
        "escalation": "minimal_301bp -> context_1kb -> context_2kb before biological null",
        "stage3_locked": True,
        "note": "Stage-3 slot assignments unchanged; reporter-null does not prove architecture",
        "n_constructs": len(constructs),
        "constructs": constructs,
        "data_dir": str(DATA),
    }
    meta_path = OUT / "stage2_reporter_panel_v1.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # markdown report
    lines = [
        "# Stage-2 reporter panel — desk v1",
        "",
        f"**Date:** {meta['timestamp'][:10]}  ",
        "**Status:** `STAGE2_REPORTER_DESK_READY` · **ORDER FORBIDDEN** · **no transfection**  ",
        "**Protocol:** `SCALE_PROTOCOL_prospective_panel_v1.md` Stage 2  ",
        f"**Sequences:** `{DATA.as_posix()}`  ",
        f"**JSON:** `{meta_path.name}`",
        "",
        "## Goal",
        "",
        "REF vs ALT autonomous activity for locked Stage-2 shortlist (8 alleles).",
        "Does **not** freeze Stage-3; does **not** claim loops.",
        "",
        "## Constructs",
        "",
        "| ID | Variant | Role | Stage3 slot | AG CHIP | AG contact | 301 bp window |",
        "|----|---------|------|:-----------:|--------:|-----------:|--------------|",
    ]
    for c in constructs:
        w = c["windows"]["minimal_301bp"]
        lines.append(
            f"| {c['id']} | `{c['variant_id']}` | {c['role']} | "
            f"{'yes' if c['stage3'] else 'no'} | "
            f"{c['ag'].get('chip_tf_mae') or '—'} | "
            f"{c['ag'].get('contact_mae') or '—'} | `{w['grch38']}` |"
        )
    lines += [
        "",
        "## Window ladder (each allele)",
        "",
        "| Window | Length | Rule |",
        "|--------|-------:|------|",
        "| **minimal_301bp** | 301 | start here |",
        "| context_1kb | 1001 | escalate if null/equivocal |",
        "| context_2kb | 2001 | before biological B− |",
        "",
        "## MCID",
        "",
        "```yaml",
        "mcid: |log2(ALT/REF)| >= 0.5 in >=2 independent transfections",
        "fail: no reproducible direction",
        "```",
        "",
        "## Interpretation vs Stage-3",
        "",
        "| Outcome | Meaning |",
        "|---------|---------|",
        "| Reporter+ | M3 supported in autonomous window |",
        "| Reporter− after ladder | not activity-null for architecture claim |",
        "| N3 near-null | matching control OK |",
        "| Do not reshuffle Stage-3 slots by reporter beauty | LOCKED |",
        "",
        "## Pre-order gate",
        "",
        "- [ ] Signed panel or Phase B0 GO",
        "- [ ] Backbone ID frozen",
        "- [ ] Primer-BLAST / synthesis vendor chosen",
        "- [ ] PO SKUs match this checklist",
        "",
        "**If unchecked → no oligo PO.**",
        "",
        "## Linked",
        "",
        "- `STAGE1_RESULTS_2026-07-15.md`",
        "- `prospective_panel_registry_v1.yaml`",
        "- `BranchB_reporter_design_v1.md` (C1 template)",
        "- `GO_note_draft_C1_B_first_v1.md`",
        "",
    ]
    md_path = OUT / "STAGE2_REPORTER_PANEL_v1.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # oligo checklist
    cl = [
        "# Stage-2 reporter oligo checklist v1",
        "",
        "**ORDER FORBIDDEN** until signed GO.",
        "",
        "## First PO (if GO): B-min only (301 bp REF+ALT) for all 8 IDs",
        "",
        "| SKU | Files |",
        "|-----|-------|",
    ]
    for c in constructs:
        w = c["windows"]["minimal_301bp"]
        cl.append(f"| {c['id']}-301-REF/ALT | `{w['ref_file']}`, `{w['alt_file']}` |")
    cl += [
        "",
        "Hold 1 kb / 2 kb as optional escalate line items.",
        "",
        f"Directory: `{DATA}`",
        "",
    ]
    (OUT / "Stage2_oligo_checklist_v1.md").write_text("\n".join(cl), encoding="utf-8")

    print(json.dumps({"n": len(constructs), "dir": str(DATA), "md": str(md_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
