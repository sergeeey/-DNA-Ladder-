"""Unit tests for hic_contact_lib.py — critical-path coverage >= 60%.

Tests cover:
  - load_triples: normal, empty, malformed lines
  - bin_of: basic, boundary
  - analyze_contact: symmetric lookup, PASS scenario, INSUFFICIENT_BG scenario,
    missing primary, focal-row counting
  - score_resolution: PASS, INSUFFICIENT_BG, FAIL
  - sample_verdict: PASS+PASS, one INSUFFICIENT_BG, FAIL+FAIL, PARTIAL, INCONCLUSIVE
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# Allow importing from the scripts directory
_SCRIPTS = Path(__file__).resolve().parents[1] / "pilot_scaffold" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from hic_contact_lib import (  # noqa: E402
    analyze_contact,
    bin_of,
    load_triples,
    sample_verdict,
    score_resolution,
)
from freeze_stage3_architecture_anchors import (  # noqa: E402
    find_ctcf_anchor,
    pick_tss,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_triples(tmp: Path, rows: list[tuple[int, int, float]]) -> Path:
    """Write a juicer-style triple file and return its path."""
    text = "\n".join(f"{a}\t{b}\t{v}" for a, b, v in rows)
    tmp.write_text(text, encoding="utf-8")
    return tmp


# ---------------------------------------------------------------------------
# load_triples
# ---------------------------------------------------------------------------


class TestLoadTriples(unittest.TestCase):
    def test_normal_tab_separated(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("100\t200\t3.14\n110\t300\t1.0\n")
            p = Path(f.name)
        rows = load_triples(p)
        self.assertEqual(rows, [(100, 200, 3.14), (110, 300, 1.0)])

    def test_skips_malformed_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("not_a_number\t200\t3.14\n100\t200\t1.5\n")
            p = Path(f.name)
        rows = load_triples(p)
        self.assertEqual(rows, [(100, 200, 1.5)])

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            p = Path(f.name)
        rows = load_triples(p)
        self.assertEqual(rows, [])

    def test_missing_file(self):
        rows = load_triples(Path("/does/not/exist/fake.txt"))
        self.assertEqual(rows, [])

    def test_skips_wrong_column_count(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("100\t200\n100\t200\t1.0\n")
            p = Path(f.name)
        rows = load_triples(p)
        self.assertEqual(rows, [(100, 200, 1.0)])


# ---------------------------------------------------------------------------
# bin_of
# ---------------------------------------------------------------------------


class TestBinOf(unittest.TestCase):
    def test_exact_bin_boundary(self):
        self.assertEqual(bin_of(10_000, 10_000), 10_000)

    def test_interior(self):
        self.assertEqual(bin_of(15_500, 10_000), 10_000)

    def test_zero(self):
        self.assertEqual(bin_of(0, 10_000), 0)

    def test_25kb(self):
        self.assertEqual(bin_of(62_162_472, 25_000), 62_150_000)


# ---------------------------------------------------------------------------
# analyze_contact
# ---------------------------------------------------------------------------


def _make_obs_oe_files(
    obs_rows: list[tuple[int, int, float]],
    oe_rows: list[tuple[int, int, float]],
) -> tuple[Path, Path]:
    with tempfile.NamedTemporaryFile(suffix="_obs.txt", delete=False) as handle:
        obs_file = Path(handle.name)
    with tempfile.NamedTemporaryFile(suffix="_oe.txt", delete=False) as handle:
        oe_file = Path(handle.name)
    obs_file.write_text("\n".join(f"{a}\t{b}\t{v}" for a, b, v in obs_rows), encoding="utf-8")
    oe_file.write_text("\n".join(f"{a}\t{b}\t{v}" for a, b, v in oe_rows), encoding="utf-8")
    return obs_file, oe_file


class TestAnchorFreezeHelpers(unittest.TestCase):
    def test_find_ctcf_anchor_uses_bed_half_open_semantics(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bed", delete=False) as handle:
            handle.write("chr11\t100\t200\tpeak-low\t1\n")
            handle.write("chr11\t100\t200\tpeak-high\t5\n")
            bed = Path(handle.name)

        hit = find_ctcf_anchor(bed, "chr11", 101)

        self.assertIsNotNone(hit)
        self.assertEqual(hit["id"], "peak-high")
        self.assertIsNone(find_ctcf_anchor(bed, "chr11", 100))
        self.assertIsNotNone(find_ctcf_anchor(bed, "chr11", 200))

    def test_pick_tss_is_strand_aware_and_deterministic(self):
        genes = [
            {
                "id": "ENSG_B",
                "biotype": "protein_coding",
                "strand": 1,
                "start": 900,
                "end": 1200,
            },
            {
                "id": "ENSG_A",
                "biotype": "protein_coding",
                "strand": -1,
                "start": 800,
                "end": 1100,
            },
        ]

        selected = pick_tss(genes, 1000)

        self.assertEqual(selected["id"], "ENSG_A")
        self.assertEqual(selected["_tss_1based"], 1100)


class TestAnalyzeContact(unittest.TestCase):
    """Tests for analyze_contact."""

    # E anchor: 62_150_000–62_170_000 (mid bin 62_160_000 at 10kb)
    # P anchor: 62_450_000–62_470_000 (mid bin 62_460_000 at 10kb)
    # primary pair: (62_160_000, 62_460_000), distance = 300_000

    E = (62_150_000, 62_170_000)
    P = (62_450_000, 62_470_000)
    BINSIZE = 10_000
    FOCAL = 62_160_000  # exactly the E mid bin

    def _bg_rows(self, n: int = 25, dist: int = 300_000, base_val: float = 1.0) -> list[tuple[int, int, float]]:
        """Generate n background rows at the same distance as the primary pair.

        Starts at 63 Mb to avoid accidentally generating the primary pair
        (62_160_000, 62_460_000) which sits in the E/P bin exclusion window.
        """
        rows = []
        for i in range(n):
            a = 63_000_000 + i * 10_000  # outside E/P bin range
            b = a + dist
            rows.append((a, b, base_val))
        return rows

    def test_symmetric_obs_lookup(self):
        """Primary pair must be found regardless of which triangle juicer emitted."""
        # Emit (high, low) order to test symmetry
        primary_reversed = (62_460_000, 62_160_000)
        bg = self._bg_rows(25)
        obs_rows = [primary_reversed + (5.0,)] + bg
        oe_rows = [(62_460_000, 62_160_000, 2.5)]
        obs_f, oe_f = _make_obs_oe_files(obs_rows, oe_rows)

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL)
        self.assertIsNotNone(m["primary_obs"], "Symmetric lookup failed: primary_obs is None")
        self.assertAlmostEqual(m["primary_obs"], 5.0)

    def test_pass_scenario(self):
        """With strong signal and adequate background, metrics should support PASS."""
        primary = (62_160_000, 62_460_000)
        bg = self._bg_rows(30, base_val=1.0)
        # Add focal-row pixels so nonzero > 0
        focal_pixels = [(62_160_000, 62_170_000, 2.0), (62_160_000, 62_180_000, 1.5)]
        obs_rows = [primary + (5.0,)] + bg + focal_pixels
        oe_rows = [primary + (2.5,)]
        obs_f, oe_f = _make_obs_oe_files(obs_rows, oe_rows)

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL)
        self.assertEqual(m["same_distance_bg_n"], 30)
        self.assertIsNotNone(m["enrich_mean"])
        self.assertGreater(m["enrich_mean"], 1.5)
        self.assertIsNotNone(m["primary_oe"])
        self.assertGreater(m["primary_oe"], 1.2)

    def test_insufficient_bg(self):
        """With fewer than 20 background bins, bg_n should be < 20."""
        primary = (62_160_000, 62_460_000)
        bg = self._bg_rows(5)  # only 5 — below threshold
        obs_rows = [primary + (5.0,)] + bg
        oe_rows = [primary + (2.5,)]
        obs_f, oe_f = _make_obs_oe_files(obs_rows, oe_rows)

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL)
        self.assertLess(m["same_distance_bg_n"], 20)
        self.assertEqual(score_resolution(m), "INSUFFICIENT_BG")

    def test_missing_primary_returns_none(self):
        """If primary bin pair is absent from obs, primary_obs should be None."""
        bg = self._bg_rows(25)
        # No primary pixel
        obs_f, oe_f = _make_obs_oe_files(bg, [])

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL)
        self.assertIsNone(m["primary_obs"])

    def test_focal_row_nonzero_counted(self):
        """Focal-row nonzero count should reflect pixels in the E anchor bin row."""
        primary = (62_160_000, 62_460_000)
        focal_pixels = [
            (62_160_000, 62_170_000, 3.0),
            (62_160_000, 62_180_000, 0.0),  # zero — should NOT count
            (62_160_000, 62_190_000, 1.0),
        ]
        bg = self._bg_rows(25)
        obs_rows = [primary + (5.0,)] + focal_pixels + bg
        oe_rows = [primary + (2.5,)]
        obs_f, oe_f = _make_obs_oe_files(obs_rows, oe_rows)

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL)
        # Should count 2 nonzero (the 0.0 one doesn't count, plus the primary pair itself)
        self.assertGreaterEqual(m["focal_row_nonzero"], 2)

    def test_symmetric_exclusion_when_e_downstream_of_p(self):
        """Primary pair must be excluded from background even when E > P (A754 case).

        Uses 65Mb base to avoid generating the primary pair (63_460_000, 63_160_000)
        in the background set.
        """
        E_rev = (63_450_000, 63_470_000)  # higher (E downstream of P)
        P_rev = (63_150_000, 63_170_000)  # lower
        # primary pair: e_mid=63_460_000, p_mid=63_160_000, dist=300_000
        primary = (63_460_000, 63_160_000)
        # WHY: bg starts at 65Mb so no bg row produces the primary pair coords
        bg: list[tuple[int, int, float]] = [
            (65_000_000 + i * 10_000, 65_000_000 + i * 10_000 + 300_000, 1.0)
            for i in range(25)
        ]
        obs_rows = [primary + (8.0,)] + bg
        oe_rows = [primary + (3.0,)]
        obs_f, oe_f = _make_obs_oe_files(obs_rows, oe_rows)

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, E_rev, P_rev, 63_460_000)
        # Primary should be found at 8.0, NOT averaged into background
        self.assertIsNotNone(m["primary_obs"])
        self.assertAlmostEqual(m["primary_obs"], 8.0)
        # bg_n should be 25 (the primary pair excluded from bg)
        self.assertEqual(m["same_distance_bg_n"], 25)

    def test_empty_obs_file_returns_none_primary(self):
        """Empty dump file should yield primary_obs=None and bg_n=0."""
        with tempfile.NamedTemporaryFile(suffix="_obs.txt", delete=False) as handle:
            obs_f = Path(handle.name)
        with tempfile.NamedTemporaryFile(suffix="_oe.txt", delete=False) as handle:
            oe_f = Path(handle.name)
        obs_f.write_text("", encoding="utf-8")
        oe_f.write_text("", encoding="utf-8")

        m = analyze_contact(obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL)
        self.assertIsNone(m["primary_obs"])
        self.assertEqual(m["same_distance_bg_n"], 0)

    def test_same_bin_end_to_end_is_unresolved(self):
        """A518-like anchors in one 25 kb bin must never be scored as FAIL."""
        e_anchor = (518_574, 519_098)
        p_anchor = (504_895, 509_895)
        primary = (500_000, 500_000)
        background = [
            (1_000_000 + i * 25_000, 1_000_000 + i * 25_000, 100.0)
            for i in range(25)
        ]
        obs_f, oe_f = _make_obs_oe_files(
            [primary + (325.0,), *background],
            [primary + (1.8,)],
        )

        metrics = analyze_contact(
            obs_f,
            oe_f,
            25_000,
            e_anchor,
            p_anchor,
            518_836,
        )

        self.assertEqual(metrics["primary_pair"], [500_000, 500_000])
        self.assertEqual(score_resolution(metrics), "UNRESOLVED_SAME_BIN")


# ---------------------------------------------------------------------------
# score_resolution
# ---------------------------------------------------------------------------


class TestScoreResolution(unittest.TestCase):
    def _pass_metrics(self) -> dict:
        return {
            "primary_obs": 5.0,
            "primary_oe": 2.5,
            "same_distance_bg_n": 30,
            "enrich_mean": 3.0,
            "obs_percentile": 0.9,
            "focal_row_nonzero": 5,
        }

    def test_pass(self):
        self.assertEqual(score_resolution(self._pass_metrics()), "PASS")

    def test_insufficient_bg(self):
        m = self._pass_metrics()
        m["same_distance_bg_n"] = 19  # below threshold
        self.assertEqual(score_resolution(m), "INSUFFICIENT_BG")

    def test_fail_no_primary_obs(self):
        m = self._pass_metrics()
        m["primary_obs"] = None
        self.assertEqual(score_resolution(m), "FAIL")

    def test_fail_low_enrich(self):
        m = self._pass_metrics()
        m["enrich_mean"] = 1.2  # below 1.5
        self.assertEqual(score_resolution(m), "FAIL")

    def test_fail_low_percentile(self):
        m = self._pass_metrics()
        m["obs_percentile"] = 0.5  # below 0.75
        self.assertEqual(score_resolution(m), "FAIL")

    def test_fail_low_oe(self):
        m = self._pass_metrics()
        m["primary_oe"] = 1.0  # below 1.2
        self.assertEqual(score_resolution(m), "FAIL")

    def test_fail_zero_focal_row(self):
        m = self._pass_metrics()
        m["focal_row_nonzero"] = 0
        self.assertEqual(score_resolution(m), "FAIL")

    def test_same_bin_is_unresolved(self):
        m = self._pass_metrics()
        m["primary_pair"] = [500_000, 500_000]
        self.assertEqual(score_resolution(m), "UNRESOLVED_SAME_BIN")


# ---------------------------------------------------------------------------
# sample_verdict
# ---------------------------------------------------------------------------


class TestSampleVerdict(unittest.TestCase):
    def test_both_pass(self):
        self.assertEqual(sample_verdict("PASS", "PASS"), "PASS")

    def test_one_insufficient_bg(self):
        self.assertEqual(sample_verdict("PASS", "INSUFFICIENT_BG"), "INCONCLUSIVE")

    def test_both_insufficient_bg(self):
        self.assertEqual(sample_verdict("INSUFFICIENT_BG", "INSUFFICIENT_BG"), "INCONCLUSIVE")

    def test_both_fail(self):
        self.assertEqual(sample_verdict("FAIL", "FAIL"), "UNSUPPORTED")

    def test_partial_pass_fail(self):
        self.assertEqual(sample_verdict("PASS", "FAIL"), "PARTIAL")

    def test_partial_fail_pass(self):
        self.assertEqual(sample_verdict("FAIL", "PASS"), "PARTIAL")

    def test_inconclusive_both_fail_not_bg(self):
        # Already covered by test_both_fail; verify "else" branch doesn't fire
        self.assertEqual(sample_verdict("FAIL", "FAIL"), "UNSUPPORTED")

    def test_inconclusive_neither_pass_nor_bg_nor_fail(self):
        # If some unexpected score comes through, should fall through to INCONCLUSIVE
        self.assertEqual(sample_verdict("UNKNOWN_SCORE", "ANOTHER"), "INCONCLUSIVE")

    def test_insufficient_bg_overrides_fail(self):
        # Even if one is FAIL and other is INSUFFICIENT_BG, inconclusive
        self.assertEqual(sample_verdict("FAIL", "INSUFFICIENT_BG"), "INCONCLUSIVE")

    def test_same_bin_overrides_fail(self):
        self.assertEqual(
            sample_verdict("FAIL", "UNRESOLVED_SAME_BIN"),
            "INCONCLUSIVE",
        )


if __name__ == "__main__":
    unittest.main()
