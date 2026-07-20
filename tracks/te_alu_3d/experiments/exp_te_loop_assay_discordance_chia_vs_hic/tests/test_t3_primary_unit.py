#!/usr/bin/env python3
"""Unit tests for T3 primary AluSz OR helpers (no network, no ENCODE files)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from t3_primary_alusz_or import (  # noqa: E402
    build_units,
    contingency_or,
    desk_verdict,
    fisher_exact_two_sided,
    merge_intervals,
    midpoint_windows,
    overlaps_any,
    pad_min_width,
    woolf_or_ci,
)


class TestMergePad(unittest.TestCase):
    def test_merge_bookended(self):
        merged = merge_intervals(
            [("chr1", 0, 100), ("chr1", 100, 200), ("chr1", 500, 600)]
        )
        self.assertEqual(merged, [("chr1", 0, 200), ("chr1", 500, 600)])

    def test_pad_to_1kb(self):
        padded = pad_min_width([("chr1", 100, 200)], min_bp=1000)
        self.assertEqual(padded[0][2] - padded[0][1], 1000)

    def test_build_units_ge1kb(self):
        units = build_units(
            [("chr1", 0, 100), ("chr1", 50, 150), ("chr2", 0, 5000)], min_bp=1000
        )
        self.assertTrue(all(e - s >= 1000 for _, s, e in units))
        self.assertEqual(len(units), 2)

    def test_midpoint_windows_fixed_1kb(self):
        wins = midpoint_windows([("chr1", 0, 10000), ("chr2", 100, 200)], win_bp=1000)
        self.assertTrue(all(e - s == 1000 for _, s, e in wins))
        self.assertEqual(wins[0], ("chr1", 4500, 5500))


class TestOverlap(unittest.TestCase):
    def test_overlap(self):
        ivs = [(100, 200), (500, 600)]
        self.assertTrue(overlaps_any(150, 160, ivs))
        self.assertFalse(overlaps_any(200, 250, ivs))
        self.assertTrue(overlaps_any(199, 201, ivs))


class TestFisherVerdict(unittest.TestCase):
    def test_enrichment_table(self):
        or_, p = fisher_exact_two_sided(80, 20, 20, 80)
        self.assertGreaterEqual(or_, 1.3)
        self.assertLess(p, 0.01)

    def test_contingency_rates(self):
        r = contingency_or([True, True, False, False], [True, False, False, False])
        self.assertEqual(r["a_pol2_te_pos"], 2)
        self.assertEqual(r["c_hic_te_pos"], 1)
        self.assertGreater(r["fisher_or"], 1.0)

    def test_desk_verdict_thresholds(self):
        self.assertEqual(desk_verdict(1.5, 1.2, 1.8)["verdict"], "SUPPORT_DESK")
        self.assertEqual(desk_verdict(1.05, 0.9, 1.2)["verdict"], "FAIL_DESK_PRIMARY")
        self.assertEqual(desk_verdict(1.2, 1.0, 1.4)["verdict"], "INCONCLUSIVE_DESK")

    def test_woolf_ci(self):
        or_, lo, hi = woolf_or_ci(80, 20, 20, 80)
        self.assertLessEqual(lo, or_)
        self.assertGreaterEqual(hi, or_)


if __name__ == "__main__":
    unittest.main(verbosity=2)
