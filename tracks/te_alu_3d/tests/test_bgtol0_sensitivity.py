"""Tests for the bg_tol_bins=0 sensitivity side-car.

Coverage:
  - classify_score_transition: all five transition labels
  - SameBinGuardError: raised when E_mid == P_mid at bg_tol_bins=0
  - check_same_bin_guard: correct detection, non-same-bin passes silently
  - verify_manifest_hash: correct hash passes, wrong hash raises
  - verify_dump_hashes: all-match passes, single mismatch raises
  - verify_baseline_hash: correct pin passes, changed file raises
  - holdout guard: path containing 'holdout' raises
  - bg_tol_bins=0 vs bg_tol_bins=1: bg_n differs on synthetic data with ±tol pixels
  - analyze_contact bg_tol_bins=0: exact-distance background only
  - Integration smoke test (skipped if dump files absent)
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "pilot_scaffold" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from hic_contact_lib import analyze_contact, bin_of  # noqa: E402
from run_stage3_architecture_wt_contact_bgtol0 import (  # noqa: E402
    SameBinGuardError,
    _reject_holdout_path,
    _sha256_file,
    assert_output_paths_safe,
    check_same_bin_guard,
    classify_score_transition,
    verify_manifest_freeze_pin,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_triples(path: Path, rows: list[tuple[int, int, float]]) -> Path:
    path.write_text("\n".join(f"{a}\t{b}\t{v}" for a, b, v in rows), encoding="utf-8")
    return path


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_str(s: str) -> str:
    return _sha256(s.encode("utf-8"))


# ---------------------------------------------------------------------------
# classify_score_transition
# ---------------------------------------------------------------------------


class TestClassifyScoreTransition(unittest.TestCase):
    def test_stable_fail(self):
        self.assertEqual(classify_score_transition("FAIL", "FAIL"), "STABLE")

    def test_stable_pass(self):
        self.assertEqual(classify_score_transition("PASS", "PASS"), "STABLE")

    def test_stable_insufficient_bg(self):
        self.assertEqual(
            classify_score_transition("INSUFFICIENT_BG", "INSUFFICIENT_BG"), "STABLE"
        )

    def test_upgraded_fail_to_pass(self):
        self.assertEqual(classify_score_transition("FAIL", "PASS"), "UPGRADED")

    def test_upgraded_insufficient_bg_to_pass(self):
        self.assertEqual(
            classify_score_transition("INSUFFICIENT_BG", "PASS"), "UPGRADED"
        )

    def test_downgraded_pass_to_fail(self):
        self.assertEqual(classify_score_transition("PASS", "FAIL"), "DOWNGRADED")

    def test_downgraded_pass_to_insufficient_bg(self):
        self.assertEqual(
            classify_score_transition("PASS", "INSUFFICIENT_BG"), "DOWNGRADED"
        )

    def test_changed_insufficient_bg_to_fail(self):
        # Neither upgrade nor downgrade — just a change between non-pass states
        self.assertEqual(
            classify_score_transition("INSUFFICIENT_BG", "FAIL"), "CHANGED"
        )

    def test_changed_fail_to_insufficient_bg(self):
        self.assertEqual(
            classify_score_transition("FAIL", "INSUFFICIENT_BG"), "CHANGED"
        )

    def test_same_bin_blocked_hard_fail(self):
        self.assertEqual(
            classify_score_transition(
                "UNRESOLVED_SAME_BIN", "SAME_BIN_GUARD_VIOLATION"
            ),
            "SAME_BIN_BLOCKED_HARD_FAIL",
        )

    def test_same_bin_guard_always_hard_fail_regardless_of_old(self):
        for old in ("PASS", "FAIL", "INSUFFICIENT_BG", "UNRESOLVED_SAME_BIN"):
            with self.subTest(old=old):
                self.assertEqual(
                    classify_score_transition(old, "SAME_BIN_GUARD_VIOLATION"),
                    "SAME_BIN_BLOCKED_HARD_FAIL",
                )


# ---------------------------------------------------------------------------
# check_same_bin_guard / SameBinGuardError
# ---------------------------------------------------------------------------


class TestCheckSameBinGuard(unittest.TestCase):
    def test_raises_when_same_bin_10kb(self):
        """Anchors resolving to the same 10 kb bin must raise SameBinGuardError."""
        # Both mid-points land in bin 500_000 at 10 kb
        e = (500_000, 505_000)
        p = (500_000, 508_000)
        with self.assertRaises(SameBinGuardError):
            check_same_bin_guard(e, p, binsize=10_000)

    def test_raises_when_same_bin_25kb(self):
        """Mirrors the A518 case: both anchors in bin 500_000 at 25 kb."""
        e = (518_575, 519_098)
        p = (504_895, 509_895)
        # bin_of(518836, 25000) == bin_of(507395, 25000) == 500000
        self.assertEqual(bin_of(518_836, 25_000), 500_000)
        self.assertEqual(bin_of(507_395, 25_000), 500_000)
        with self.assertRaises(SameBinGuardError):
            check_same_bin_guard(e, p, binsize=25_000)

    def test_no_raise_when_different_bins(self):
        """Anchors in different bins must NOT raise."""
        e = (518_575, 519_098)
        p = (504_895, 509_895)
        # At 10 kb: bin_of(518836,10000)=510000, bin_of(507395,10000)=500000 — different
        check_same_bin_guard(e, p, binsize=10_000)

    def test_no_raise_for_a754_at_10kb(self):
        """A754 at 10 kb: E_mid and P_mid are in different bins."""
        e = (75_156_315, 75_156_841)
        p = (75_141_748, 75_146_748)
        check_same_bin_guard(e, p, binsize=10_000)

    def test_no_raise_for_a754_at_25kb(self):
        """A754 at 25 kb: E_mid (75150000) and P_mid (75125000) are different."""
        e = (75_156_315, 75_156_841)
        p = (75_141_748, 75_146_748)
        check_same_bin_guard(e, p, binsize=25_000)

    def test_no_raise_for_a518_at_10kb(self):
        """A518 at 10 kb: E_mid (510000) and P_mid (500000) are different."""
        e = (518_575, 519_098)
        p = (504_895, 509_895)
        check_same_bin_guard(e, p, binsize=10_000)

    def test_same_bin_guard_error_message_contains_bin(self):
        e = (500_000, 505_000)
        p = (500_000, 508_000)
        with self.assertRaises(SameBinGuardError) as cm:
            check_same_bin_guard(e, p, binsize=10_000)
        self.assertIn("500000", str(cm.exception))


# ---------------------------------------------------------------------------
# Holdout guard
# ---------------------------------------------------------------------------


class TestHoldoutGuard(unittest.TestCase):
    def test_holdout_path_raises(self):
        p = Path("/some/project/data/holdout/secret.txt")
        with self.assertRaises(RuntimeError) as cm:
            _reject_holdout_path(p)
        self.assertIn("FORBIDDEN", str(cm.exception))

    def test_normal_path_passes(self):
        p = Path("/some/project/data/prospective/results.json")
        _reject_holdout_path(p)

    def test_holdout_in_middle_of_path_raises(self):
        p = Path("/data/holdout_samples/hic.txt")
        with self.assertRaises(RuntimeError):
            _reject_holdout_path(p)


# ---------------------------------------------------------------------------
# verify_manifest_hash
# ---------------------------------------------------------------------------


class TestVerifyManifestHash(unittest.TestCase):
    def _make_manifest(self, tmp: Path, content: str) -> tuple[Path, Path]:
        mj = tmp / "manifest.json"
        mh = tmp / "manifest.json.sha256"
        mj.write_text(content, encoding="utf-8")
        digest = _sha256(mj.read_bytes())
        mh.write_text(digest + "\n", encoding="utf-8")
        return mj, mh

    def test_correct_hash_passes(self):
        """verify_manifest_hash should not raise when hash matches."""
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        payload = {"manifest_version": "test", "dump_sha256": {}}
        content = json.dumps(payload, indent=2)
        mj, mh = self._make_manifest(tmp, content)

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with (
            mock.patch.object(mod, "MANIFEST_JSON", mj),
            mock.patch.object(mod, "MANIFEST_HASH", mh),
        ):
            result = mod.verify_manifest_hash()
        self.assertEqual(result["manifest_version"], "test")

    def test_wrong_hash_raises(self):
        """verify_manifest_hash must raise when the stored hash does not match the file."""
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        mj = tmp / "manifest.json"
        mh = tmp / "manifest.json.sha256"
        mj.write_text('{"manifest_version": "test"}', encoding="utf-8")
        mh.write_text("0" * 64 + "\n", encoding="utf-8")  # wrong hash

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with (
            mock.patch.object(mod, "MANIFEST_JSON", mj),
            mock.patch.object(mod, "MANIFEST_HASH", mh),
        ):
            with self.assertRaises(RuntimeError) as cm:
                mod.verify_manifest_hash()
        self.assertIn("mismatch", str(cm.exception).lower())

    def test_missing_manifest_raises_file_not_found(self):
        """verify_manifest_hash must raise FileNotFoundError when manifest absent."""
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        missing = tmp / "nonexistent.json"
        missing_hash = tmp / "nonexistent.json.sha256"

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with (
            mock.patch.object(mod, "MANIFEST_JSON", missing),
            mock.patch.object(mod, "MANIFEST_HASH", missing_hash),
        ):
            with self.assertRaises(FileNotFoundError):
                mod.verify_manifest_hash()


# ---------------------------------------------------------------------------
# verify_dump_hashes
# ---------------------------------------------------------------------------


class TestVerifyDumpHashes(unittest.TestCase):
    def _setup(self, tmp: Path) -> tuple[dict, Path]:
        """Create 2 synthetic dump files and a manifest referencing them."""
        dump_dir = tmp / "dumps"
        dump_dir.mkdir()
        names = ["ARCH_01_A754_obs_KR_10kb.txt", "ARCH_01_A754_oe_KR_10kb.txt"]
        dump_sha256: dict[str, str] = {}
        for name in names:
            p = dump_dir / name
            p.write_text("100\t200\t1.0\n", encoding="utf-8")
            dump_sha256[name] = _sha256_file(p)
        manifest = {"dump_sha256": dump_sha256}
        return manifest, dump_dir

    def test_all_hashes_match_passes(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        manifest, dump_dir = self._setup(tmp)

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "DUMP_DIR", dump_dir):
            mod.verify_dump_hashes(manifest)  # must not raise

    def test_single_hash_mismatch_raises(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        manifest, dump_dir = self._setup(tmp)

        # Tamper with one dump file
        first_name = next(iter(manifest["dump_sha256"]))
        (dump_dir / first_name).write_text("tampered\n", encoding="utf-8")

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "DUMP_DIR", dump_dir):
            with self.assertRaises(RuntimeError) as cm:
                mod.verify_dump_hashes(manifest)
        self.assertIn("mismatch", str(cm.exception).lower())

    def test_missing_dump_raises_file_not_found(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        empty_dir = tmp / "empty"
        empty_dir.mkdir()
        manifest = {"dump_sha256": {"ARCH_01_A754_obs_KR_10kb.txt": "a" * 64}}

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "DUMP_DIR", empty_dir):
            with self.assertRaises(FileNotFoundError):
                mod.verify_dump_hashes(manifest)


# ---------------------------------------------------------------------------
# bg_tol_bins=0 vs bg_tol_bins=1: exact-distance isolation
# ---------------------------------------------------------------------------


class TestBgTolBinsZero(unittest.TestCase):
    """Confirm that bg_tol_bins=0 excludes the ±1-bin pixels that tol=1 includes."""

    # Anchors 3 bins apart to avoid same-bin guard.
    # e_mid = bin_of((60_000_000 + 60_020_000)//2, 10kb) = bin_of(60_010_000, 10kb) = 60_010_000
    # p_mid = bin_of((60_450_000 + 60_470_000)//2, 10kb) = bin_of(60_460_000, 10kb) = 60_460_000
    # target_dist = |60_460_000 - 60_010_000| = 450_000
    E = (60_000_000, 60_020_000)
    P = (60_450_000, 60_470_000)

    BINSIZE = 10_000
    FOCAL = 60_010_000

    def _make_files(self, tmp: Path, n: int = 30) -> tuple[Path, Path]:
        obs_f = tmp / "obs.txt"
        oe_f = tmp / "oe.txt"
        # Primary: must match (e_mid, p_mid) = (60_010_000, 60_460_000), dist=450_000
        primary = (60_010_000, 60_460_000)
        rows_obs = [primary + (10.0,)]
        # Exact-distance background: n rows at dist=450_000 (= target_dist).
        # These ARE included at bg_tol_bins=0.
        for i in range(n):
            a = 61_000_000 + i * 10_000
            rows_obs.append((a, a + 450_000, 1.0))
        # Adjacent pixels at dist=440_000 and dist=460_000 (±1 bin from target):
        # INCLUDED at bg_tol_bins=1 but EXCLUDED at bg_tol_bins=0.
        for i in range(10):
            a = 62_000_000 + i * 10_000
            rows_obs.append((a, a + 440_000, 99.0))  # ±1-bin low
        for i in range(10):
            a = 63_000_000 + i * 10_000
            rows_obs.append((a, a + 460_000, 99.0))  # ±1-bin high

        oe_rows = [primary + (2.0,)]
        obs_f.write_text(
            "\n".join(f"{a}\t{b}\t{v}" for a, b, v in rows_obs), encoding="utf-8"
        )
        oe_f.write_text(
            "\n".join(f"{a}\t{b}\t{v}" for a, b, v in oe_rows), encoding="utf-8"
        )
        return obs_f, oe_f

    def test_bgtol0_bg_n_equals_exact_distance_count(self):
        """With bg_tol_bins=0, bg_n should count only exactly-dist pixels."""
        tmp = Path(tempfile.mkdtemp())
        obs_f, oe_f = self._make_files(tmp, n=30)

        m = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=0
        )
        # Exactly n=30: the ±1-bin rows at 440k and 460k are excluded; only 450k rows count.
        self.assertEqual(m["same_distance_bg_n"], 30)

    def test_bgtol1_bg_n_larger_than_bgtol0(self):
        """With bg_tol_bins=1, the ±1-bin pixels inflate bg_n above the exact count."""
        tmp = Path(tempfile.mkdtemp())
        obs_f, oe_f = self._make_files(tmp, n=30)

        m0 = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=0
        )
        m1 = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=1
        )
        # bg_n at tol=1 must be larger because it picks up the ±1-bin rows
        self.assertGreater(m1["same_distance_bg_n"], m0["same_distance_bg_n"])

    def test_bgtol0_enrich_mean_differs_from_bgtol1_due_to_high_adjacent(self):
        """The ±1-bin rows contain 99.0 values; excluding them changes enrich_mean."""
        tmp = Path(tempfile.mkdtemp())
        obs_f, oe_f = self._make_files(tmp, n=30)

        m0 = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=0
        )
        m1 = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=1
        )
        # tol=1 background includes high-valued (99.0) adjacent pixels → higher bg_mean
        # → lower enrich_mean than tol=0 (which only sees the 1.0-valued exact rows)
        self.assertIsNotNone(m0["enrich_mean"])
        self.assertIsNotNone(m1["enrich_mean"])
        self.assertGreater(m0["enrich_mean"], m1["enrich_mean"])

    def test_bgtol0_primary_obs_unaffected(self):
        """bg_tol_bins does not affect the primary observation value."""
        tmp = Path(tempfile.mkdtemp())
        obs_f, oe_f = self._make_files(tmp, n=30)

        m0 = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=0
        )
        m1 = analyze_contact(
            obs_f, oe_f, self.BINSIZE, self.E, self.P, self.FOCAL, bg_tol_bins=1
        )
        self.assertAlmostEqual(m0["primary_obs"], m1["primary_obs"])


# ---------------------------------------------------------------------------
# verify_baseline_hash
# ---------------------------------------------------------------------------


class TestVerifyBaselineHash(unittest.TestCase):
    def test_correct_pin_passes(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        bj = tmp / "baseline.json"
        content = json.dumps({"panel_verdict": "INCONCLUSIVE"})
        bj.write_text(content, encoding="utf-8")
        digest = _sha256_file(bj)
        manifest = {
            "baseline_result_sha256": digest,
            "baseline_result_json": "baseline.json",
        }

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "BASELINE_JSON", bj):
            result = mod.verify_baseline_hash(manifest)
        self.assertEqual(result["panel_verdict"], "INCONCLUSIVE")

    def test_changed_file_raises(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        bj = tmp / "baseline.json"
        bj.write_text('{"panel_verdict": "INCONCLUSIVE"}', encoding="utf-8")
        manifest = {"baseline_result_sha256": "0" * 64}

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "BASELINE_JSON", bj):
            with self.assertRaises(RuntimeError) as cm:
                mod.verify_baseline_hash(manifest)
        self.assertIn("changed", str(cm.exception).lower())


class TestAdditionalIntegrityGuards(unittest.TestCase):
    def test_manifest_freeze_pin_mismatch_raises(self):
        with self.assertRaises(RuntimeError):
            verify_manifest_freeze_pin(
                {"freeze_sha256": "old"},
                "current",
            )

    def test_freeze_hash_mismatch_raises(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        freeze = tmp / "freeze.json"
        sidecar = tmp / "freeze.json.sha256"
        freeze.write_text('{"freeze_version":"test"}', encoding="utf-8")
        sidecar.write_text("0" * 64 + "\n", encoding="utf-8")
        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with (
            mock.patch.object(mod, "FREEZE_JSON", freeze),
            mock.patch.object(mod, "FREEZE_HASH", sidecar),
        ):
            with self.assertRaises(RuntimeError):
                mod.verify_freeze_hash()

    def test_claim_hash_mismatch_raises(self):
        import importlib
        import unittest.mock as mock

        tmp = Path(tempfile.mkdtemp())
        claim = tmp / "claim.md"
        claim.write_text("changed", encoding="utf-8")
        manifest = {
            "sensitivity_claim": claim.name,
            "sensitivity_claim_sha256": "0" * 64,
        }
        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "CLAIM_MD", claim):
            with self.assertRaises(RuntimeError):
                mod.verify_claim_hash(manifest)

    def test_output_guard_rejects_parent_result_path(self):
        import importlib
        import unittest.mock as mock

        mod = importlib.import_module("run_stage3_architecture_wt_contact_bgtol0")
        with mock.patch.object(mod, "OUT_JSON", mod.BASELINE_JSON):
            with self.assertRaises(RuntimeError):
                assert_output_paths_safe()


# ---------------------------------------------------------------------------
# Integration smoke test (uses real dump files if present)
# ---------------------------------------------------------------------------


class TestIntegrationSmoke(unittest.TestCase):
    """Smoke test against the real dump files — skipped if files absent."""

    PROSPECTIVE = Path(__file__).resolve().parents[1] / "09_outputs" / "prospective"
    DUMP_DIR = PROSPECTIVE / "g4a_stage3_architecture_wt_dumps"

    SLOTS = [
        {
            "slot_id": "ARCH_01",
            "candidate_id": "A754",
            "e_anchor": (75_156_315, 75_156_841),
            "p_anchor": (75_141_748, 75_146_748),
            "focal": (75_156_315 + 75_156_841) // 2,
        },
        {
            "slot_id": "ARCH_02",
            "candidate_id": "A518",
            "e_anchor": (518_575, 519_098),
            "p_anchor": (504_895, 509_895),
            "focal": (518_575 + 519_098) // 2,
        },
    ]

    def _dump_path(self, slot: dict, kind: str, binsize: int) -> Path:
        tag = f"{slot['slot_id']}_{slot['candidate_id']}"
        return self.DUMP_DIR / f"{tag}_{kind}_KR_{binsize // 1000}kb.txt"

    def test_a754_10kb_bgtol0_runs_and_has_adequate_bg(self):
        obs = self._dump_path(self.SLOTS[0], "obs", 10_000)
        oe = self._dump_path(self.SLOTS[0], "oe", 10_000)
        if not obs.exists() or not oe.exists():
            self.skipTest("Real dump files not present")
        slot = self.SLOTS[0]
        m = analyze_contact(
            obs,
            oe,
            10_000,
            slot["e_anchor"],
            slot["p_anchor"],
            slot["focal"],
            bg_tol_bins=0,
        )
        self.assertGreaterEqual(
            m["same_distance_bg_n"], 20, "bg_n too low at bg_tol_bins=0"
        )
        self.assertIsNotNone(m["primary_obs"])

    def test_a754_25kb_bgtol0_runs_without_same_bin_guard(self):
        obs = self._dump_path(self.SLOTS[0], "obs", 25_000)
        oe = self._dump_path(self.SLOTS[0], "oe", 25_000)
        if not obs.exists() or not oe.exists():
            self.skipTest("Real dump files not present")
        slot = self.SLOTS[0]
        # Must not raise SameBinGuardError (different bins at 25kb for A754)
        check_same_bin_guard(slot["e_anchor"], slot["p_anchor"], binsize=25_000)
        m = analyze_contact(
            obs,
            oe,
            25_000,
            slot["e_anchor"],
            slot["p_anchor"],
            slot["focal"],
            bg_tol_bins=0,
        )
        self.assertIsNotNone(m)

    def test_a518_10kb_bgtol0_runs(self):
        obs = self._dump_path(self.SLOTS[1], "obs", 10_000)
        oe = self._dump_path(self.SLOTS[1], "oe", 10_000)
        if not obs.exists() or not oe.exists():
            self.skipTest("Real dump files not present")
        slot = self.SLOTS[1]
        m = analyze_contact(
            obs,
            oe,
            10_000,
            slot["e_anchor"],
            slot["p_anchor"],
            slot["focal"],
            bg_tol_bins=0,
        )
        self.assertIsNotNone(m)

    def test_a518_25kb_raises_same_bin_guard(self):
        """A518 at 25 kb must always trigger the same-bin guard."""
        slot = self.SLOTS[1]
        with self.assertRaises(SameBinGuardError):
            check_same_bin_guard(slot["e_anchor"], slot["p_anchor"], binsize=25_000)

    def test_bgtol0_bg_n_less_than_or_equal_bgtol1_on_real_data(self):
        """bg_tol_bins=0 should produce bg_n ≤ bg_tol_bins=1 (exact subset)."""
        obs = self._dump_path(self.SLOTS[0], "obs", 10_000)
        oe = self._dump_path(self.SLOTS[0], "oe", 10_000)
        if not obs.exists() or not oe.exists():
            self.skipTest("Real dump files not present")
        slot = self.SLOTS[0]
        m0 = analyze_contact(
            obs,
            oe,
            10_000,
            slot["e_anchor"],
            slot["p_anchor"],
            slot["focal"],
            bg_tol_bins=0,
        )
        m1 = analyze_contact(
            obs,
            oe,
            10_000,
            slot["e_anchor"],
            slot["p_anchor"],
            slot["focal"],
            bg_tol_bins=1,
        )
        self.assertLessEqual(m0["same_distance_bg_n"], m1["same_distance_bg_n"])


if __name__ == "__main__":
    unittest.main()
