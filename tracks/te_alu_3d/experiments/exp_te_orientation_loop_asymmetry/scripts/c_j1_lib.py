#!/usr/bin/env python3
"""Shared helpers for C-J1 TE orientation vs loop-anchor asymmetry."""

from __future__ import annotations

import gzip
import math
from collections import defaultdict

CANON = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
TE_CLASSES = frozenset({"SINE", "LINE", "LTR"})
WIN_BP = 1000
MIN_ANCHOR_BP = 1000
MCID_SUPPORT = 0.10
MCID_KILL = 0.05
SEED = 20260721

# UCSC rmsk.txt.gz with bin column (0-based)
RMSK_STRAND = 9
RMSK_CHROM = 5
RMSK_START = 6
RMSK_END = 7
RMSK_NAME = 10
RMSK_CLASS = 11
RMSK_FAMILY = 12

Anchor = tuple[str, int, int]
Loop = tuple[Anchor, Anchor]  # left, right


def open_text(path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("rt")


def pad_min_width(chrom: str, s: int, e: int, min_bp: int = MIN_ANCHOR_BP) -> Anchor:
    w = e - s
    if w >= min_bp:
        return (chrom, s, e)
    mid = (s + e) // 2
    half = min_bp // 2
    s2 = max(0, mid - half)
    return (chrom, s2, s2 + min_bp)


def midpoint_window(chrom: str, s: int, e: int, win_bp: int = WIN_BP) -> Anchor:
    mid = (s + e) // 2
    half = win_bp // 2
    s2 = max(0, mid - half)
    return (chrom, s2, s2 + win_bp)


def unitize_anchor(chrom: str, s: int, e: int) -> Anchor:
    return midpoint_window(*pad_min_width(chrom, s, e))


def load_bedpe_loops(path) -> list[Loop]:
    """Load Hi-C loops as (left_unit, right_unit) pairs; drop non-canonical / inverted."""
    out: list[Loop] = []
    with open_text(path) as f:
        for line in f:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 6:
                continue
            c1, s1, e1 = cols[0], int(cols[1]), int(cols[2])
            c2, s2, e2 = cols[3], int(cols[4]), int(cols[5])
            if c1 not in CANON or c2 not in CANON or e1 <= s1 or e2 <= s2:
                continue
            # Same-chrom only for left/right genomic asymmetry
            if c1 != c2:
                continue
            left = unitize_anchor(c1, s1, e1)
            right = unitize_anchor(c2, s2, e2)
            # Enforce genomic left ≤ right by midpoint
            if left[1] > right[1]:
                left, right = right, left
            out.append((left, right))
    return out


def load_te_strand_intervals(rmsk_path, *, alu_only: bool = False):
    """chrom -> sorted list of (start, end, strand, repName, repClass, repFamily)."""
    by: dict[str, list[tuple[int, int, str, str, str, str]]] = defaultdict(list)
    with open_text(rmsk_path) as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= RMSK_FAMILY:
                continue
            chrom = cols[RMSK_CHROM]
            if chrom not in CANON:
                continue
            rep_class = cols[RMSK_CLASS]
            if rep_class not in TE_CLASSES:
                continue
            fam = cols[RMSK_FAMILY]
            name = cols[RMSK_NAME]
            if alu_only and "Alu" not in fam and "Alu" not in name:
                continue
            strand = cols[RMSK_STRAND]
            if strand not in {"+", "-"}:
                continue
            try:
                start = int(cols[RMSK_START])
                end = int(cols[RMSK_END])
            except ValueError:
                continue
            if end <= start:
                continue
            by[chrom].append((start, end, strand, name, rep_class, fam))
    for chrom in by:
        by[chrom].sort(key=lambda x: (x[0], x[1]))
    return by


def max_overlap_strand(
    start: int,
    end: int,
    te_ivs: list[tuple[int, int, str, str, str, str]],
) -> str | None:
    """Return strand of max-overlap TE; ties → earliest start. None if no hit."""
    if not te_ivs:
        return None
    lo, hi = 0, len(te_ivs)
    while lo < hi:
        mid = (lo + hi) // 2
        if te_ivs[mid][1] <= start:
            lo = mid + 1
        else:
            hi = mid
    best_ov = 0
    best_start = None
    best_strand = None
    for i in range(lo, len(te_ivs)):
        s, e, strand, _n, _c, _f = te_ivs[i]
        if s >= end:
            break
        ov = min(end, e) - max(start, s)
        if ov <= 0:
            continue
        if ov > best_ov or (ov == best_ov and (best_start is None or s < best_start)):
            best_ov = ov
            best_start = s
            best_strand = strand
    return best_strand


def verdict_abs_delta(abs_delta: float) -> str:
    if abs_delta >= MCID_SUPPORT:
        return "SUPPORT"
    if abs_delta < MCID_KILL:
        return "REJECT"
    return "INCONCLUSIVE"


def chrom_block_bootstrap_delta(
    left_flags: list[tuple[str, int]],
    right_flags: list[tuple[str, int]],
    *,
    n_boot: int = 500,
    seed: int = SEED,
) -> tuple[float, float]:
    """Bootstrap CI for Δ = mean(left) − mean(right); flags are (chrom, is_plus 0/1)."""
    import random

    rng = random.Random(seed)
    by_l: dict[str, list[int]] = defaultdict(list)
    by_r: dict[str, list[int]] = defaultdict(list)
    for c, f in left_flags:
        by_l[c].append(f)
    for c, f in right_flags:
        by_r[c].append(f)
    chroms = sorted(set(by_l) | set(by_r))
    if not chroms:
        return float("nan"), float("nan")
    deltas: list[float] = []
    for _ in range(n_boot):
        sample = [rng.choice(chroms) for _ in chroms]
        ls = [f for c in sample for f in by_l.get(c, ())]
        rs = [f for c in sample for f in by_r.get(c, ())]
        if not ls or not rs:
            continue
        deltas.append(sum(ls) / len(ls) - sum(rs) / len(rs))
    if not deltas:
        return float("nan"), float("nan")
    deltas.sort()
    lo = deltas[int(0.025 * (len(deltas) - 1))]
    hi = deltas[int(0.975 * (len(deltas) - 1))]
    return lo, hi


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
        if p_out != p_out:
            p_out = None
    except Exception:  # noqa: BLE001
        p_out = None
    return or_, lo, hi, p_out
