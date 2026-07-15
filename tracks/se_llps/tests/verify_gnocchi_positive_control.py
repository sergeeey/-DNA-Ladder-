#!/usr/bin/env python3
"""Unit tests for the intergenic-sampling logic in
scripts/gnocchi_positive_control_analysis.py -- specifically far_from_any_tss,
the one piece of genuinely new logic in that script (the rest reuses
already-tested weighted_mean_z / mann_whitney_u / paired_permutation_test
from gnocchi_constraint_se_vs_typical_analysis.py). A bug here could let
near-gene (potentially constrained) regions leak into the "intergenic"
control group, which would shrink the expected effect size and undermine
the positive control's own validity.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gnocchi_positive_control_analysis import far_from_any_tss  # noqa: E402


class TestFarFromAnyTss(unittest.TestCase):
    def setUp(self):
        self.tss_by_chrom = {"chr1": [10_000, 50_000, 200_000]}

    def test_position_exactly_at_min_distance_is_far_enough(self):
        # 10_000 - 100_000 would be negative; use the 200_000 TSS instead
        self.assertTrue(far_from_any_tss("chr1", 300_000, self.tss_by_chrom, 100_000))

    def test_position_just_inside_exclusion_zone_is_not_far(self):
        self.assertFalse(far_from_any_tss("chr1", 250_000, self.tss_by_chrom, 100_000))

    def test_position_far_from_all_tss_is_far(self):
        self.assertTrue(far_from_any_tss("chr1", 1_000_000, self.tss_by_chrom, 100_000))

    def test_position_near_first_tss_in_list_is_not_far(self):
        self.assertFalse(far_from_any_tss("chr1", 10_050, self.tss_by_chrom, 100_000))

    def test_unknown_chromosome_is_treated_as_far(self):
        # no TSS data for this chromosome -- conservative default: don't block sampling
        self.assertTrue(far_from_any_tss("chr99", 5000, self.tss_by_chrom, 100_000))

    def test_position_between_two_close_tss_neither_within_range(self):
        tss_by_chrom = {"chr1": [0, 500_000]}
        self.assertTrue(far_from_any_tss("chr1", 250_000, tss_by_chrom, 100_000))


if __name__ == "__main__":
    unittest.main(verbosity=2)
