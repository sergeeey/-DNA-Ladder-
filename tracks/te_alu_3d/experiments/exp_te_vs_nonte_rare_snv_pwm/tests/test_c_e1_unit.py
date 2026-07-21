#!/usr/bin/env python3
"""Unit tests for C-E1 helpers + claim/decision freeze artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from c_e1_lib import (  # noqa: E402
    KILL_ABS_DELTA,
    SUPPORT_ABS_DELTA,
    cliffs_delta,
    excluded_pos,
    is_snv,
    match_1to1,
    merge_intervals,
    quantile_bins,
    te_overlap_at,
    verdict_delta,
)
import numpy as np


def test_claim_and_decision():
    claim = (ROOT / "claim.md").read_text(encoding="utf-8")
    assert "C-E1" in claim
    assert "non-HBB" in claim
    assert "0.20" in claim
    decision = (ROOT / "decision.md").read_text(encoding="utf-8")
    assert "REJECT" in decision
    assert "0.033" in decision or "FAIL_KILL" in decision


def test_exclusions():
    assert excluded_pos(5_250_001) is True  # HBB
    assert excluded_pos(65_000_001) is True  # holdout
    assert excluded_pos(10_000_000) is False


def test_cliffs_identical_and_separated():
    xs = [1.0, 2.0, 3.0, 4.0]
    assert abs(cliffs_delta(xs, xs)) < 1e-9
    a = [10.0, 11.0, 12.0, 13.0]
    b = [0.0, 1.0, 2.0, 3.0]
    d = cliffs_delta(a, b)
    assert d > 0.9


def test_verdict_gates():
    assert verdict_delta(0.01) == "REJECT"
    assert verdict_delta(0.10) == "INCONCLUSIVE"
    assert verdict_delta(0.25) == "SUPPORT"
    assert SUPPORT_ABS_DELTA == 0.20
    assert KILL_ABS_DELTA == 0.05


def test_match_and_bins():
    bins = quantile_bins(np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]), 4)
    assert len(bins) == 8
    assert set(bins.tolist()) <= {0, 1, 2, 3}
    pool = {("chr11", 0): ["n1", "n2"], ("chr11", 1): ["n3"]}
    exposed = [("t1", ("chr11", 0)), ("t2", ("chr11", 0)), ("t3", ("chr11", 1))]
    m = match_1to1(exposed, pool, seed=20260721)
    assert m["t1"] is not None
    assert m["t2"] is not None
    assert m["t3"] == "n3"
    assert m["t1"] != m["t2"]


def test_te_overlap_and_merge():
    te = {"chr11": [(100, 200, "AluY"), (500, 600, "SVA_F")]}
    assert te_overlap_at("chr11", 150, te) == "AluY"
    assert te_overlap_at("chr11", 250, te) is None
    assert te_overlap_at("chr11", 550, te) == "SVA_F"
    merged = merge_intervals(
        [("chr11", 0, 10), ("chr11", 8, 20), ("chr11", 100, 110)]
    )
    assert merged == [("chr11", 0, 20), ("chr11", 100, 110)]
    assert is_snv("A", "G")
    assert not is_snv("A", "GG")


def test_primary_result_on_disk():
    primary = json.loads(
        (ROOT / "results" / "primary_result_cliffs_delta.json").read_text(encoding="utf-8")
    )
    assert primary["candidate_id"] == "C-E1"
    assert primary["verdict"] == "REJECT"
    assert abs(primary["cliffs_delta"]) < KILL_ABS_DELTA
    lock = json.loads((ROOT / "results" / "matching_lock.json").read_text(encoding="utf-8"))
    assert lock["locked_before_pwm"] is True
    assert lock["n_matched_pairs"] == primary["n_scored_pairs"]


if __name__ == "__main__":
    test_claim_and_decision()
    test_exclusions()
    test_cliffs_identical_and_separated()
    test_verdict_gates()
    test_match_and_bins()
    test_te_overlap_and_merge()
    test_primary_result_on_disk()
    print("OK")
