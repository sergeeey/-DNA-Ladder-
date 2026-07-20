#!/usr/bin/env python3
"""Shared C-A2 helpers: active rule, switcher, matching, Fisher OR (no I/O)."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Sequence

import numpy as np

TE_CLASSES = frozenset({"SINE", "LINE", "LTR", "DNA", "Retroposon"})
RNG_SEED = 20260720
K_MATCH = 5


def is_active_classification(klass: str, completeness: str) -> bool:
    """Pre-registered SCREEN active rule for dELS switching."""
    if completeness.strip() != "All-data/Full-classification":
        return False
    k = klass.strip()
    return k == "dELS" or k.startswith("dELS,")


def is_registry_dels(klass: str) -> bool:
    """Registry primary class is dELS (ignore CTCF-bound suffix)."""
    primary = klass.strip().split(",")[0].strip()
    return primary == "dELS"


def switcher_flag(active_vector: Sequence[bool]) -> bool:
    """Switcher := active in ≥1 AND inactive in ≥3."""
    n = len(active_vector)
    a = sum(1 for x in active_vector if x)
    return a >= 1 and (n - a) >= 3


def tss_dist_bin(dist_bp: float) -> int:
    """log10(d+1) bins: [0,3), [3,4), [4,5), [5,∞) → 0..3."""
    x = math.log10(dist_bp + 1.0)
    if x < 3:
        return 0
    if x < 4:
        return 1
    if x < 5:
        return 2
    return 3


def fisher_or_woolf(
    a: int, b: int, c: int, d: int
) -> tuple[float, float, float, float]:
    """2x2 Fisher-style OR with Haldane-Anscombe correction + Woolf CI.

    Table:
      switcher     non-switcher
    E    a              b
    Ctrl c              d
    """
    aa, bb, cc, dd = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    or_ = (aa * dd) / (bb * cc)
    se = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
    log_or = math.log(or_)
    lo = math.exp(log_or - 1.96 * se)
    hi = math.exp(log_or + 1.96 * se)
    # two-sided p from hypergeometric / Fisher exact via scipy if available
    try:
        from scipy.stats import fisher_exact

        _, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
    except Exception:  # noqa: BLE001
        p = float("nan")
    return or_, lo, hi, float(p)


def match_1k(
    exposed_keys: Sequence[tuple],
    pool_by_key: dict[tuple, list[str]],
    *,
    k: int = K_MATCH,
    seed: int = RNG_SEED,
) -> dict[str, list[str]]:
    """Match each exposed id to up to k pool ids sharing the covariate key.

    Keys are opaque tuples. Sampling without replacement within each key's pool
    across exposed indices that share the key (greedy in input order).
    """
    rng = np.random.default_rng(seed)
    # working copies of available pool ids per key
    avail: dict[tuple, list[str]] = {
        key: list(ids) for key, ids in pool_by_key.items()
    }
    for key in avail:
        rng.shuffle(avail[key])

    out: dict[str, list[str]] = {}
    for exp_id, key in exposed_keys:
        bucket = avail.get(key, [])
        take = bucket[:k]
        avail[key] = bucket[k:]
        out[exp_id] = take
    return out


def quantile_bins(values: np.ndarray, n_bins: int) -> np.ndarray:
    """Assign 0..n_bins-1 by empirical quantiles (duplicates → lower bin)."""
    if len(values) == 0:
        return np.array([], dtype=int)
    # rank-based to handle ties stably
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.linspace(0, 1, len(values), endpoint=False)
    bins = np.minimum((ranks * n_bins).astype(int), n_bins - 1)
    return bins


def overlap_any(
    intervals_a: list[tuple[int, int]],
    intervals_b: list[tuple[int, int]],
) -> list[bool]:
    """For each interval in A, whether it overlaps any interval in B (same chrom)."""
    if not intervals_a:
        return []
    if not intervals_b:
        return [False] * len(intervals_a)
    b = sorted(intervals_b)
    out: list[bool] = []
    j0 = 0
    for s, e in intervals_a:
        while j0 < len(b) and b[j0][1] <= s:
            j0 += 1
        hit = False
        j = j0
        while j < len(b) and b[j][0] < e:
            if b[j][1] > s:
                hit = True
                break
            j += 1
        out.append(hit)
    return out


def group_by_chrom(
    rows: Iterable[tuple[str, int, int, str]],
) -> dict[str, list[tuple[int, int, str]]]:
    g: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for chrom, start, end, uid in rows:
        g[chrom].append((start, end, uid))
    for chrom in g:
        g[chrom].sort()
    return g
