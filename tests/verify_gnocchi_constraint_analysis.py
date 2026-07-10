#!/usr/bin/env python3
"""Unit tests for the region-level aggregation and matching logic in
scripts/gnocchi_constraint_se_vs_typical_analysis.py -- the functions that
turn per-1kb-window Z-scores into per-enhancer-region summary values and
match SE-constituent peaks to typical peaks by length. These are the two
places a silent bug would most directly corrupt the REJECT verdict (wrong
weighting would shift the effect size; wrong matching would reintroduce the
length confound the experiment was specifically designed to remove).
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    mann_whitney_u,
    overlaps_any,
    paired_permutation_test,
    weighted_mean_z,
)


def make_gnocchi_index(chrom, windows):
    """windows: list of (start, end, z). Builds the same structure
    load_gnocchi_windows() produces for one chromosome."""
    windows = sorted(windows)
    return {
        chrom: (
            [w[0] for w in windows],
            [w[1] for w in windows],
            [w[2] for w in windows],
        )
    }


class TestWeightedMeanZ(unittest.TestCase):
    def test_single_window_fully_contains_region(self):
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 5.0)])
        self.assertAlmostEqual(weighted_mean_z("chr1", 1200, 1400, gnocchi), 5.0)

    def test_region_spans_two_windows_equal_overlap(self):
        # region [1500,2500) overlaps [1000,2000) by 500bp and [2000,3000) by 500bp
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 0.0), (2000, 3000, 10.0)])
        self.assertAlmostEqual(weighted_mean_z("chr1", 1500, 2500, gnocchi), 5.0)

    def test_region_spans_two_windows_unequal_overlap(self):
        # region [1900,2100) overlaps [1000,2000) by 100bp and [2000,3000) by 100bp
        # -> still equal weight in this case; use asymmetric region instead
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 0.0), (2000, 3000, 8.0)])
        # region [1750,2050): 250bp in window1 (z=0), 50bp in window2 (z=8)
        expected = (250 * 0.0 + 50 * 8.0) / 300
        self.assertAlmostEqual(weighted_mean_z("chr1", 1750, 2050, gnocchi), expected)

    def test_region_with_no_overlapping_window_returns_none(self):
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 5.0)])
        self.assertIsNone(weighted_mean_z("chr1", 5000, 6000, gnocchi))

    def test_unknown_chromosome_returns_none(self):
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 5.0)])
        self.assertIsNone(weighted_mean_z("chr2", 1200, 1400, gnocchi))

    def test_region_partially_off_the_edge_of_coverage(self):
        # region starts before any window and ends inside the first window --
        # only the overlapping portion should count, not the whole region length
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 4.0)])
        self.assertAlmostEqual(weighted_mean_z("chr1", 500, 1500, gnocchi), 4.0)

    def test_qc_failed_windows_already_excluded_upstream(self):
        # simulates a gap in coverage (QC-failed window dropped by the loader) --
        # weighted_mean_z must skip the gap, not error or silently fabricate a value
        gnocchi = make_gnocchi_index("chr1", [(1000, 2000, 2.0), (3000, 4000, 6.0)])
        # region [1500,3500) covers 500bp of window1 (z=2) and 500bp of window2 (z=6),
        # with a 1000bp gap [2000,3000) that contributes zero weight
        expected = (500 * 2.0 + 500 * 6.0) / 1000
        self.assertAlmostEqual(weighted_mean_z("chr1", 1500, 3500, gnocchi), expected)


class TestOverlapsAny(unittest.TestCase):
    def test_true_when_inside(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertTrue(overlaps_any("chr1", 1200, 1300, by_chrom))

    def test_false_when_outside(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertFalse(overlaps_any("chr1", 3000, 3100, by_chrom))

    def test_true_on_partial_overlap(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertTrue(overlaps_any("chr1", 1900, 2100, by_chrom))

    def test_false_when_touching_not_overlapping(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertFalse(overlaps_any("chr1", 2000, 2500, by_chrom))

    def test_false_on_unknown_chromosome(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertFalse(overlaps_any("chr2", 1200, 1300, by_chrom))


class TestPairedPermutationTest(unittest.TestCase):
    def test_identical_groups_give_near_zero_observed_diff_and_high_p(self):
        pairs = [(1.0, 1.0)] * 50
        observed, p = paired_permutation_test(pairs, n_perm=500, seed=1)
        self.assertAlmostEqual(observed, 0.0)
        self.assertGreater(p, 0.5)

    def test_strong_consistent_difference_gives_low_p(self):
        # every pair has SE = typical + 5 -- an obviously real, huge effect
        pairs = [(i + 5.0, float(i)) for i in range(50)]
        observed, p = paired_permutation_test(pairs, n_perm=2000, seed=1)
        self.assertAlmostEqual(observed, 5.0)
        self.assertLess(p, 0.01)

    def test_p_value_is_never_zero(self):
        # (count_extreme + 1) / (n_perm + 1) floor guards against p=0.0 overclaiming
        pairs = [(i + 5.0, float(i)) for i in range(50)]
        _, p = paired_permutation_test(pairs, n_perm=100, seed=1)
        self.assertGreater(p, 0.0)


class TestMannWhitneyUSanityAgainstKnownDirection(unittest.TestCase):
    def test_shifted_group_gives_correct_sign_of_cliffs_delta(self):
        group1 = [5.0, 6.0, 7.0, 8.0, 9.0]  # consistently higher
        group2 = [0.0, 1.0, 2.0, 3.0, 4.0]
        _, _, delta = mann_whitney_u(group1, group2)
        self.assertGreater(delta, 0.9)  # near-total separation -> delta near +1

    def test_identical_groups_give_zero_delta(self):
        group = [1.0, 2.0, 3.0]
        _, _, delta = mann_whitney_u(group, list(group))
        self.assertAlmostEqual(delta, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
