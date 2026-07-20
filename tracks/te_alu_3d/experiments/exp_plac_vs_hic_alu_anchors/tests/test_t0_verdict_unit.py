"""Unit tests for C-K1 T0 verdict classifier (no network)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t0_probe_plac_vs_hic.py"


def _load():
    spec = importlib.util.spec_from_file_location("t0_probe_plac_vs_hic", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_classify_blocked_when_no_bedpe():
    mod = _load()
    assert (
        mod.classify_verdict(
            {
                "encode_usable_plac_grch38_bedpe": False,
                "fourdn_usable_plac_grch38_bedpe": False,
            }
        )
        == "BLOCKED_DATA"
    )


def test_classify_pass_when_encode_bedpe():
    mod = _load()
    assert (
        mod.classify_verdict(
            {
                "encode_usable_plac_grch38_bedpe": True,
                "fourdn_usable_plac_grch38_bedpe": False,
            }
        )
        == "PASS_FREEZE_CANDIDATE"
    )


def test_classify_pass_when_fourdn_bedpe():
    mod = _load()
    assert (
        mod.classify_verdict(
            {
                "encode_usable_plac_grch38_bedpe": False,
                "fourdn_usable_plac_grch38_bedpe": True,
            }
        )
        == "PASS_FREEZE_CANDIDATE"
    )
