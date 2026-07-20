#!/usr/bin/env python3
"""Unit tests for C-B1 topology kill-test helpers (no large downloads required)."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXP / "scripts"))

from kill_test_chr_holdout import (  # noqa: E402
    LoopGraph,
    interval_hits,
    overlaps,
    verdict_from_delta,
)


class TestOverlaps(unittest.TestCase):
    def test_overlap_true(self):
        self.assertTrue(overlaps(100, 200, 150, 250))

    def test_touching_false(self):
        self.assertFalse(overlaps(100, 200, 200, 300))

    def test_interval_hits_binary_search(self):
        ivs = [(0, 10), (20, 30), (40, 50)]
        self.assertTrue(interval_hits(ivs, 25, 26))
        self.assertFalse(interval_hits(ivs, 10, 20))
        self.assertTrue(interval_hits(ivs, 45, 60))


class TestLoopGraph(unittest.TestCase):
    def setUp(self):
        # Three anchors A-B-C in a path; A overlaps enh, C overlaps prom
        # A: 100-200, B: 1000-1100, C: 5000-5100
        self.loops = [
            ("chr1", 100, 200, "chr1", 1000, 1100),
            ("chr1", 1000, 1100, "chr1", 5000, 5100),
            ("chr1", 8000, 8100, "chr1", 9000, 9100),  # separate component
        ]
        self.g = LoopGraph(self.loops)

    def test_degree_enhancer(self):
        # enhancer 100-200 overlaps A → one edge to B
        self.assertEqual(self.g.degree_of_region("chr1", 100, 200), 1)

    def test_degree_promoter(self):
        self.assertEqual(self.g.degree_of_region("chr1", 5000, 5100), 1)

    def test_shared_community(self):
        size = self.g.shared_community_size("chr1", 100, 200, 5000, 5100)
        self.assertEqual(size, 3)  # A-B-C connected

    def test_no_shared_community(self):
        size = self.g.shared_community_size("chr1", 100, 200, 8000, 8100)
        self.assertEqual(size, 0)

    def test_min_loop_span_rank_direct(self):
        # Direct loop between enh and mid-range partner: add a spanning loop
        loops = [
            ("chr1", 100, 200, "chr1", 5000, 5100),  # direct E-P, span ~4900
            ("chr1", 100, 200, "chr1", 10000, 10100),  # longer
        ]
        g = LoopGraph(loops)
        # spans sorted by length → direct E-P should be rank 1
        rank = g.min_loop_span_rank("chr1", 100, 200, 5000, 5100)
        self.assertEqual(rank, 1.0)

    def test_min_loop_span_rank_missing(self):
        rank = self.g.min_loop_span_rank("chr1", 100, 200, 8000, 8100)
        self.assertEqual(rank, float(len(self.g.spans_by_chrom["chr1"]) + 1))


class TestVerdict(unittest.TestCase):
    def test_fail(self):
        self.assertEqual(verdict_from_delta(0.01), "FAIL_KILL")

    def test_inconclusive(self):
        self.assertEqual(verdict_from_delta(0.03), "INCONCLUSIVE")

    def test_pass(self):
        self.assertEqual(verdict_from_delta(0.05), "PASS_KILL")

    def test_nan(self):
        self.assertEqual(verdict_from_delta(float("nan")), "BLOCKED_PIPELINE")


if __name__ == "__main__":
    unittest.main()
