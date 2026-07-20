#!/usr/bin/env python3
"""Unit tests for C-I1 T0 verdict classifier."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "t0_probe_microc_vs_hic.py"


def _load():
    spec = importlib.util.spec_from_file_location("t0_microc", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_blocked_without_bedpe():
    mod = _load()
    r = {
        "encode_usable_microc_grch38_bedpe": False,
        "fourdn_usable_microc_grch38_bedpe": False,
    }
    assert mod.classify_verdict(r) == "BLOCKED_DATA"


def test_pass_encode():
    mod = _load()
    r = {
        "encode_usable_microc_grch38_bedpe": True,
        "fourdn_usable_microc_grch38_bedpe": False,
    }
    assert mod.classify_verdict(r) == "PASS_FREEZE_CANDIDATE"


def test_pass_fourdn():
    mod = _load()
    r = {
        "encode_usable_microc_grch38_bedpe": False,
        "fourdn_usable_microc_grch38_bedpe": True,
    }
    assert mod.classify_verdict(r) == "PASS_FREEZE_CANDIDATE"


if __name__ == "__main__":
    test_blocked_without_bedpe()
    test_pass_encode()
    test_pass_fourdn()
    print("OK")
