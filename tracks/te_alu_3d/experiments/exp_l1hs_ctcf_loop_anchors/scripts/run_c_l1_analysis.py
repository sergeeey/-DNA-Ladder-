#!/usr/bin/env python3
"""C-L1: L1HS 5′UTR at CTCF peaks on Hi-C anchors vs matched background CTCF peaks.

Unit = CTCF peak (both arms) so length matching is well-defined.
Case: CTCF peaks overlapping ≥1 merged Hi-C anchor.
Control: 1:1 matched CTCF peaks with zero Hi-C overlap (chrom + length_q4 + umap_q4).
"""

from __future__ import annotations

import gzip
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyBigWig

ROOT = Path(__file__).resolve().parent.parent
INP = ROOT / "data" / "input"
RES = ROOT / "results"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from c_l1_lib import (  # noqa: E402
    CANON,
    L1HS_UTR_BP,
    MCID_KILL,
    MCID_SUPPORT,
    RNG_SEED,
    RMSK_CHROM,
    RMSK_END,
    RMSK_NAME,
    RMSK_START,
    RMSK_STRAND,
    UMAP_THR,
    fisher_or_woolf,
    group_by_key,
    match_1to1,
    quantile_bins,
    verdict_or,
)

CELLS = {
    "K562": {
        "hic": INP / "ENCFF693XIL.bedpe.gz",
        "ctcf": INP / "ENCFF769AUF.bed.gz",
        "primary": True,
    },
    "HCT116": {
        "hic": INP / "ENCFF060QTI.bedpe.gz",
        "ctcf": INP / "ENCFF463FGL.bed.gz",
        "primary": False,
    },
}


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("rt")


