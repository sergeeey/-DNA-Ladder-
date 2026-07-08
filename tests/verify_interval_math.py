#!/usr/bin/env python3
"""Permanent unit/property tests for the interval-math functions in
scripts/llps_promoter_vs_se_analysis.py and scripts/liftover.py.

Written after Agent(reviewer) fuzz-tested subtract_intervals() against a
brute-force bitmap reference (2000 randomized trials, 0 failures) during
review of exp_llps_promoter_vs_se_chip_evidence and recommended committing
that kind of check permanently rather than re-deriving confidence each
session (see decision.md's "Verification" section for that review).
Also covers the confirmed-and-fixed off-by-one in liftover.py's
reverse-strand branch, as a regression test.

Run: python tests/verify_interval_math.py
"""

import os
import random
import sys
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))

from liftover import Chain, lift_point  # noqa: E402
from llps_promoter_vs_se_analysis import (  # noqa: E402
    merge_intervals,
    point_in_intervals,
    subtract_intervals,
)


def intervals_to_bitmap(intervals, size):
    bitmap = [False] * size
    for s, e in intervals:
        for i in range(max(0, s), min(size, e)):
            bitmap[i] = True
    return bitmap


def bitmap_to_intervals(bitmap):
    intervals = []
    start = None
    for i, v in enumerate(bitmap):
        if v and start is None:
            start = i
        elif not v and start is not None:
            intervals.append((start, i))
            start = None
    if start is not None:
        intervals.append((start, len(bitmap)))
    return intervals


class TestMergeIntervals(unittest.TestCase):
    def test_touching_intervals_merge(self):
        merged, total_bp = merge_intervals({"chr1": [(100, 200), (200, 300)]})
        self.assertEqual(merged["chr1"], [(100, 300)])
        self.assertEqual(total_bp, 200)

    def test_overlapping_intervals_merge(self):
        merged, total_bp = merge_intervals({"chr1": [(100, 250), (200, 300)]})
        self.assertEqual(merged["chr1"], [(100, 300)])
        self.assertEqual(total_bp, 200)

    def test_disjoint_intervals_stay_separate(self):
        merged, total_bp = merge_intervals({"chr1": [(100, 200), (300, 400)]})
        self.assertEqual(merged["chr1"], [(100, 200), (300, 400)])
        self.assertEqual(total_bp, 200)

    def test_unsorted_input_still_merges_correctly(self):
        merged, _ = merge_intervals({"chr1": [(300, 400), (100, 200), (150, 350)]})
        self.assertEqual(merged["chr1"], [(100, 400)])


