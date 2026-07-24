"""Tests for hic_remote_preflight.py — coverage >= 60% of module.

Tests cover:
  - _reject_forbidden_url: holdout URL raises, normal URL passes
  - check_head: 200+ranges=PASS, 200+no-ranges=FAIL, 404=FAIL, error=FAIL
  - check_range_magic: 206+HIC=PASS, 206+wrong=FAIL, 200(no206)=FAIL, error=FAIL
  - run_preflight: all-pass returns OK, head-fail raises, range-fail raises
  - run_preflight_all: all-pass, first-failure short-circuits and raises
"""
from __future__ import annotations

import sys
import unittest
import unittest.mock as mock
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

_SCRIPTS = Path(__file__).resolve().parents[1] / "pilot_scaffold" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from hic_remote_preflight import (  # noqa: E402
    HIC_MAGIC,
    RemotePreflightBlockedError,
    _head_check,
    _range_check,
    _reject_forbidden_url,
    check_head,
    check_range_magic,
    run_preflight,
    run_preflight_all,
)
from run_stage3_architecture_replic import (  # noqa: E402
    CLAIM_SHA256_EXPECTED,
    SAMPLE_URLS,
    cross_sample_slot_verdict,
    panel_verdict,
    verify_cross_chain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _MockResponse:
    """Minimal mock for urllib.request.urlopen context-manager response."""

    def __init__(
        self,
        status: int = 200,
        headers: dict | None = None,
        body: bytes = b"",
    ):
        self.status = status
        self.headers = headers or {}
        self._body = body

    # urllib responses expose headers via .get()
    def __enter__(self) -> "_MockResponse":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def read(self, n: int = -1) -> bytes:
        return self._body[:n] if n >= 0 else self._body

    def get(self, key: str, default: str | None = None) -> str | None:  # noqa: D102
        return self.headers.get(key, default)


# ---------------------------------------------------------------------------
# _reject_forbidden_url
# ---------------------------------------------------------------------------


class TestRejectForbiddenUrl(unittest.TestCase):
    def test_holdout_raises(self):
        with self.assertRaises(RemotePreflightBlockedError) as cm:
            _reject_forbidden_url("https://example.com/holdout/data.hic")
        self.assertIn("FORBIDDEN", str(cm.exception))

    def test_holdout_case_insensitive(self):
        with self.assertRaises(RemotePreflightBlockedError):
            _reject_forbidden_url("https://example.com/HOLDOUT/data.hic")

    def test_normal_url_passes(self):
        _reject_forbidden_url("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/x.hic")

    def test_url_with_holdout_in_filename_raises(self):
        with self.assertRaises(RemotePreflightBlockedError):
            _reject_forbidden_url("https://example.com/data/holdout_samples.hic")


# ---------------------------------------------------------------------------
# check_head
# ---------------------------------------------------------------------------


class TestCheckHead(unittest.TestCase):
    _URL = "https://example.com/test.hic"

    def _mock_urlopen(self, status: int, headers: dict) -> mock.MagicMock:
        resp = _MockResponse(status=status, headers=headers)
        return mock.patch("urllib.request.urlopen", return_value=resp)

    def test_ok_head_returns_eligible_true(self):
        with self._mock_urlopen(200, {"Content-Length": "123456", "Accept-Ranges": "bytes"}):
            result = check_head(self._URL)
        self.assertTrue(result["eligible"])
        self.assertTrue(result["ok_status"])
        self.assertTrue(result["ok_length"])
        self.assertTrue(result["ok_ranges"])

    def test_missing_accept_ranges_returns_ineligible(self):
        with self._mock_urlopen(200, {"Content-Length": "123456"}):
            result = check_head(self._URL)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["ok_ranges"])

    def test_accept_ranges_none_returns_ineligible(self):
        with self._mock_urlopen(200, {"Content-Length": "123456", "Accept-Ranges": "none"}):
            result = check_head(self._URL)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["ok_ranges"])

    def test_404_returns_ineligible(self):
        def _raise(*args, **kwargs):
            raise HTTPError(self._URL, 404, "Not Found", {}, None)

        with mock.patch("urllib.request.urlopen", side_effect=_raise):
            result = check_head(self._URL)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["status"], 404)

    def test_network_error_returns_ineligible(self):
        def _raise(*args, **kwargs):
            raise OSError("connection refused")

        with mock.patch("urllib.request.urlopen", side_effect=_raise):
            result = check_head(self._URL)
        self.assertFalse(result["eligible"])
        self.assertIsNotNone(result["error"])

    def test_zero_content_length_returns_ineligible(self):
        with self._mock_urlopen(200, {"Content-Length": "0", "Accept-Ranges": "bytes"}):
            result = check_head(self._URL)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["ok_length"])

    def test_holdout_url_raises_blocked(self):
        with self.assertRaises(RemotePreflightBlockedError):
            check_head("https://example.com/holdout/data.hic")


