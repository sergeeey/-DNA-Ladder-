#!/usr/bin/env python3
"""Unit tests for C-J1 helpers (no large downloads required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from c_j1_lib import (  # noqa: E402
    MCID_KILL,
    MCID_SUPPORT,
    max_overlap_strand,
    unitize_anchor,
    verdict_abs_delta,
)


def test_claim_prereg_exists():
    claim = (ROOT / "claim.md").read_text(encoding="utf-8")
    assert "C-J1" in claim
    assert "orientation" in claim.lower() or "Δ_orient" in claim or "delta_orient" in claim.lower()
    assert "ENCFF693XIL" in claim
    assert "0.10" in claim
    assert "0.05" in claim


def test_verdict_thresholds():
    assert verdict_abs_delta(0.12) == "SUPPORT"
    assert verdict_abs_delta(0.02) == "REJECT"
    assert verdict_abs_delta(0.07) == "INCONCLUSIVE"
    assert MCID_SUPPORT == 0.10
    assert MCID_KILL == 0.05


def test_unitize_and_max_overlap_strand():
    u = unitize_anchor("chr1", 100, 200)
    assert u[0] == "chr1"
    assert u[2] - u[1] == 1000
    te = [
        (0, 50, "+", "a", "SINE", "Alu"),
        (80, 150, "-", "b", "SINE", "Alu"),  # overlap 70 bp with [90,110] → wait
        (90, 200, "+", "c", "LINE", "L1"),
    ]
    # window [90, 110]: b overlaps 20, c overlaps 20 → tie by earliest start → b (−)
    assert max_overlap_strand(90, 110, te) == "-"
    # window [0, 40]: only a
    assert max_overlap_strand(0, 40, te) == "+"
    assert max_overlap_strand(300, 400, te) is None


def test_max_overlap_prefers_larger():
    te = [
        (0, 20, "+", "a", "SINE", "Alu"),
        (10, 100, "-", "b", "SINE", "Alu"),
    ]
    # window [0, 50]: a ov=20, b ov=40 → −
    assert max_overlap_strand(0, 50, te) == "-"


if __name__ == "__main__":
    test_claim_prereg_exists()
    test_verdict_thresholds()
    test_unitize_and_max_overlap_strand()
    test_max_overlap_prefers_larger()
    print("OK")
