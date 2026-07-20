"""Unit tests for C-A2 switcher / matching / Fisher helpers (no network)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "scripts" / "c_a2_lib.py"
T0 = Path(__file__).resolve().parents[1] / "scripts" / "t0_probe_screen_matrix.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_active_rule():
    mod = _load(LIB, "c_a2_lib")
    assert mod.is_active_classification("dELS", "All-data/Full-classification")
    assert mod.is_active_classification("dELS,CTCF-bound", "All-data/Full-classification")
    assert not mod.is_active_classification("pELS", "All-data/Full-classification")
    assert not mod.is_active_classification("dELS", "Missing-data/Partial-classification")
    assert not mod.is_active_classification("Low-DNase", "All-data/Full-classification")


def test_switcher_definition():
    mod = _load(LIB, "c_a2_lib")
    # N=10: need A>=1 and inactive>=3
    assert mod.switcher_flag([True] + [False] * 9)
    assert mod.switcher_flag([True] * 7 + [False] * 3)
    assert not mod.switcher_flag([False] * 10)  # never active
    assert not mod.switcher_flag([True] * 8 + [False] * 2)  # only 2 inactive


def test_match_before_outcome_invariant():
    """Matching uses only covariate keys — no switcher in key space."""
    mod = _load(LIB, "c_a2_lib")
    pool = {
        ("chr1", 0, 0, 0, 0): [f"c{i}" for i in range(20)],
        ("chr1", 0, 0, 0, 1): [f"d{i}" for i in range(5)],
    }
    exposed = [("s0", ("chr1", 0, 0, 0, 0)), ("s1", ("chr1", 0, 0, 0, 0))]
    m = mod.match_1k(exposed, pool, k=5, seed=20260720)
    assert len(m["s0"]) == 5
    assert len(m["s1"]) == 5
    assert set(m["s0"]).isdisjoint(m["s1"])


def test_fisher_or_direction():
    mod = _load(LIB, "c_a2_lib")
    or_hi, _, _, _ = mod.fisher_or_woolf(40, 10, 20, 30)
    or_lo, _, _, _ = mod.fisher_or_woolf(10, 40, 30, 20)
    assert or_hi > 1.0
    assert or_lo < 1.0


def test_t0_blocked_without_panel():
    mod = _load(T0, "t0_probe_screen_matrix")
    assert (
        mod.classify_verdict(
            {
                "registry_v3_ok": True,
                "n_switching_beds_ok": 3,
                "baseline_bed_ok": True,
                "rmsk_ok": True,
            }
        )
        == "BLOCKED_DATA"
    )
    assert (
        mod.classify_verdict(
            {
                "registry_v3_ok": True,
                "n_switching_beds_ok": 10,
                "baseline_bed_ok": True,
                "rmsk_ok": True,
            }
        )
        == "PASS_FREEZE_CANDIDATE"
    )
