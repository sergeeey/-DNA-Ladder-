#!/usr/bin/env python3
"""Unit tests for the new logic in
scripts/se_continuous_rank_dichotomization_check.py: find_enclosing_se,
ranks_of, pearson_on_ranks, and permutation_test_correlation. These
functions directly determine the correlation/p-values the decision.md
verdict is based on -- a silent bug here would corrupt the "partial signal"
finding.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from se_continuous_rank_dichotomization_check import (  # noqa: E402
    find_enclosing_se,
    pearson_on_ranks,
    permutation_test_correlation,
    ranks_of,
    spearman,
)


class TestFindEnclosingSE(unittest.TestCase):
    def test_returns_interval_when_inside(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertEqual(find_enclosing_se("chr1", 1200, 1300, by_chrom), (1000, 2000))

    def test_returns_none_when_outside(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertIsNone(find_enclosing_se("chr1", 3000, 3100, by_chrom))

    def test_returns_none_on_unknown_chromosome(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertIsNone(find_enclosing_se("chr2", 1200, 1300, by_chrom))

    def test_partial_overlap_still_counts(self):
        by_chrom = {"chr1": [(1000, 2000)]}
        self.assertEqual(find_enclosing_se("chr1", 1900, 2100, by_chrom), (1000, 2000))


class TestRanksOf(unittest.TestCase):
    def test_no_ties_gives_integer_ranks(self):
        self.assertEqual(ranks_of([30, 10, 20]), [3.0, 1.0, 2.0])

    def test_ties_get_average_rank(self):
        # values 10,10,20 -> ranks 1,2,3 but the two 10s share rank 1.5
        self.assertEqual(ranks_of([10, 10, 20]), [1.5, 1.5, 3.0])

    def test_all_equal_gives_same_middle_rank(self):
        self.assertEqual(ranks_of([5, 5, 5]), [2.0, 2.0, 2.0])


class TestPearsonOnRanksAndSpearman(unittest.TestCase):
    def test_perfect_monotonic_relationship_gives_rho_one(self):
        xs = [1, 2, 3, 4, 5]
        ys = [10, 20, 30, 40, 50]
        self.assertAlmostEqual(spearman(xs, ys), 1.0)

    def test_perfect_inverse_relationship_gives_rho_minus_one(self):
        xs = [1, 2, 3, 4, 5]
        ys = [50, 40, 30, 20, 10]
        self.assertAlmostEqual(spearman(xs, ys), -1.0)

    def test_no_relationship_gives_near_zero(self):
        # brute-force-verified: this permutation gives exactly rho=0.0 against
        # 1..8, not an assumption about "looks random enough"
        xs = [1, 2, 3, 4, 5, 6, 7, 8]
        ys = [1, 4, 6, 7, 8, 5, 3, 2]
        self.assertAlmostEqual(spearman(xs, ys), 0.0)

    def test_constant_vector_gives_zero_not_error(self):
        xs = [5, 5, 5, 5]
        ys = [1, 2, 3, 4]
        self.assertEqual(spearman(xs, ys), 0.0)

    def test_pearson_on_ranks_matches_spearman(self):
        xs = [5, 3, 8, 1, 9]
        ys = [2, 4, 6, 1, 8]
        self.assertAlmostEqual(pearson_on_ranks(ranks_of(xs), ranks_of(ys)), spearman(xs, ys))


class TestPermutationTestCorrelation(unittest.TestCase):
    def test_observed_matches_spearman(self):
        xs = [1, 2, 3, 4, 5, 6, 7, 8]
        ys = [8, 7, 6, 5, 4, 3, 2, 1]
        observed, p = permutation_test_correlation(xs, ys, 200, seed=1)
        self.assertAlmostEqual(observed, spearman(xs, ys))

    def test_strong_relationship_gives_low_p(self):
        xs = list(range(30))
        ys = list(range(30))
        _, p = permutation_test_correlation(xs, ys, 500, seed=1)
        self.assertLess(p, 0.05)

    def test_p_value_never_zero(self):
        xs = list(range(20))
        ys = list(range(20))
        _, p = permutation_test_correlation(xs, ys, 100, seed=1)
        self.assertGreater(p, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
