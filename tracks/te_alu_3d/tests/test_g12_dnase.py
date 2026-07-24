"""Tests for G12 DNase overlap helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "pilot_scaffold" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_g12_common_alu_hudep2_dnase import score_arm, variant_in_peaks  # noqa: E402


def test_variant_in_peaks_half_open():
    peaks = [("chr11", 100, 200, ".")]
    assert not variant_in_peaks(peaks, "chr11", 100)
    assert variant_in_peaks(peaks, "chr11", 101)
    assert variant_in_peaks(peaks, "chr11", 200)
    assert not variant_in_peaks(peaks, "chr11", 201)
    assert not variant_in_peaks(peaks, "chr1", 150)


def test_score_arm_counts():
    peaks = [("chr1", 10, 20, "."), ("chr1", 50, 60, ".")]
    variants = [
        {"variant_id": "a", "role": "CASE", "chrom": "chr1", "pos": 15},
        {"variant_id": "b", "role": "CASE", "chrom": "chr1", "pos": 40},
        {"variant_id": "c", "role": "CASE", "chrom": "chr1", "pos": 55},
    ]
    arm = score_arm(variants, peaks)
    assert arm["n_hit"] == 2
    assert arm["n_miss"] == 1
