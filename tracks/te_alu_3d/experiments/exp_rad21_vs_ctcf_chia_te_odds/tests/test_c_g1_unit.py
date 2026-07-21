#!/usr/bin/env python3
"""Unit tests for C-G1 T0."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_t0_blocked():
    data = json.loads((ROOT / "data" / "t0_accession_probe.json").read_text())
    assert data["candidate_id"] == "C-G1"
    assert data["verdict"] == "BLOCKED_DATA"
    assert data["rad21_grch38_loop_bedpe"] == []
    assert any(x["accession"] == "ENCFF118PBQ" for x in data["ctcf_grch38_loop_bedpe"])


if __name__ == "__main__":
    test_t0_blocked()
    print("OK")
