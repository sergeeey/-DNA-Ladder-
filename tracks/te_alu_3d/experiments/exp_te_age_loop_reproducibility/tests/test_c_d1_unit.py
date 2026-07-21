#!/usr/bin/env python3
"""Unit tests for C-D1 helpers (no large downloads required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from c_d1_lib import (  # noqa: E402
    MCID_KILL,
    MCID_SUPPORT,
    assign_tertile,
    fisher_or_woolf,
    merge_intervals,
    midpoint_windows,
    overlaps_any,
    tertile_cuts,
    verdict_delta,
)


def test_claim_prereg_exists():
    claim = (ROOT / "claim.md").read_text(encoding="utf-8")
    assert "C-D1" in claim
    assert "milliDiv" in claim
    assert "ENCFF511QFN" in claim
    assert "ENCFF693XIL" in claim
    assert "0.10" in claim


def test_tertile_and_verdict():
    vals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    q33, q66 = tertile_cuts(vals)
    assert q33 < q66
    assert assign_tertile(1.0, q33, q66) == 0
    assert assign_tertile(9.0, q33, q66) == 2
    assert verdict_delta(0.12) == "SUPPORT"
    assert verdict_delta(0.02) == "REJECT"
    assert verdict_delta(0.07) == "INCONCLUSIVE"
    assert MCID_SUPPORT == 0.10
    assert MCID_KILL == 0.05


def test_merge_midpoint_overlap():
    merged = merge_intervals([("chr1", 100, 200), ("chr1", 150, 300), ("chr1", 500, 600)])
    assert merged == [("chr1", 100, 300), ("chr1", 500, 600)]
    mids = midpoint_windows([("chr1", 0, 100)])
    assert mids[0][2] - mids[0][1] == 1000
    ivs = [(0, 100), (200, 300), (400, 500)]
    assert overlaps_any(90, 110, ivs) is True
    assert overlaps_any(150, 180, ivs) is False
    # TE milli helper
    from c_d1_lib import min_milli_overlap

    te = [(0, 50, 200, "a", "SINE", "Alu"), (80, 120, 50, "b", "SINE", "Alu")]
    milli, cls, fam = min_milli_overlap(90, 110, te)
    assert milli == 50 and cls == "SINE"
    assert min_milli_overlap(150, 180, te)[0] is None


def test_fisher_or():
    or_, lo, hi, _p = fisher_or_woolf(20, 80, 10, 90)
    assert or_ > 1.0
    assert lo < or_ < hi


if __name__ == "__main__":
    test_claim_prereg_exists()
    test_tertile_and_verdict()
    test_merge_midpoint_overlap()
    test_fisher_or()
    print("OK")
