#!/usr/bin/env python3
"""Unit tests for C-F1 Mustache/HiCCUPS concordance helpers."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_claim_prereg_exists():
    claim = (ROOT / "claim.md").read_text(encoding="utf-8")
    assert "C-F1" in claim
    assert "Mustache" in claim
    assert "ENCFF693XIL" in claim
    assert "BLOCKED_DATA" in claim


def test_t0_probe_json():
    path = ROOT / "data" / "t0_accession_probe.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "C-F1"
    assert data["verdict"] == "BLOCKED_DATA"
    assert data["mustache_hits"] == []
    hic = data.get("hiccups_files") or []
    assert any(x.get("accession") == "ENCFF693XIL" for x in hic)


def test_decision_blocked():
    text = (ROOT / "decision.md").read_text(encoding="utf-8")
    assert "BLOCKED_DATA" in text
    assert "Mustache" in text
    assert "DELTA" in text  # explicit non-substitution


if __name__ == "__main__":
    test_claim_prereg_exists()
    test_t0_probe_json()
    test_decision_blocked()
    print("OK")
