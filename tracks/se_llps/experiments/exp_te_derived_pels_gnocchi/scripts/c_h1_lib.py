#!/usr/bin/env python3
"""Shared helpers for C-H1 TE-derived pELS vs Gnocchi (no I/O)."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Sequence

import numpy as np

TE_CLASSES = frozenset({"SINE", "LINE", "LTR", "DNA", "Retroposon"})
RNG_SEED = 20260720
KEEP_CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
SUPPORT_ABS_DELTA = 0.15
KILL_ABS_DELTA = 0.05


def is_registry_pels(klass: str) -> bool:
    primary = klass.strip().split(",")[0].strip()
    return primary == "pELS"


def tss_dist_bin(dist_bp: float) -> int:
    x = math.log10(dist_bp + 1.0)
    if x < 3:
        return 0
    if x < 4:
        return 1
    if x < 5:
        return 2
    return 3


def quantile_bins(values: np.ndarray, n_bins: int) -> np.ndarray:
    if len(values) == 0:
        return np.array([], dtype=int)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.linspace(0, 1, len(values), endpoint=False)
    bins = np.minimum((ranks * n_bins).astype(int), n_bins - 1)
    return bins


def match_1to1(
    exposed_keys: Sequence[tuple],
    pool_by_key: dict[tuple, list[str]],
    *,
    seed: int = RNG_SEED,
) -> dict[str, str | None]:
    """Match each exposed id to one pool id sharing the covariate key (w/o replacement)."""
    rng = np.random.default_rng(seed)
    avail: dict[tuple, list[str]] = {key: list(ids) for key, ids in pool_by_key.items()}
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


def cliffs_delta(group1: Sequence[float], group2: Sequence[float]) -> float:
    """Cliff's δ = 2U/(n1 n2) - 1 using Mann-Whitney U ranking."""
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


def paired_permutation_p(diffs: Sequence[float], n_perm: int, seed: int) -> tuple[float, float]:
    """Two-sided permutation p on mean(diff); null = random sign flips."""
    diffs = list(diffs)
    n = len(diffs)
    if n == 0:
        return float("nan"), float("nan")
    observed = sum(diffs) / n
    rng = np.random.default_rng(seed)
    count = 0
    arr = np.asarray(diffs, dtype=float)
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=n)
        perm_mean = float(np.mean(arr * signs))
        if abs(perm_mean) >= abs(observed):
            count += 1
    p = (count + 1) / (n_perm + 1)
    return observed, p


def bootstrap_mean_ci(
    diffs: Sequence[float], n_boot: int, seed: int, alpha: float = 0.05
) -> tuple[float, float, float]:
    arr = np.asarray(list(diffs), dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(np.mean(arr))
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample = rng.choice(arr, size=arr.size, replace=True)
        boots[i] = float(np.mean(sample))
    lo = float(np.quantile(boots, alpha / 2))
    hi = float(np.quantile(boots, 1 - alpha / 2))
    return mean, lo, hi


def verdict_from_abs_delta(abs_delta: float) -> str:
    if abs_delta < KILL_ABS_DELTA:
        return "REJECT"
    if abs_delta >= SUPPORT_ABS_DELTA:
        return "SUPPORT"
    return "INCONCLUSIVE"


def group_by_key(ids: Sequence[str], keys: dict[str, tuple]) -> dict[tuple, list[str]]:
    out: dict[tuple, list[str]] = defaultdict(list)
    for eid in ids:
        out[keys[eid]].append(eid)
    return out