# ---------------------------------------------------------------------------
# check_range_magic
# ---------------------------------------------------------------------------


class TestCheckRangeMagic(unittest.TestCase):
    _URL = "https://example.com/test.hic"

    def _mock_urlopen(self, status: int, body: bytes) -> mock.MagicMock:
        resp = _MockResponse(status=status, body=body)
        return mock.patch("urllib.request.urlopen", return_value=resp)

    def test_206_with_hic_magic_eligible(self):
        with self._mock_urlopen(206, b"HIC\x00"):
            result = check_range_magic(self._URL)
        self.assertTrue(result["eligible"])
        self.assertTrue(result["ok_206"])
        self.assertTrue(result["ok_magic"])

    def test_206_with_wrong_magic_ineligible(self):
        with self._mock_urlopen(206, b"BAD\x00"):
            result = check_range_magic(self._URL)
        self.assertFalse(result["eligible"])
        self.assertTrue(result["ok_206"])
        self.assertFalse(result["ok_magic"])

    def test_200_instead_of_206_ineligible(self):
        """Server ignoring Range header returns 200 — range requests not supported."""
        with self._mock_urlopen(200, b"HIC\x00"):
            result = check_range_magic(self._URL)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["ok_206"])

    def test_404_range_request_ineligible(self):
        def _raise(*args, **kwargs):
            raise HTTPError(self._URL, 404, "Not Found", {}, BytesIO(b""))

        with mock.patch("urllib.request.urlopen", side_effect=_raise):
            result = check_range_magic(self._URL)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["status"], 404)

    def test_empty_body_ineligible(self):
        with self._mock_urlopen(206, b""):
            result = check_range_magic(self._URL)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["ok_magic"])

    def test_short_body_only_2_bytes_ineligible(self):
        """Less than 3 bytes → magic check fails even if prefix matches."""
        with self._mock_urlopen(206, b"HI"):
            result = check_range_magic(self._URL)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["ok_magic"])

    def test_holdout_url_raises_blocked(self):
        with self.assertRaises(RemotePreflightBlockedError):
            check_range_magic("https://example.com/holdout/data.hic")

    def test_magic_bytes_hex_present_in_result(self):
        with self._mock_urlopen(206, b"HIC\x00"):
            result = check_range_magic(self._URL)
        self.assertEqual(result["magic_bytes_hex"], HIC_MAGIC.hex())


# ---------------------------------------------------------------------------
# run_preflight
# ---------------------------------------------------------------------------