def load_bed(path: Path) -> list[tuple[str, int, int]]:
    out = []
    with open_text(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            chrom, s, e = p[0], int(p[1]), int(p[2])
            if chrom not in CANON or e <= s:
                continue
            out.append((chrom, s, e))
    return out


def load_bedpe_anchors(path: Path) -> list[tuple[str, int, int]]:
    seen: set[tuple[str, int, int]] = set()
    with open_text(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 6:
                continue
            for chrom, s, e in ((p[0], int(p[1]), int(p[2])), (p[3], int(p[4]), int(p[5]))):
                if chrom in CANON and e > s:
                    seen.add((chrom, s, e))
    return sorted(seen)


def merge_intervals(ivs: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    by: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for c, s, e in ivs:
        by[c].append((s, e))
    out = []
    for chrom, rows in by.items():
        rows.sort()
        cs, ce = rows[0]
        for s, e in rows[1:]:
            if s <= ce:
                ce = max(ce, e)
            else:
                out.append((chrom, cs, ce))
                cs, ce = s, e
        out.append((chrom, cs, ce))
    return sorted(out)


def to_chrom_dict(ivs: list[tuple[str, int, int]]) -> dict[str, list[tuple[int, int]]]:
    d: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for c, s, e in ivs:
        d[c].append((s, e))
    for c in d:
        d[c].sort()
    return d


def intervals_overlap_any(
    query: list[tuple[str, int, int]],
    targets: dict[str, list[tuple[int, int]]],
) -> list[bool]:
    out = []
    for chrom, s, e in query:
        iv = targets.get(chrom, [])
        lo, hi = 0, len(iv)
        while lo < hi:
            mid = (lo + hi) // 2
            if iv[mid][1] <= s:
                lo = mid + 1
            else:
                hi = mid
        j = lo
        hit = False
        while j < len(iv) and iv[j][0] < e:
            if iv[j][1] > s:
                hit = True
                break
            j += 1
        out.append(hit)
    return out


def load_l1hs_utr(path: Path) -> dict[str, list[tuple[int, int]]]:
    out: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) <= RMSK_NAME:
                continue
            if p[RMSK_NAME] != "L1HS":
                continue
            chrom = p[RMSK_CHROM]
            if chrom not in CANON:
                continue
            s, e = int(p[RMSK_START]), int(p[RMSK_END])
            strand = p[RMSK_STRAND]
            if e <= s:
                continue
            if strand == "+":
                u_s, u_e = s, min(e, s + L1HS_UTR_BP)
            elif strand == "-":
                u_s, u_e = max(s, e - L1HS_UTR_BP), e
            else:
                continue
            if u_e > u_s:
                out[chrom].append((u_s, u_e))
    for c in out:
        out[c].sort()
    return out


def mean_umap(bw, windows: list[tuple[str, int, int]]) -> list[float]:
    chroms = bw.chroms() or {}
    vals = []
    for chrom, s, e in windows:
        if chrom not in chroms:
            vals.append(0.0)
            continue
        clen = chroms[chrom]
        s2 = max(0, min(s, clen))
        e2 = max(s2 + 1, min(e, clen))
        try:
            m = bw.stats(chrom, s2, e2, type="mean")[0]
        except RuntimeError:
            m = None
        vals.append(float(m) if m is not None else 0.0)
    return vals


def run_cell(cell: str, cfg: dict, l1hs: dict, bw) -> dict:
    print(f"\n=== {cell} ===", flush=True)
    hic = merge_intervals(load_bedpe_anchors(cfg["hic"]))
    ctcf = load_bed(cfg["ctcf"])
    hic_by = to_chrom_dict(hic)
    on_anchor = intervals_overlap_any(ctcf, hic_by)
    case = [p for p, h in zip(ctcf, on_anchor) if h]
    ctrl = [p for p, h in zip(ctcf, on_anchor) if not h]
    print(f"  CTCF on-anchor={len(case)}  off-anchor={len(ctrl)}", flush=True)

    case_ids = [f"case_{i}" for i in range(len(case))]
    ctrl_ids = [f"ctrl_{i}" for i in range(len(ctrl))]
    wins = {**dict(zip(case_ids, case)), **dict(zip(ctrl_ids, ctrl))}

    case_lens = np.array([e - s for _, s, e in case], dtype=float)
    ctrl_lens = np.array([e - s for _, s, e in ctrl], dtype=float)
    case_umap = np.array(mean_umap(bw, case), dtype=float)
    ctrl_umap = np.array(mean_umap(bw, ctrl), dtype=float)
    all_lens = np.concatenate([case_lens, ctrl_lens])
    all_umap = np.concatenate([case_umap, ctrl_umap])
    len_bins = quantile_bins(all_lens, 4)
    umap_bins = quantile_bins(all_umap, 4)
    n_case = len(case_ids)

    keys: dict[str, tuple] = {}
    for i, cid in enumerate(case_ids):
        keys[cid] = (case[i][0], int(len_bins[i]), int(umap_bins[i]))
    for i, cid in enumerate(ctrl_ids):
        keys[cid] = (ctrl[i][0], int(len_bins[n_case + i]), int(umap_bins[n_case + i]))

    matched = match_1to1(
        [(cid, keys[cid]) for cid in case_ids],
        group_by_key(ctrl_ids, keys),
        seed=RNG_SEED,
    )
    pairs = [(c, m) for c, m in matched.items() if m is not None]
    n_under = sum(1 for m in matched.values() if m is None)
    print(f"  matched={len(pairs)} undermatched={n_under}", flush=True)
    med_c = float(np.median([wins[c][2] - wins[c][1] for c, _ in pairs])) if pairs else None
    med_m = float(np.median([wins[m][2] - wins[m][1] for _, m in pairs])) if pairs else None
    if pairs:
        print(f"  median length case/ctrl={med_c:.0f}/{med_m:.0f}", flush=True)

    case_hit = intervals_overlap_any([wins[c] for c, _ in pairs], l1hs)
    ctrl_hit = intervals_overlap_any([wins[m] for _, m in pairs], l1hs)
    a, b = sum(case_hit), len(case_hit) - sum(case_hit)
    c, d = sum(ctrl_hit), len(ctrl_hit) - sum(ctrl_hit)
    or_, lo, hi, p = fisher_or_woolf(a, b, c, d)
    print(f"  primary OR={or_:.4f} CI=({lo:.4f},{hi:.4f}) [{a},{b};{c},{d}]", flush=True)

    case_u = {cid: case_umap[i] for i, cid in enumerate(case_ids)}
    ctrl_u = {cid: ctrl_umap[i] for i, cid in enumerate(ctrl_ids)}
    a2 = b2 = c2 = d2 = 0
    n_umap = 0
    for (cid, mid), ch, mh in zip(pairs, case_hit, ctrl_hit):
        if case_u[cid] >= UMAP_THR and ctrl_u[mid] >= UMAP_THR:
            n_umap += 1
            if ch:
                a2 += 1
            else:
                b2 += 1
            if mh:
                c2 += 1
            else:
                d2 += 1
    or_u, lo_u, hi_u, p_u = (
        fisher_or_woolf(a2, b2, c2, d2) if n_umap else (float("nan"),) * 4
    )
    print(f"  umap≥{UMAP_THR} n={n_umap} OR={or_u:.4f} [{a2},{b2};{c2},{d2}]", flush=True)

    return {
        "cell": cell,
        "primary_cell": cfg["primary"],
        "unit": "CTCF_peak_on_vs_off_HiC_anchor",
        "n_case_ctcf_on_anchor": len(case),
        "n_ctrl_pool": len(ctrl),
        "n_matched_pairs": len(pairs),
        "n_undermatched": n_under,
        "median_length_matched_case": med_c,
        "median_length_matched_ctrl": med_m,
        "contingency_primary": {"a": a, "b": b, "c": c, "d": d},
        "or_primary": or_,
        "or_ci95": [lo, hi],
        "p_fisher": p,
        "n_pairs_umap_ge_0_3": n_umap,
        "contingency_umap": {"a": a2, "b": b2, "c": c2, "d": d2},
        "or_umap_0_3": or_u,
        "or_umap_ci95": [lo_u, hi_u],
        "p_fisher_umap": p_u,
        "mcid_support": MCID_SUPPORT,
        "mcid_kill": MCID_KILL,
        "verdict": verdict_or(or_, or_u if n_umap else None),
    }


def main() -> None:
    t0 = time.time()
    RES.mkdir(parents=True, exist_ok=True)
    print("loading L1HS 5′UTR…", flush=True)
    l1hs = load_l1hs_utr(INP / "rmsk.txt.gz")
    print(f"  intervals={sum(len(v) for v in l1hs.values())}", flush=True)
    bw = pyBigWig.open(str(INP / "k100.Umap.MultiTrackMappability.bw"))
    results = {cell: run_cell(cell, cfg, l1hs, bw) for cell, cfg in CELLS.items()}
    bw.close()
    overall = {
        "experiment": "exp_l1hs_ctcf_loop_anchors",
        "candidate_id": "C-L1",
        "seed": RNG_SEED,
        "l1hs_utr_bp": L1HS_UTR_BP,
        "cells": results,
        "primary_verdict": results["K562"]["verdict"],
        "elapsed_sec": round(time.time() - t0, 1),
        "note": (
            "Unit=CTCF peak on vs off Hi-C anchor (length-matched). "
            "Hi-C-anchor-as-unit abandoned: median span ~10kb vs CTCF ~0.4kb prevents "
            "valid length match; mid-1kb yields ~0 L1HS hits."
        ),
    }
    (RES / "primary_result_OR_CI.json").write_text(json.dumps(overall, indent=2) + "\n")
    (RES / "matching_lock.json").write_text(
        json.dumps(
            {
                "seed": RNG_SEED,
                "unit": "CTCF_peak",
                "covariates": ["chrom", "length_bin_q4", "umap_bin_q4"],
                "k562_matched": results["K562"]["n_matched_pairs"],
                "hct116_matched": results["HCT116"]["n_matched_pairs"],
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(overall, indent=2))


if __name__ == "__main__":
    main()
