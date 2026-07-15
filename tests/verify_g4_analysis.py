#!/usr/bin/env python3
"""Integration test for load_and_liftover_g4 in scripts/g4_se_vs_typical_analysis.py --
the one new piece of glue code in that script (lift_interval, merge_intervals, and
overlap_fraction are all separately tested elsewhere already). Verifies the
liftover-then-merge pipeline correctly counts failures and merges output,
since a bug here would silently corrupt the G4 peak set the REJECT verdict
depends on.
"""

import gzip
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from g4_se_vs_typical_analysis import load_and_liftover_g4  # noqa: E402
from liftover import Chain  # noqa: E402


def make_identity_chain(chrom, size):
    """A trivial chain that maps chrom 1:1 onto itself (offset 0, same strand)."""
    return {chrom: [Chain(0, size, 0, "+", size, [(0, size, 0)])]}


class TestLoadAndLiftoverG4(unittest.TestCase):
    def _write_bed_gz(self, rows):
        f = tempfile.NamedTemporaryFile(suffix=".bed.gz", delete=False)
        with gzip.open(f.name, "wt") as gz:
            for chrom, start, end in rows:
                gz.write(f"{chrom}\t{start}\t{end}\n")
        return Path(f.name)

    def test_all_peaks_lift_successfully_with_identity_chain(self):
        path = self._write_bed_gz([("chr1", 100, 200), ("chr1", 300, 400)])
        chains = make_identity_chain("chr1", 10_000)
        merged, n_total, n_failed = load_and_liftover_g4(path, chains)
        self.assertEqual(n_total, 2)
        self.assertEqual(n_failed, 0)
        self.assertEqual(merged["chr1"], [(100, 200), (300, 400)])

    def test_peaks_outside_chain_coverage_count_as_failed(self):
        path = self._write_bed_gz([("chr1", 100, 200), ("chr2", 100, 200)])
        # chain only covers chr1 -- chr2 peak has no chain to lift through
        chains = make_identity_chain("chr1", 10_000)
        merged, n_total, n_failed = load_and_liftover_g4(path, chains)
        self.assertEqual(n_total, 2)
        self.assertEqual(n_failed, 1)
        self.assertNotIn("chr2", merged)

    def test_overlapping_lifted_peaks_get_merged(self):
        path = self._write_bed_gz([("chr1", 100, 300), ("chr1", 250, 400)])
        chains = make_identity_chain("chr1", 10_000)
        merged, n_total, n_failed = load_and_liftover_g4(path, chains)
        self.assertEqual(n_failed, 0)
        # the two overlapping input peaks must merge into one [100,400) interval,
        # not stay as two separate overlapping entries
        self.assertEqual(merged["chr1"], [(100, 400)])

    def test_plain_uncompressed_bed_also_works(self):
        f = tempfile.NamedTemporaryFile(suffix=".bed", mode="w", delete=False)
        f.write("chr1\t500\t600\n")
        f.close()
        chains = make_identity_chain("chr1", 10_000)
        merged, n_total, n_failed = load_and_liftover_g4(Path(f.name), chains)
        self.assertEqual(n_total, 1)
        self.assertEqual(n_failed, 0)
        self.assertEqual(merged["chr1"], [(500, 600)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
