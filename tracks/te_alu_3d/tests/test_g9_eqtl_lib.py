"""Unit tests for G9 eQTL enrichment helpers."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "pilot_scaffold" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from g9_eqtl_lib import (  # noqa: E402
    af_decile,
    cap_sorted,
    classify_eqtl_query_result,
    decide_enrichment,
    excluded_pos,
    fisher_exact_2x2,
    in_expanded_peaks,
    in_half_open,
    is_eqtl_hit,
    match_controls_by_af_decile,
    variant_id,
)


def test_half_open_boundaries():
    assert not in_half_open(100, 100, 200)
    assert in_half_open(101, 100, 200)
    assert in_half_open(200, 100, 200)
    assert not in_half_open(201, 100, 200)


def test_excluded_holdout_and_hbb():
    assert excluded_pos(5_250_000)
    assert excluded_pos(65_000_000)
    assert not excluded_pos(10_000_000)
    assert not excluded_pos(5_199_999)


def test_expanded_peaks_pad():
    peaks = [(1000, 1100, "p")]
    assert in_expanded_peaks(peaks, 1001, 250)
    assert in_expanded_peaks(peaks, 751, 250)  # 1000-250+1
    assert not in_expanded_peaks(peaks, 750, 250)
    assert in_expanded_peaks(peaks, 1350, 250)
    assert not in_expanded_peaks(peaks, 1351, 250)


def test_af_decile_bounds():
    assert af_decile(0.04) == -1
    assert af_decile(0.05) == 0
    assert af_decile(0.274) == 4
    assert af_decile(0.50) == 9
    assert af_decile(0.51) == 10
    assert af_decile(0.02, af_min=0.01, af_max=0.50) == 0
    assert af_decile(0.009, af_min=0.01, af_max=0.50) == -1


def test_eqtl_hit_by_pvalue():
    assert is_eqtl_hit([{"pvalue": 1e-9}])
    assert not is_eqtl_hit([{"pvalue": 1e-6}])
    assert not is_eqtl_hit([])


def test_eqtl_hit_by_nlog10p():
    assert is_eqtl_hit([{"nlog10p": 8.0}])
    assert not is_eqtl_hit([{"neg_log10_pvalue": 5.0}])


def test_fisher_balanced_nullish():
    p = fisher_exact_2x2(10, 10, 10, 10)
    assert p == pytest.approx(1.0)


def test_fisher_extreme():
    p = fisher_exact_2x2(20, 0, 0, 20)
    assert p < 1e-6


def test_decide_pass():
    d = decide_enrichment(40, 10, 10, 40)
    assert d["verdict"] == "PASS"
    assert d["p_case"] > d["p_ctrl"]


def test_decide_wrong_direction_reject():
    d = decide_enrichment(10, 40, 40, 10)
    assert d["verdict"] == "REJECT"
    assert d["reason"] == "wrong_direction"


def test_decide_negligible_reject():
    d = decide_enrichment(16, 34, 15, 35)  # diff ~0.02, n=50
    assert d["verdict"] == "REJECT"
    assert d["reason"] == "negligible_diff"


def test_decide_underpowered():
    d = decide_enrichment(5, 5, 5, 5)
    assert d["verdict"] == "INCONCLUSIVE"
    assert d["reason"] == "underpowered"


def test_match_controls_af_decile_reproducible():
    cases = [
        {"chrom": "chr11", "pos": 1, "ref": "A", "alt": "G", "af": 0.06},
        {"chrom": "chr11", "pos": 2, "ref": "A", "alt": "C", "af": 0.20},
        {"chrom": "chr11", "pos": 3, "ref": "A", "alt": "T", "af": 0.45},
    ]
    pool = [
        {"chrom": "chr11", "pos": 100 + i, "ref": "A", "alt": "G", "af": af}
        for i, af in enumerate([0.055, 0.07, 0.19, 0.21, 0.44, 0.48, 0.30])
    ]
    a = match_controls_by_af_decile(cases, pool, seed=20260722, cap=3)
    b = match_controls_by_af_decile(cases, pool, seed=20260722, cap=3)
    assert len(a) == 3
    assert [variant_id(**{k: v[k] for k in ("chrom", "pos", "ref", "alt")}) for v in a] == [
        variant_id(**{k: v[k] for k in ("chrom", "pos", "ref", "alt")}) for v in b
    ]


def test_cap_sorted():
    rows = [
        {"pos": 3, "ref": "A", "alt": "G"},
        {"pos": 1, "ref": "C", "alt": "T"},
        {"pos": 2, "ref": "A", "alt": "C"},
    ]
    out = cap_sorted(rows, cap=2)
    assert [r["pos"] for r in out] == [1, 2]


def test_fisher_rejects_negative():
    with pytest.raises(ValueError):
        fisher_exact_2x2(-1, 0, 0, 0)


def test_nlog_threshold_matches_pvalue():
    assert math.isclose(-math.log10(5e-8), 7.30102999566, rel_tol=1e-9)


def test_classify_http_400_is_miss():
    assert classify_eqtl_query_result(None, http_status=400) == "MISS"


def test_classify_empty_is_miss():
    assert classify_eqtl_query_result([], http_status=200) == "MISS"


def test_classify_hit():
    assert classify_eqtl_query_result([{"pvalue": 1e-9}], http_status=200) == "HIT"


def test_classify_server_error():
    assert classify_eqtl_query_result(None, http_status=503) == "ERROR"
