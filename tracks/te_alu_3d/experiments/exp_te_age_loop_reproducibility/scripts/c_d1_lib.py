#!/usr/bin/env python3
"""Shared helpers for C-D1 TE age vs loop-call reproducibility."""

from __future__ import annotations

import gzip
import math
from collections import defaultdict
from typing import Iterable

CANON = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
TE_CLASSES = frozenset({"SINE", "LINE", "LTR"})
WIN_BP = 1000
MIN_ANCHOR_BP = 1000
MCID_SUPPORT = 0.10
MCID_KILL = 0.05
SEED = 20260721

# UCSC rmsk.txt.gz with bin column (0-based)
RMSK_MILLIDIV = 2
RMSK_CHROM = 5
RMSK_START = 6
RMSK_END = 7
RMSK_NAME = 10
RMSK_CLASS = 11
RMSK_FAMILY = 12

Anchor = tuple[str, int, int]


def open_text(path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("rt")


def load_bedpe_anchors(path) -> list[Anchor]:
    seen: set[Anchor] = set()
    with open_text(path) as f:
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


def merge_intervals(anchors: list[Anchor]) -> list[Anchor]:
    by: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for c, s, e in anchors:
        by[c].append((s, e))
    out: list[Anchor] = []
    for chrom, ivs in by.items():
        ivs.sort()
        cs, ce = ivs[0]
        for s, e in ivs[1:]:
            if s <= ce:
                ce = max(ce, e)
            else:
                out.append((chrom, cs, ce))
                cs, ce = s, e
        out.append((chrom, cs, ce))
    return sorted(out)


def pad_min_width(anchors: list[Anchor], min_bp: int = MIN_ANCHOR_BP) -> list[Anchor]:
    out: list[Anchor] = []
    for chrom, s, e in anchors:
        w = e - s
        if w >= min_bp:
            out.append((chrom, s, e))
            continue
        mid = (s + e) // 2
        half = min_bp // 2
        s2 = max(0, mid - half)
        out.append((chrom, s2, s2 + min_bp))
    return out


def midpoint_windows(anchors: list[Anchor], win_bp: int = WIN_BP) -> list[Anchor]:
    out: list[Anchor] = []
    half = win_bp // 2
    for chrom, s, e in anchors:
        mid = (s + e) // 2
        s2 = max(0, mid - half)
        out.append((chrom, s2, s2 + win_bp))
    return out


def build_units(raw: list[Anchor]) -> list[Anchor]:
    return midpoint_windows(pad_min_width(merge_intervals(raw)))


def interval_index(ivs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return sorted(ivs)


def overlaps_any(start: int, end: int, ivs: list[tuple[int, int]]) -> bool:
    if not ivs:
        return False
    lo, hi = 0, len(ivs)
    while lo < hi:
        mid = (lo + hi) // 2
        if ivs[mid][1] <= start:
            lo = mid + 1
        else:
            hi = mid
    for i in range(lo, len(ivs)):
        s, e = ivs[i]
        if s >= end:
            break
        if e > start:
            return True
    return False


def min_milli_overlap(
    start: int,
    end: int,
    te_ivs: list[tuple[int, int, int, str, str, str]],
) -> tuple[int | None, str | None, str | None]:
    """te_ivs sorted by start: (start, end, milliDiv, name, class, family)."""
    if not te_ivs:
        return None, None, None
    lo, hi = 0, len(te_ivs)
    while lo < hi:
        mid = (lo + hi) // 2
        if te_ivs[mid][1] <= start:
            lo = mid + 1
        else:
            hi = mid
    best = None
    for i in range(lo, len(te_ivs)):
        s, e, milli, _n, cls, fam = te_ivs[i]
        if s >= end:
            break
        if e > start:
            if best is None or milli < best[0]:
                best = (milli, cls, fam)
    if best is None:
        return None, None, None
    return best


def fisher_or_woolf(a: int, b: int, c: int, d: int) -> tuple[float, float, float, float | None]:
    aa, bb, cc, dd = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    or_ = (aa * dd) / (bb * cc)
    se = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
    log_or = math.log(or_)
    lo = math.exp(log_or - 1.96 * se)
    hi = math.exp(log_or + 1.96 * se)
    try:
        from scipy.stats import fisher_exact

        _, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
        p_out: float | None = float(p)
        if p_out != p_out:  # NaN
            p_out = None
    except Exception:  # noqa: BLE001
        p_out = None
    return or_, lo, hi, p_out


def tertile_cuts(values: list[float]) -> tuple[float, float]:
    """Return (q33, q66) nearest-rank cuts splitting into ~equal tertiles."""
    if len(values) < 3:
        raise ValueError("need ≥3 values for tertiles")
    s = sorted(values)
    n = len(s)
    i1 = max(0, n // 3 - 1)
    i2 = max(i1, 2 * n // 3 - 1)
    return s[i1], s[i2]


def assign_tertile(v: float, q33: float, q66: float) -> int:
    """0=young (low milliDiv), 1=mid, 2=old (high milliDiv)."""
    if v <= q33:
        return 0
    if v <= q66:
        return 1
    return 2


def verdict_delta(delta: float) -> str:
    if delta >= MCID_SUPPORT:
        return "SUPPORT"
    if delta < MCID_KILL:
        return "REJECT"
    return "INCONCLUSIVE"


def chrom_block_bootstrap_delta(
    young_flags: list[tuple[str, int]],
    old_flags: list[tuple[str, int]],
    *,
    n_boot: int = 500,
    seed: int = SEED,
) -> tuple[float, float]:
    """Bootstrap CI for Δ = mean(old) − mean(young); flags are (chrom, repro 0/1)."""
    import random

    rng = random.Random(seed)
    by_y: dict[str, list[int]] = defaultdict(list)
    by_o: dict[str, list[int]] = defaultdict(list)
    for c, f in young_flags:
        by_y[c].append(f)
    for c, f in old_flags:
        by_o[c].append(f)
    chroms = sorted(set(by_y) | set(by_o))
    if not chroms:
        return float("nan"), float("nan")
    deltas: list[float] = []
    for _ in range(n_boot):
        sample = [rng.choice(chroms) for _ in chroms]
        ys = [f for c in sample for f in by_y.get(c, ())]
        os_ = [f for c in sample for f in by_o.get(c, ())]
        if not ys or not os_:
            continue
        deltas.append(sum(os_) / len(os_) - sum(ys) / len(ys))
    if not deltas:
        return float("nan"), float("nan")
    deltas.sort()
    lo = deltas[int(0.025 * (len(deltas) - 1))]
    hi = deltas[int(0.975 * (len(deltas) - 1))]
    return lo, hi
