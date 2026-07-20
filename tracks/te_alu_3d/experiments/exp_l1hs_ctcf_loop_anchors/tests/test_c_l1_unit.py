#!/usr/bin/env python3
"""Unit tests for C-L1 helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from c_l1_lib import fisher_or_woolf, match_1to1, verdict_or  # noqa: E402


def test_fisher_symmetric():
    or_, lo, hi, _p = fisher_or_woolf(10, 10, 10, 10)
    assert abs(or_ - 1.0) < 0.05


def test_fisher_enriched():
    or_, lo, hi, _p = fisher_or_woolf(50, 50, 5, 95)
    assert or_ > 1.4
    assert lo > 1.0


def test_match_no_reuse():
    exposed = [("e1", ("chr1", 0, 0)), ("e2", ("chr1", 0, 0))]
    pool = {("chr1", 0, 0): ["c1", "c2"]}
    m = match_1to1(exposed, pool, seed=1)
    assert m["e1"] != m["e2"]


def test_verdict_gates():
    assert verdict_or(1.5, 1.5) == "SUPPORT"
    assert verdict_or(1.5, 1.0) == "REJECT"
    assert verdict_or(1.0, 1.0) == "REJECT"
    assert verdict_or(1.2, 1.2) == "INCONCLUSIVE"


if __name__ == "__main__":
    test_fisher_symmetric()
    test_fisher_enriched()
    test_match_no_reuse()
    test_verdict_gates()
    print("OK")
