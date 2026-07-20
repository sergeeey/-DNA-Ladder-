"""Unit tests for T6 caller-swap helpers (no large downloads)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_caller_swap_meta_lists_delta_not_mustache():
    t6 = _load("t6_caller_swap_k562")
    assert t6.PRIMARY_HIC["accession"] == "ENCFF693XIL"
    accs = {a["accession"] for a in t6.ALTERNATES}
    assert "ENCFF657QKE" in accs  # DELTA
    assert "Mustache" in t6.MUSTACHE_NOTE or "mustache" in t6.MUSTACHE_NOTE.lower()
    assert t6.MUSTACHE_NOTE  # documents unavailability


def test_desk_verdict_thresholds_shared_with_t3():
    t3 = _load("t3_primary_alusz_or")
    fail = t3.desk_verdict(0.91, 0.85, 0.97)
    assert fail["verdict"] == "FAIL_DESK_PRIMARY"
    mid = t3.desk_verdict(1.11, 1.05, 1.17)
    assert mid["verdict"] == "INCONCLUSIVE_DESK"
    support = t3.desk_verdict(1.35, 1.20, 1.50)
    assert support["verdict"] == "SUPPORT_DESK"


def test_caller_swap_results_artifact_if_present():
    results = Path(__file__).resolve().parent.parent / "results" / "caller_swap_k562.json"
    if not results.exists():
        pytest.skip("caller_swap_k562.json not present")
    import json

    data = json.loads(results.read_text())
    assert data["status"].startswith("CALLER_SWAP")
    assert data["mustache_status"] == "UNAVAILABLE_ON_ENCODE_K562_GRCh38"
    delta = next(a for a in data["alternates"] if a["accession"] == "ENCFF657QKE")
    assert delta["alusz"]["fisher_or"] < 1.1
    assert data["primary_hiccups"]["alusz"]["fisher_or"] < 1.1