class TestSubtractIntervals(unittest.TestCase):
    def test_no_overlap_returns_a_unchanged(self):
        a = {"chr1": [(100, 200)]}
        b = {"chr1": [(300, 400)]}
        result, bp = subtract_intervals(a, b)
        self.assertEqual(result["chr1"], [(100, 200)])
        self.assertEqual(bp, 100)

    def test_b_fully_contains_a(self):
        a = {"chr1": [(100, 200)]}
        b = {"chr1": [(50, 250)]}
        result, bp = subtract_intervals(a, b)
        self.assertEqual(result["chr1"], [])
        self.assertEqual(bp, 0)

    def test_b_overlaps_a_left_edge(self):
        a = {"chr1": [(100, 200)]}
        b = {"chr1": [(50, 150)]}
        result, bp = subtract_intervals(a, b)
        self.assertEqual(result["chr1"], [(150, 200)])
        self.assertEqual(bp, 50)

    def test_b_overlaps_a_right_edge(self):
        a = {"chr1": [(100, 200)]}
        b = {"chr1": [(150, 250)]}
        result, bp = subtract_intervals(a, b)
        self.assertEqual(result["chr1"], [(100, 150)])
        self.assertEqual(bp, 50)

    def test_multiple_b_intervals_carve_out_middle(self):
        a = {"chr1": [(100, 300)]}
        b = {"chr1": [(150, 180), (200, 220)]}
        result, bp = subtract_intervals(a, b)
        self.assertEqual(result["chr1"], [(100, 150), (180, 200), (220, 300)])
        self.assertEqual(bp, 50 + 20 + 80)

    def test_touching_not_overlapping_b_does_not_remove_a(self):
        a = {"chr1": [(100, 200)]}
        b = {"chr1": [(200, 300)]}
        result, bp = subtract_intervals(a, b)
        self.assertEqual(result["chr1"], [(100, 200)])
        self.assertEqual(bp, 100)

    def test_never_produces_negative_length_or_out_of_bounds(self):
        random.seed(42)
        for _ in range(500):
            size = 200
            n_a = random.randint(1, 5)
            n_b = random.randint(1, 5)
            a_bitmap = [False] * size
            b_bitmap = [False] * size
            for _ in range(n_a):
                s = random.randint(0, size - 1)
                e = random.randint(s + 1, size)
                for i in range(s, e):
                    a_bitmap[i] = True
            for _ in range(n_b):
                s = random.randint(0, size - 1)
                e = random.randint(s + 1, size)
                for i in range(s, e):
                    b_bitmap[i] = True

            a_intervals = {"chr1": bitmap_to_intervals(a_bitmap)}
            b_intervals = {"chr1": bitmap_to_intervals(b_bitmap)}
            a_merged, _ = merge_intervals(a_intervals)
            b_merged, _ = merge_intervals(b_intervals)
            result, bp = subtract_intervals(a_merged, b_merged)

            expected_bitmap = [a_bitmap[i] and not b_bitmap[i] for i in range(size)]
            expected_intervals = bitmap_to_intervals(expected_bitmap)
            expected_bp = sum(e - s for s, e in expected_intervals)

            self.assertEqual(result.get("chr1", []), expected_intervals)
            self.assertEqual(bp, expected_bp)
            for s, e in result.get("chr1", []):
                self.assertGreater(e, s, "negative or zero-length interval produced")
                self.assertGreaterEqual(s, 0)
                self.assertLessEqual(e, size)


class TestPointInIntervals(unittest.TestCase):
    def setUp(self):
        self.merged, _ = merge_intervals({"chr1": [(100, 200), (300, 400)]})

    def test_point_inside_first_interval(self):
        self.assertTrue(point_in_intervals("chr1", 150, self.merged))

    def test_point_at_exact_start(self):
        self.assertTrue(point_in_intervals("chr1", 100, self.merged))

    def test_point_at_exact_end_is_excluded(self):
        # half-open convention: [start, end)
        self.assertFalse(point_in_intervals("chr1", 200, self.merged))

    def test_point_in_gap_between_intervals(self):
        self.assertFalse(point_in_intervals("chr1", 250, self.merged))

    def test_point_before_first_interval(self):
        self.assertFalse(point_in_intervals("chr1", 50, self.merged))

    def test_point_after_last_interval(self):
        self.assertFalse(point_in_intervals("chr1", 450, self.merged))

    def test_unknown_chromosome(self):
        self.assertFalse(point_in_intervals("chrUnknown", 150, self.merged))


class TestLiftoverReverseStrand(unittest.TestCase):
    """Regression test for the confirmed-and-fixed off-by-one bug (2026-07-08,
    Agent(reviewer) review): chain.q_size - (q_block_start + offset) needed a
    -1 since q_size is an exclusive length, not a valid max index."""

    def test_reverse_strand_endpoints_map_to_valid_indices(self):
        chains = defaultdict(list)
        chains["chr1"].append(Chain(0, 10, 0, "-", 10, [(0, 10, 0)]))
        chains = dict(chains)

        t0 = lift_point(chains, "chr1", 0)
        t9 = lift_point(chains, "chr1", 9)

        self.assertEqual(t0, ("chr1", 9))
        self.assertEqual(t9, ("chr1", 0))
        # neither result should ever equal q_size (10) -- that was the bug's signature
        self.assertNotEqual(t0[1], 10)
        self.assertNotEqual(t9[1], 10)

    def test_forward_strand_unaffected(self):
        chains = defaultdict(list)
        chains["chr1"].append(Chain(0, 10, 100, "+", 10, [(0, 10, 100)]))
        chains = dict(chains)
        self.assertEqual(lift_point(chains, "chr1", 0), ("chr1", 100))
        self.assertEqual(lift_point(chains, "chr1", 9), ("chr1", 109))


if __name__ == "__main__":
    unittest.main(verbosity=2)