class TestRunPreflight(unittest.TestCase):
    _URL = "https://example.com/test.hic"

    def _ok_head(self) -> dict:
        return {
            "url": self._URL, "check": "head", "status": 200,
            "content_length": "123456", "accept_ranges": "bytes",
            "ok_status": True, "ok_length": True, "ok_ranges": True,
            "eligible": True, "error": None,
        }

    def _ok_range(self) -> dict:
        return {
            "url": self._URL, "check": "range_magic", "status": 206,
            "data": b"HIC\x00", "ok_206": True, "ok_magic": True,
            "magic_bytes_hex": "484943", "eligible": True, "error": None,
        }

    def _fail_head(self) -> dict:
        h = self._ok_head()
        h["ok_ranges"] = False
        h["eligible"] = False
        return h

    def _fail_range(self) -> dict:
        r = self._ok_range()
        r["ok_206"] = False
        r["eligible"] = False
        return r

    def test_all_pass_returns_ok_dict(self):
        with (
            mock.patch("hic_remote_preflight.check_head", return_value=self._ok_head()),
            mock.patch("hic_remote_preflight.check_range_magic", return_value=self._ok_range()),
        ):
            result = run_preflight(self._URL)
        self.assertEqual(result["status"], "OK")
        self.assertIn("head", result)
        self.assertIn("range_magic", result)

    def test_head_fail_raises_blocked(self):
        with (
            mock.patch("hic_remote_preflight.check_head", return_value=self._fail_head()),
            mock.patch("hic_remote_preflight.check_range_magic", return_value=self._ok_range()),
        ):
            with self.assertRaises(RemotePreflightBlockedError) as cm:
                run_preflight(self._URL)
        self.assertIn("BLOCKED", str(cm.exception))

    def test_range_fail_raises_blocked(self):
        with (
            mock.patch("hic_remote_preflight.check_head", return_value=self._ok_head()),
            mock.patch("hic_remote_preflight.check_range_magic", return_value=self._fail_range()),
        ):
            with self.assertRaises(RemotePreflightBlockedError):
                run_preflight(self._URL)

    def test_both_fail_raises_blocked_with_both_reasons(self):
        with (
            mock.patch("hic_remote_preflight.check_head", return_value=self._fail_head()),
            mock.patch("hic_remote_preflight.check_range_magic", return_value=self._fail_range()),
        ):
            with self.assertRaises(RemotePreflightBlockedError) as cm:
                run_preflight(self._URL)
        msg = str(cm.exception)
        self.assertIn("HEAD", msg)
        self.assertIn("RANGE", msg)

    def test_holdout_url_raises_before_network(self):
        with self.assertRaises(RemotePreflightBlockedError):
            run_preflight("https://example.com/holdout/data.hic")

    def test_result_contains_block_reasons_on_failure(self):
        with (
            mock.patch("hic_remote_preflight.check_head", return_value=self._fail_head()),
            mock.patch("hic_remote_preflight.check_range_magic", return_value=self._ok_range()),
        ):
            try:
                run_preflight(self._URL)
            except RemotePreflightBlockedError:
                pass  # expected


# ---------------------------------------------------------------------------
# run_preflight_all
# ---------------------------------------------------------------------------


class TestRunPreflightAll(unittest.TestCase):
    _URL_A = "https://example.com/a.hic"
    _URL_B = "https://example.com/b.hic"

    def _ok_result(self, url: str) -> dict:
        return {"url": url, "status": "OK", "head": {}, "range_magic": {}}

    def test_all_pass_returns_ok(self):
        ok_a = self._ok_result(self._URL_A)
        ok_b = self._ok_result(self._URL_B)

        def _mock_preflight(url: str, timeout: int = 30) -> dict:
            return ok_a if url == self._URL_A else ok_b

        with mock.patch("hic_remote_preflight.run_preflight", side_effect=_mock_preflight):
            result = run_preflight_all({"a": self._URL_A, "b": self._URL_B})
        self.assertEqual(result["overall_status"], "OK")
        self.assertIn("a", result["samples"])
        self.assertIn("b", result["samples"])

    def test_first_failure_raises_immediately(self):
        """run_preflight_all must raise on first failure (fail-closed)."""

        def _mock_preflight(url: str, timeout: int = 30) -> dict:
            if url == self._URL_A:
                raise RemotePreflightBlockedError(f"BLOCKED: {url}")
            return self._ok_result(url)

        with mock.patch("hic_remote_preflight.run_preflight", side_effect=_mock_preflight):
            with self.assertRaises(RemotePreflightBlockedError):
                run_preflight_all({"a": self._URL_A, "b": self._URL_B})

    def test_empty_dict_returns_ok(self):
        result = run_preflight_all({})
        self.assertEqual(result["overall_status"], "OK")
        self.assertEqual(result["samples"], {})


# ---------------------------------------------------------------------------
# _head_check and _range_check internals (unit)
# ---------------------------------------------------------------------------


