#!/usr/bin/env python3
"""Unit tests for C-H1 TE-derived pELS Gnocchi helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from c_h1_lib import (  # noqa: E402
    KILL_ABS_DELTA,
    SUPPORT_ABS_DELTA,
    cliffs_delta,
    is_registry_pels,
    match_1to1,
    quantile_bins,
    tss_dist_bin,
    verdict_from_abs_delta,
)


def test_is_registry_pels():
    assert is_registry_pels("pELS")
    assert is_registry_pels("pELS,CTCF-bound")
    assert not is_registry_pels("dELS")
    assert not is_registry_pels("PLS")


def test_tss_dist_bin_edges():
    assert tss_dist_bin(0) == 0
    assert tss_dist_bin(998) == 0  # log10(999) < 3
    assert tss_dist_bin(999) == 1  # log10(1000) == 3 → bin 1
    assert tss_dist_bin(10_000) == 2
    assert tss_dist_bin(100_000) == 3


def test_quantile_bins_four():
    vals = np.arange(100, dtype=float)
    bins = quantile_bins(vals, 4)
    assert set(bins.tolist()) == {0, 1, 2, 3}
    assert bins[0] == 0
    assert bins[-1] == 3


def test_match_1to1_no_reuse():
    exposed = [("e1", ("chr1", 0, 0, 0)), ("e2", ("chr1", 0, 0, 0))]
    pool = {("chr1", 0, 0, 0): ["c1", "c2", "c3"]}
    m = match_1to1(exposed, pool, seed=1)
    assert m["e1"] is not None and m["e2"] is not None
    assert m["e1"] != m["e2"]
    assert {m["e1"], m["e2"]}.issubset({"c1", "c2", "c3"})


def test_match_undermatched():
    exposed = [("e1", ("chr1", 0, 0, 0))]
    pool: dict = {("chr1", 0, 0, 0): []}
    m = match_1to1(exposed, pool, seed=1)
    assert m["e1"] is None


def test_cliffs_delta_identical():
    xs = [1.0, 2.0, 3.0]
    assert abs(cliffs_delta(xs, xs)) < 1e-9


def test_cliffs_delta_separated():
    a = [10.0, 11.0, 12.0]
    b = [1.0, 2.0, 3.0]
    d = cliffs_delta(a, b)
    assert d > 0.9


def test_verdict_gates():
    assert verdict_from_abs_delta(0.04) == "REJECT"
    assert verdict_from_abs_delta(0.049) == "REJECT"
    assert verdict_from_abs_delta(0.05) == "INCONCLUSIVE"
    assert verdict_from_abs_delta(0.14) == "INCONCLUSIVE"
    assert verdict_from_abs_delta(0.15) == "SUPPORT"
    assert SUPPORT_ABS_DELTA == 0.15
    assert KILL_ABS_DELTA == 0.05


if __name__ == "__main__":
    test_is_registry_pels()
    test_tss_dist_bin_edges()
    test_quantile_bins_four()
    test_match_1to1_no_reuse()
    test_match_undermatched()
    test_cliffs_delta_identical()
    test_cliffs_delta_separated()
    test_verdict_gates()
    print("OK")
