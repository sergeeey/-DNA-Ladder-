"""Remote .hic URL preflight for G4c independent-source replication.

Performs two network checks (fail-closed; no fallback):

  1. HTTP HEAD: URL reachable, HTTP 200, Content-Length > 0,
     Accept-Ranges header == "bytes".
  2. HTTP GET with Range: bytes=0-3: server returns HTTP 206 (Partial Content),
     response body first 3 bytes == b"HIC".

If any check fails, `run_preflight` raises `RemotePreflightBlockedError` and
callers must stop immediately.  Do not improvise alternative approaches.

Usage::

    from hic_remote_preflight import run_preflight
    result = run_preflight(url)   # raises if BLOCKED; returns dict if OK
"""

from __future__ import annotations

import urllib.error
import urllib.request
from typing import Any


HIC_MAGIC = b"HIC"
_RANGE_BYTES = "bytes=0-3"

# URLs that must never be accessed
_FORBIDDEN_SUBSTRINGS = ("holdout",)


class RemotePreflightBlockedError(RuntimeError):
    """Raised when any preflight check fails; replication is BLOCKED."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _reject_forbidden_url(url: str) -> None:
    """Raise RemotePreflightBlockedError if URL contains a forbidden substring."""
    lower = url.lower()
    for sub in _FORBIDDEN_SUBSTRINGS:
        if sub in lower:
            raise RemotePreflightBlockedError(f"FORBIDDEN: URL contains '{sub}': {url}")


def _head_check(url: str, timeout: int = 30) -> dict[str, Any]:
    """Perform HTTP HEAD request; return dict with status, headers, error.

    Does not raise on HTTP error — returns error field instead.
    Caller must inspect and decide.
    """
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {
                "status": resp.status,
                "content_length": resp.headers.get("Content-Length"),
                "accept_ranges": resp.headers.get("Accept-Ranges"),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "status": exc.code,
            "content_length": None,
            "accept_ranges": None,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "status": None,
            "content_length": None,
            "accept_ranges": None,
            "error": str(exc),
        }


def _range_check(
    url: str, byte_range: str = _RANGE_BYTES, timeout: int = 30
) -> dict[str, Any]:
    """Perform HTTP GET with Range header; return dict with status, data, error.

    Does not raise on HTTP error — returns error field instead.
    """
    req = urllib.request.Request(url, headers={"Range": byte_range})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(4)
            return {"status": resp.status, "data": data, "error": None}
    except urllib.error.HTTPError as exc:
        # HTTP 206 Partial Content is returned as a normal response by urlopen,
        # so an HTTPError here means an actual error (4xx/5xx).
        body = exc.read(4) if exc.fp else b""
        return {"status": exc.code, "data": body, "error": str(exc)}
    except Exception as exc:
        return {"status": None, "data": b"", "error": str(exc)}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_head(url: str, timeout: int = 30) -> dict[str, Any]:
    """Check HEAD response for url; return structured result (does not raise)."""
    _reject_forbidden_url(url)
    result = _head_check(url, timeout=timeout)
    result["url"] = url
    result["check"] = "head"

    # Determine eligibility
    ok_status = result["status"] == 200
    cl = result.get("content_length")
    ok_length = cl is not None and int(cl) > 0
    ar = (result.get("accept_ranges") or "").lower()
    ok_ranges = ar == "bytes"

    result["ok_status"] = ok_status
    result["ok_length"] = ok_length
    result["ok_ranges"] = ok_ranges
    result["eligible"] = ok_status and ok_length and ok_ranges
    return result


def check_range_magic(url: str, timeout: int = 30) -> dict[str, Any]:
    """Check byte-range response and .hic magic bytes; return structured result (does not raise)."""
    _reject_forbidden_url(url)
    result = _range_check(url, timeout=timeout)
    result["url"] = url
    result["check"] = "range_magic"

    data: bytes = result.get("data") or b""
    ok_206 = result["status"] == 206
    ok_magic = len(data) >= 3 and data[:3] == HIC_MAGIC
    result["ok_206"] = ok_206
    result["ok_magic"] = ok_magic
    result["magic_bytes_hex"] = data[:3].hex() if data else ""
    result["eligible"] = ok_206 and ok_magic
    return result


def run_preflight(
    url: str,
    timeout: int = 30,
) -> dict[str, Any]:
    """Run full preflight for one .hic URL.

    Returns a result dict with ``status`` == ``"OK"`` on success.
    Raises ``RemotePreflightBlockedError`` if any check fails.
    """
    _reject_forbidden_url(url)

    head_result = check_head(url, timeout=timeout)
    range_result = check_range_magic(url, timeout=timeout)

    all_ok = head_result["eligible"] and range_result["eligible"]

    result: dict[str, Any] = {
        "url": url,
        "head": head_result,
        "range_magic": range_result,
        "status": "OK" if all_ok else "BLOCKED",
    }

    if not all_ok:
        reasons: list[str] = []
        if not head_result["eligible"]:
            reasons.append(
                f"HEAD failed: status={head_result['status']}, "
                f"ok_length={head_result.get('ok_length')}, "
                f"ok_ranges={head_result.get('ok_ranges')}, "
                f"error={head_result.get('error')}"
            )
        if not range_result["eligible"]:
            reasons.append(
                f"RANGE/MAGIC failed: status={range_result['status']}, "
                f"ok_206={range_result.get('ok_206')}, "
                f"ok_magic={range_result.get('ok_magic')}, "
                f"magic_hex={range_result.get('magic_bytes_hex')}, "
                f"error={range_result.get('error')}"
            )
        result["block_reasons"] = reasons
        raise RemotePreflightBlockedError(
            f"BLOCKED — preflight failed for {url}:\n"
            + "\n".join(f"  - {r}" for r in reasons)
        )

    return result


def run_preflight_all(
    urls: dict[str, str],
    timeout: int = 30,
) -> dict[str, Any]:
    """Run preflight for all named URLs.

    Args:
        urls: mapping of label → URL.
        timeout: per-request timeout in seconds.

    Returns:
        dict with ``overall_status`` == ``"OK"`` if all pass, else raises.

    Raises:
        RemotePreflightBlockedError: on first failure (fail-closed).
    """
    results: dict[str, Any] = {}
    for label, url in urls.items():
        results[label] = run_preflight(url, timeout=timeout)
    return {"overall_status": "OK", "samples": results}
