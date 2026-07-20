#!/usr/bin/env python3
"""Unit tests for T4 mappability filter helpers (no network / no bigWig required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from t4_mappability_sensitivity import filter_by_umap, or_block  # noqa: E402
from t5_replication_celltype import replication_verdict  # noqa: E402


class TestUmapFilter(unittest.TestCase):
    def test_filter_threshold(self):
        anchors = [("chr1", 0, 1000), ("chr1", 1000, 2000), ("chr1", 2000, 3000)]
        hits = [True, False, True]
        umap = [0.2, 0.4, 0.9]
        a, h, u = filter_by_umap(anchors, hits, umap, 0.3)
        self.assertEqual(len(a), 2)
        self.assertEqual(h, [False, True])
        self.assertEqual(u, [0.4, 0.9])

    def test_or_block_fail_flag(self):
        # enrichment table → OR high
        row = or_block([True] * 80 + [False] * 20, [True] * 20 + [False] * 80, "t", 0.3)
        self.assertFalse(row["below_fail_threshold_1_1"])
        # depletion-ish
        row2 = or_block([True] * 20 + [False] * 80, [True] * 40 + [False] * 60, "t", 0.3)
        self.assertTrue(row2["below_fail_threshold_1_1"])


class TestReplicationVerdict(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(replication_verdict(1.4)["verdict"], "SUPPORT_REPLICATION")
        self.assertEqual(
            replication_verdict(0.95)["verdict"], "NULL_OR_OPPOSITE_REPLICATION"
        )
        self.assertEqual(
            replication_verdict(1.2)["verdict"], "INCONCLUSIVE_REPLICATION"
        )


if __name__ == "__main__":
    unittest.main()
