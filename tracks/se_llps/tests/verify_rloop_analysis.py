#!/usr/bin/env python3
"""Unit tests for overlap_fraction in scripts/rloop_se_vs_typical_analysis.py --
the one genuinely new function in that script (matching/mann_whitney_u/
paired_permutation_test are reused, already-tested code from
gnocchi_constraint_se_vs_typical_analysis.py). A bug here would directly
corrupt the R-loop overlap fractions the REJECT verdict is based on.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from rloop_se_vs_typical_analysis import overlap_fraction  # noqa: E402


def make_rloop_index(chrom, peaks):
    peaks = sorted(peaks)
    return {chrom: peaks}


class TestOverlapFraction(unittest.TestCase):
    def test_no_peaks_on_chromosome_returns_zero(self):
        rloop = make_rloop_index("chr1", [])
        self.assertEqual(overlap_fraction("chr1", 1000, 2000, rloop), 0.0)

    def test_unknown_chromosome_returns_zero(self):
        rloop = make_rloop_index("chr1", [(1000, 2000)])
        self.assertEqual(overlap_fraction("chr2", 1000, 2000, rloop), 0.0)

    def test_region_fully_contains_peak(self):
        rloop = make_rloop_index("chr1", [(1400, 1600)])
        # region [1000,2000) is 1000bp, peak contributes 200bp -> 0.2
        self.assertAlmostEqual(overlap_fraction("chr1", 1000, 2000, rloop), 0.2)

    def test_peak_fully_contains_region(self):
        rloop = make_rloop_index("chr1", [(0, 10000)])
        self.assertAlmostEqual(overlap_fraction("chr1", 1000, 2000, rloop), 1.0)

    def test_no_overlap_returns_zero(self):
        rloop = make_rloop_index("chr1", [(5000, 6000)])
        self.assertEqual(overlap_fraction("chr1", 1000, 2000, rloop), 0.0)

    def test_touching_not_overlapping_returns_zero(self):
        rloop = make_rloop_index("chr1", [(2000, 3000)])
        self.assertEqual(overlap_fraction("chr1", 1000, 2000, rloop), 0.0)

    def test_multiple_peaks_sum_correctly(self):
        # region [1000,2000): peak1 [1100,1200) = 100bp, peak2 [1800,1900) = 100bp
        rloop = make_rloop_index("chr1", [(1100, 1200), (1800, 1900)])
        self.assertAlmostEqual(overlap_fraction("chr1", 1000, 2000, rloop), 200 / 1000)

    def test_partial_overlap_at_left_edge(self):
        rloop = make_rloop_index("chr1", [(500, 1500)])
        # region [1000,2000): overlap is [1000,1500) = 500bp
        self.assertAlmostEqual(overlap_fraction("chr1", 1000, 2000, rloop), 0.5)

    def test_zero_length_region_returns_zero_not_error(self):
        rloop = make_rloop_index("chr1", [(1000, 2000)])
        self.assertEqual(overlap_fraction("chr1", 1500, 1500, rloop), 0.0)

    def test_fraction_clamped_to_one_if_input_peaks_overlap_each_other(self):
        # load_rloop_peaks() merges overlapping peaks before this function ever
        # sees them, but overlap_fraction has a defensive clamp regardless --
        # verifies the backstop, not "correctness" for out-of-contract input
        # (two overlapping-with-each-other peaks both inside the region would
        # double-count to 1.2 without the clamp).
        rloop = make_rloop_index("chr1", [(1000, 1600), (1400, 2000)])
        result = overlap_fraction("chr1", 1000, 2000, rloop)
        self.assertEqual(result, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
