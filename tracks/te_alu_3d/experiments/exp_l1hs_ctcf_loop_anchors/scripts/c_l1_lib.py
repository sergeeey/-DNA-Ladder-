#!/usr/bin/env python3
"""Shared helpers for C-L1 L1HS @ CTCF∩Hi-C anchors."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Sequence

import numpy as np

CANON = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
TE_CLASSES = frozenset({"SINE", "LINE", "LTR", "DNA", "Retroposon"})
RNG_SEED = 20260720
WIN_BP = 1000
L1HS_UTR_BP = 2000
MCID_SUPPORT = 1.4
MCID_KILL = 1.1
UMAP_THR = 0.3

# UCSC rmsk
RMSK_CHROM, RMSK_START, RMSK_END, RMSK_STRAND, RMSK_NAME = 5, 6, 7, 9, 10


def fisher_or_woolf(a: int, b: int, c: int, d: int) -> tuple[float, float, float, float]:
    aa, bb, cc, dd = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    or_ = (aa * dd) / (bb * cc)
    se = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
    log_or = math.log(or_)
    lo = math.exp(log_or - 1.96 * se)
    hi = math.exp(log_or + 1.96 * se)
    try:
        from scipy.stats import fisher_exact

        _, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
    except Exception:  # noqa: BLE001
        p = float("nan")
    return or_, lo, hi, float(p)


def quantile_bins(values: np.ndarray, n_bins: int) -> np.ndarray:
    if len(values) == 0:
        return np.array([], dtype=int)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.linspace(0, 1, len(values), endpoint=False)
    return np.minimum((ranks * n_bins).astype(int), n_bins - 1)


def match_1to1(
    exposed_keys: Sequence[tuple],
    pool_by_key: dict[tuple, list[str]],
    *,
    seed: int = RNG_SEED,
) -> dict[str, str | None]:
    rng = np.random.default_rng(seed)
    avail = {k: list(v) for k, v in pool_by_key.items()}
    for k in avail:
        rng.shuffle(avail[k])
    out: dict[str, str | None] = {}
    for eid, key in exposed_keys:
        bucket = avail.get(key, [])
        if not bucket:
            out[eid] = None
            continue
        out[eid] = bucket[0]
        avail[key] = bucket[1:]
    return out


def verdict_or(or_primary: float, or_umap: float | None) -> str:
    if or_umap is not None and or_umap < MCID_KILL:
        return "REJECT"
    if or_primary >= MCID_SUPPORT:
        return "SUPPORT"
    if or_primary < MCID_KILL:
        return "REJECT"
    return "INCONCLUSIVE"


def group_by_key(ids: Sequence[str], keys: dict[str, tuple]) -> dict[tuple, list[str]]:
    out: dict[tuple, list[str]] = defaultdict(list)
    for i in ids:
        out[keys[i]].append(i)
    return out