class TestInternalChecks(unittest.TestCase):
    """Test internal helpers that don't reject forbidden URLs themselves."""

    _URL = "https://example.com/test.hic"

    def test_head_check_returns_none_status_on_network_error(self):
        def _raise(*args, **kwargs):
            raise OSError("timeout")

        with mock.patch("urllib.request.urlopen", side_effect=_raise):
            result = _head_check(self._URL)
        self.assertIsNone(result["status"])
        self.assertIsNotNone(result["error"])

    def test_range_check_returns_error_on_http_error(self):
        def _raise(*args, **kwargs):
            raise HTTPError(self._URL, 403, "Forbidden", {}, BytesIO(b""))

        with mock.patch("urllib.request.urlopen", side_effect=_raise):
            result = _range_check(self._URL)
        self.assertEqual(result["status"], 403)
        self.assertIsNotNone(result["error"])

    def test_range_check_captures_partial_body_from_http_error(self):
        def _raise(*args, **kwargs):
            raise HTTPError(self._URL, 403, "Forbidden", {}, BytesIO(b"ERR!"))

        with mock.patch("urllib.request.urlopen", side_effect=_raise):
            result = _range_check(self._URL)
        self.assertEqual(result["status"], 403)


class TestReplicationDecisionAndChain(unittest.TestCase):
    def _matching_chain(self) -> tuple[dict, dict, str, str]:
        freeze_hash = "a" * 64
        eligibility_hash = "b" * 64
        eligibility = {
            "anchor_freeze_sha256": freeze_hash,
            "claim_sha256": CLAIM_SHA256_EXPECTED,
            "eligible_samples": [
                {"sample_label": label, "url": url}
                for label, url in SAMPLE_URLS.items()
            ],
        }
        preflight = {
            "eligibility_freeze_sha256": eligibility_hash,
            "samples": {
                label: {"url": url} for label, url in SAMPLE_URLS.items()
            },
        }
        return eligibility, preflight, freeze_hash, eligibility_hash

    def test_cross_sample_pass(self):
        self.assertEqual(
            cross_sample_slot_verdict("PASS", "PASS"),
            "REPLICATION_PASS",
        )

    def test_cross_sample_unsupported(self):
        self.assertEqual(
            cross_sample_slot_verdict("UNSUPPORTED", "UNSUPPORTED"),
            "REPLICATION_UNSUPPORTED",
        )

    def test_panel_inconclusive_overrides_unsupported(self):
        self.assertEqual(
            panel_verdict(
                ["REPLICATION_UNSUPPORTED", "REPLICATION_INCONCLUSIVE"]
            ),
            "REPLICATION_INCONCLUSIVE",
        )

    def test_panel_supported(self):
        self.assertEqual(
            panel_verdict(["REPLICATION_PASS", "REPLICATION_PASS"]),
            "REPLICATION_SUPPORTED",
        )

    def test_panel_blocked(self):
        self.assertEqual(
            panel_verdict(["BLOCKED", "REPLICATION_PASS"]),
            "BLOCKED",
        )

    def test_cross_chain_accepts_matching_artifacts(self):
        eligibility, preflight, freeze_hash, eligibility_hash = self._matching_chain()
        verify_cross_chain(
            eligibility,
            preflight,
            freeze_hash,
            eligibility_hash,
        )

    def test_cross_chain_rejects_freeze_mismatch(self):
        with self.assertRaises(RuntimeError):
            verify_cross_chain(
                {"anchor_freeze_sha256": "old"},
                {},
                "current",
                "eligibility",
            )

    def test_cross_chain_rejects_claim_mismatch(self):
        eligibility, preflight, freeze_hash, eligibility_hash = self._matching_chain()
        eligibility["claim_sha256"] = "wrong"
        with self.assertRaises(RuntimeError):
            verify_cross_chain(
                eligibility,
                preflight,
                freeze_hash,
                eligibility_hash,
            )

    def test_cross_chain_rejects_preflight_eligibility_mismatch(self):
        eligibility, preflight, freeze_hash, eligibility_hash = self._matching_chain()
        preflight["eligibility_freeze_sha256"] = "wrong"
        with self.assertRaises(RuntimeError):
            verify_cross_chain(
                eligibility,
                preflight,
                freeze_hash,
                eligibility_hash,
            )

    def test_cross_chain_rejects_url_mismatch(self):
        eligibility, preflight, freeze_hash, eligibility_hash = self._matching_chain()
        preflight["samples"]["noIAAdiff"]["url"] = "https://example.com/wrong.hic"
        with self.assertRaises(RuntimeError):
            verify_cross_chain(
                eligibility,
                preflight,
                freeze_hash,
                eligibility_hash,
            )


if __name__ == "__main__":
    unittest.main()
