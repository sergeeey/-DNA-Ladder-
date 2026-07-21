#!/usr/bin/env python3
"""C-E1 pure helpers: exclusions, TE overlap, matching, Cliff's δ (no network I/O)."""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

import numpy as np

RNG_SEED = 20260721
SUPPORT_ABS_DELTA = 0.20
KILL_ABS_DELTA = 0.05
MAX_AF = 0.001
UMAP_FLANK = 50  # ±50 bp mean umap per claim

# Hard exclusions (chr11 0-based half-open geography)
HBB = (5_200_000, 5_300_000, "HBB_development")
# Holdout HO_A/B/C contiguous geography — sealed; never score for enrichment
HOLDOUT_GEO = (64_000_000, 68_000_000, "holdout_HO_A_B_C_geography")
EXCLUDE = (HBB, HOLDOUT_GEO)


def excluded_pos(pos1: int) -> bool:
    """True if 1-based POS falls in HBB or sealed holdout geography."""
    p0 = pos1 - 1
    return any(a <= p0 < b for a, b, _ in EXCLUDE)


def interval_overlaps_exclude(start0: int, end0: int) -> bool:
    for a, b, _ in EXCLUDE:
        if start0 < b and end0 > a:
            return True
    return False


def quantile_bins(values: np.ndarray, n_bins: int) -> np.ndarray:
    if len(values) == 0:
        return np.array([], dtype=int)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.linspace(0, 1, len(values), endpoint=False)
    return np.minimum((ranks * n_bins).astype(int), n_bins - 1)


def cliffs_delta(group1: Sequence[float], group2: Sequence[float]) -> float:
    """Cliff's δ (group1 vs group2) = 2U/(n1 n2) - 1."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return float("nan")
    combined = [(d, 0) for d in group1] + [(d, 1) for d in group2]
    combined.sort(key=lambda x: x[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    return (2 * u1 / (n1 * n2)) - 1


def match_1to1(
    exposed_keys: Sequence[tuple],
    pool_by_key: dict[tuple, list[str]],
    *,
    seed: int = RNG_SEED,
) -> dict[str, str | None]:
    """Match each exposed id to one pool id sharing covariate key (w/o replacement)."""
    rng = np.random.default_rng(seed)
    avail: dict[tuple, list[str]] = {k: list(ids) for k, ids in pool_by_key.items()}
    for key in avail:
        rng.shuffle(avail[key])
    out: dict[str, str | None] = {}
    for exp_id, key in exposed_keys:
        bucket = avail.get(key, [])
        if not bucket:
            out[exp_id] = None
            continue
        out[exp_id] = bucket[0]
        avail[key] = bucket[1:]
    return out


def group_by_key(ids: Sequence[str], keys: Sequence[tuple]) -> dict[tuple, list[str]]:
    out: dict[tuple, list[str]] = defaultdict(list)
    for i, k in zip(ids, keys):
        out[k].append(i)
    return dict(out)


def te_overlap_at(
    chrom: str,
    pos1: int,
    te_by_chrom: dict[str, list[tuple[int, int, str]]],
) -> str | None:
    """Return TE name if 1-based POS overlaps any Alu/SVA interval (0-based bed).

    Assumes per-chrom intervals sorted by start (rmsk-derived; non-nested).
    """
    rows = te_by_chrom.get(chrom, [])
    p0 = pos1 - 1
    lo, hi = 0, len(rows)
    while lo < hi:
        mid = (lo + hi) // 2
        if rows[mid][0] <= p0:
            lo = mid + 1
        else:
            hi = mid
    i = lo - 1
    if i >= 0:
        s, e, name = rows[i]
        if s <= p0 < e:
            return name
    return None


def load_te_bed(path) -> dict[str, list[tuple[int, int, str]]]:
    from pathlib import Path

    by: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) < 3:
            continue
        chrom = p[0] if p[0].startswith("chr") else f"chr{p[0]}"
        name = p[3] if len(p) > 3 else "TE"
        by[chrom].append((int(p[1]), int(p[2]), name))
    for chrom in by:
        by[chrom].sort()
    return dict(by)


def load_ctcf_peaks(path, *, pad: int = 250) -> list[tuple[str, int, int]]:
    """Load peaks as padded 0-based intervals; drop those intersecting exclusions."""
    from pathlib import Path

    out: list[tuple[str, int, int]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) < 3:
            continue
        chrom = p[0] if p[0].startswith("chr") else f"chr{p[0]}"
        if chrom != "chr11":
            continue
        s = max(0, int(p[1]) - pad)
        e = int(p[2]) + pad
        if e <= s or interval_overlaps_exclude(s, e):
            continue
        out.append((chrom, s, e))
    return out


def merge_intervals(ivs: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    if not ivs:
        return []
    ivs = sorted(ivs)
    out = [ivs[0]]
    for c, s, e in ivs[1:]:
        pc, ps, pe = out[-1]
        if c == pc and s <= pe:
            out[-1] = (c, ps, max(pe, e))
        else:
            out.append((c, s, e))
    return out


def sample_intervals(
    ivs: list[tuple[str, int, int]],
    max_n: int,
    seed: int = RNG_SEED,
) -> list[tuple[str, int, int]]:
    if len(ivs) <= max_n:
        return list(ivs)
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(len(ivs), size=max_n, replace=False))
    return [ivs[i] for i in idx]


def verdict_delta(delta: float) -> str:
    ad = abs(delta)
    if ad < KILL_ABS_DELTA:
        return "REJECT"
    if ad < SUPPORT_ABS_DELTA:
        return "INCONCLUSIVE"
    return "SUPPORT"


def is_snv(ref: str, alt: str) -> bool:
    return len(ref) == 1 and len(alt) == 1 and ref.upper() in "ACGT" and alt.upper() in "ACGT"
