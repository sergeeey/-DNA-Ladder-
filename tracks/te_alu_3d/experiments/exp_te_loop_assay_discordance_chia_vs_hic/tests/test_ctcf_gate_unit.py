#!/usr/bin/env python3
"""Unit tests for T2 CTCF positive-control gate helpers (no network, no ENCODE files)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from t2_positive_control_ctcf_gate import (  # noqa: E402
    build_interval_index,
    fisher_exact_two_sided,
    overlaps_any,
    woolf_or_ci,
)


class TestOverlaps(unittest.TestCase):
    def test_overlap_hit(self):
        idx = build_interval_index([("chr1", 100, 200), ("chr1", 500, 600)])
        self.assertTrue(overlaps_any("chr1", 150, 160, idx))
        self.assertTrue(overlaps_any("chr1", 90, 101, idx))
        self.assertFalse(overlaps_any("chr1", 200, 250, idx))  # half-open end
        self.assertFalse(overlaps_any("chr2", 100, 150, idx))

    def test_touching_endpoints(self):
        idx = build_interval_index([("chr1", 100, 200)])
        self.assertFalse(overlaps_any("chr1", 200, 300, idx))
        self.assertTrue(overlaps_any("chr1", 199, 201, idx))


class TestFisher(unittest.TestCase):
    def test_strong_enrichment_or_above_threshold(self):
        # 80/20 vs 20/80 → OR = 16
        or_, p = fisher_exact_two_sided(80, 20, 20, 80)
        self.assertGreaterEqual(or_, 2.0)
        self.assertLess(p, 0.01)

    def test_nullish_table_or_near_one(self):
        or_, p = fisher_exact_two_sided(50, 50, 50, 50)
        self.assertAlmostEqual(or_, 1.0, places=2)
        self.assertGreater(p, 0.5)

    def test_woolf_ci_contains_point(self):
        or_, lo, hi = woolf_or_ci(80, 20, 20, 80)
        self.assertLessEqual(lo, or_)
        self.assertGreaterEqual(hi, or_)
        self.assertGreater(lo, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
