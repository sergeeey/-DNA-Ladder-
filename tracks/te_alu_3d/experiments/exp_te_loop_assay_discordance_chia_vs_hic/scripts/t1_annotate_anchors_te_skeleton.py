#!/usr/bin/env python3
"""T1 annotation skeleton: extract loop anchors + TE overlap from RMSK.

EXPLORATORY_PARTIAL only — does NOT compute primary discordant-vs-null TE ORs.
Requires controls.md checklist before any primary AluSz / subfamily OR finalization.

Outputs:
  results/t1_annotation_skeleton.json
  results/anchors_hic.bed (small; committed if modest)
  results/anchors_pol2.bed (optional)
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"

# UCSC rmsk.txt.gz columns (0-based):
# 5=genoName, 6=genoStart, 7=genoEnd, 10=repName, 11=repClass, 12=repFamily
RMSK_CHROM, RMSK_START, RMSK_END = 5, 6, 7
RMSK_NAME, RMSK_CLASS, RMSK_FAMILY = 10, 11, 12

CANON = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
# Pre-registered interest classes (counts only — no OR)
TE_CLASSES = {"SINE", "LINE", "LTR", "DNA"}
FOCUS_NAMES_PREFIX = ("AluY", "AluS", "AluJ", "SVA", "L1")


def load_bedpe_anchors(path: Path) -> list[tuple[str, int, int]]:
    seen: set[tuple[str, int, int]] = set()
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as f:  # type: ignore[arg-type]
        for line in f:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 6:
                continue
            for chrom, s, e in (
                (cols[0], int(cols[1]), int(cols[2])),
                (cols[3], int(cols[4]), int(cols[5])),
            ):
                if chrom in CANON and e > s:
                    seen.add((chrom, s, e))
    return sorted(seen)


def write_bed(path: Path, intervals: list[tuple[str, int, int]]) -> None:
    with path.open("w") as f:
        for c, s, e in intervals:
            f.write(f"{c}\t{s}\t{e}\n")


def build_anchor_index(anchors: list[tuple[str, int, int]]):
    by: dict[str, list[tuple[int, int, int]]] = {}
    for i, (c, s, e) in enumerate(anchors):
        by.setdefault(c, []).append((s, e, i))
    for c in by:
        by[c].sort()
    return by


def annotate_rmsk(
    rmsk_path: Path, anchors: list[tuple[str, int, int]]
) -> dict:
    """Mark which anchors overlap any TE; tally class/family/name prefixes."""
    index = build_anchor_index(anchors)
    hit_any = [False] * len(anchors)
    class_hits: Counter[str] = Counter()
    family_hits: Counter[str] = Counter()
    prefix_hits: Counter[str] = Counter()
    # per-anchor first-hit labels (exploratory)
    anchor_label: list[str | None] = [None] * len(anchors)

    with gzip.open(rmsk_path, "rt") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= RMSK_NAME:
                continue
            chrom = cols[RMSK_CHROM]
            if chrom not in CANON:
                continue
            try:
                start, end = int(cols[RMSK_START]), int(cols[RMSK_END])
            except ValueError:
                continue
            if end <= start:
                continue
            rep_class = cols[RMSK_CLASS]
            rep_family = cols[RMSK_FAMILY]
            rep_name = cols[RMSK_NAME]
            intervals = index.get(chrom)
            if not intervals:
                continue
            # find overlaps
            lo, hi = 0, len(intervals)
            while lo < hi:
                mid = (lo + hi) // 2
                if intervals[mid][1] <= start:
                    lo = mid + 1
                else:
                    hi = mid
            for j in range(lo, len(intervals)):
                s, e, idx = intervals[j]
                if s >= end:
                    break
                if s < end and e > start:
                    if not hit_any[idx]:
                        hit_any[idx] = True
                        if rep_class in TE_CLASSES:
                            class_hits[rep_class] += 1
                        family_hits[rep_family] += 1
                        for pref in FOCUS_NAMES_PREFIX:
                            if rep_name.startswith(pref):
                                prefix_hits[pref] += 1
                                break
                        anchor_label[idx] = f"{rep_class}|{rep_family}|{rep_name}"

    n = len(anchors)
    n_hit = sum(hit_any)
    return {
        "n_anchors": n,
        "n_overlapping_any_rmsk_interval": n_hit,
        "overlap_rate": n_hit / n if n else None,
        "class_first_hit_counts": dict(class_hits),
        "family_first_hit_top20": dict(family_hits.most_common(20)),
        "focus_prefix_first_hit_counts": dict(prefix_hits),
        "status": "EXPLORATORY_PARTIAL",
        "primary_or_computed": False,
        "note": (
            "First-hit TE tallies only; NOT discordant-vs-null ORs. "
            "Do not finalize AluSz / primary subfamily OR until controls.md checklist done."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hic", type=Path, default=DATA / "ENCFF693XIL.bedpe.gz")
    ap.add_argument("--pol2", type=Path, default=DATA / "ENCFF511QFN.bedpe.gz")
    ap.add_argument("--rmsk", type=Path, default=DATA / "rmsk.txt.gz")
    ap.add_argument("--skip-rmsk", action="store_true")
    args = ap.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "script": "t1_annotate_anchors_te_skeleton",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "EXPLORATORY_PARTIAL",
        "primary_te_or": None,
        "anchors": {},
        "te_annotation": None,
    }

    if not args.hic.exists():
        print(f"Missing {args.hic}", file=sys.stderr)
        return 1
    hic_anchors = load_bedpe_anchors(args.hic)
    hic_bed = RESULTS / "anchors_hic.bed"
    write_bed(hic_bed, hic_anchors)
    report["anchors"]["hic"] = {
        "source": "ENCFF693XIL",
        "n_unique": len(hic_anchors),
        "bed": str(hic_bed),
    }

    if args.pol2.exists():
        pol2_anchors = load_bedpe_anchors(args.pol2)
        pol2_bed = RESULTS / "anchors_pol2.bed"
        write_bed(pol2_bed, pol2_anchors)
        report["anchors"]["pol2"] = {
            "source": "ENCFF511QFN",
            "n_unique": len(pol2_anchors),
            "bed": str(pol2_bed),
        }

    if not args.skip_rmsk:
        if not args.rmsk.exists():
            report["te_annotation"] = {
                "status": "SKIPPED_NO_RMSK",
                "path": str(args.rmsk),
            }
        else:
            print(f"Annotating {len(hic_anchors)} Hi-C anchors against {args.rmsk} ...")
            report["te_annotation"] = {
                "rmsk": str(args.rmsk),
                "universe": "hic_anchors",
                **annotate_rmsk(args.rmsk, hic_anchors),
            }

    out = RESULTS / "t1_annotation_skeleton.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "anchors": report["anchors"],
                      "te": report.get("te_annotation")}, indent=2))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
