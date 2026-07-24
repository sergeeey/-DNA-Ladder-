"""Tests for G10 slot selection + panel decision."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "pilot_scaffold" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from freeze_g10_common_alu_ctcf_anchors import select_g10_slots  # noqa: E402
from run_g10_common_alu_ctcf_indep_hic import decide_panel  # noqa: E402


def test_select_g10_slots_deterministic():
    g9c = {
        "variants": [
            {
                "role": "CASE_CTCF_ALU",
                "chrom": "chr11",
                "pos": 75445532,
                "ref": "G",
                "alt": "A",
                "variant_id": "chr11:75445532:G:A",
                "peak_start": 1,
                "peak_end": 2,
                "af": 0.1,
            },
            {
                "role": "CASE_CTCF_ALU",
                "chrom": "chr11",
                "pos": 100,
                "ref": "A",
                "alt": "T",
                "variant_id": "chr11:100:A:T",
                "peak_start": 90,
                "peak_end": 110,
                "af": 0.2,
            },
            {
                "role": "CASE_CTCF_ALU",
                "chrom": "chr11",
                "pos": 105,
                "ref": "A",
                "alt": "C",
                "variant_id": "chr11:105:A:C",
                "peak_start": 90,
                "peak_end": 110,
                "af": 0.2,
            },
            {
                "role": "CASE_CTCF_ALU",
                "chrom": "chr11",
                "pos": 200,
                "ref": "C",
                "alt": "G",
                "variant_id": "chr11:200:C:G",
                "peak_start": 190,
                "peak_end": 210,
                "af": 0.3,
            },
            {
                "role": "CASE_CTCF_ALU",
                "chrom": "chr11",
                "pos": 300,
                "ref": "G",
                "alt": "T",
                "variant_id": "chr11:300:G:T",
                "peak_start": 290,
                "peak_end": 310,
                "af": 0.4,
            },
            {
                "role": "CASE_CTCF_ALU",
                "chrom": "chr11",
                "pos": 400,
                "ref": "T",
                "alt": "A",
                "variant_id": "chr11:400:T:A",
                "peak_start": 390,
                "peak_end": 410,
                "af": 0.5,
            },
        ]
    }
    slots = select_g10_slots(g9c)
    assert len(slots) == 4
    assert slots[0]["variant"] == "chr11:100:A:T"
    assert slots[1]["variant"] == "chr11:200:C:G"
    assert [s["slot_id"] for s in slots] == ["G10_01", "G10_02", "G10_03", "G10_04"]


def test_decide_panel_pass_reject_inconclusive():
    assert decide_panel(["PASS", "PASS", "UNSUPPORTED", "PARTIAL"])["verdict"] == "PASS"
    assert decide_panel(["UNSUPPORTED", "UNSUPPORTED", "PARTIAL", "INCONCLUSIVE"])[
        "verdict"
    ] == "REJECT"
    assert decide_panel(["PASS", "UNSUPPORTED", "PARTIAL", "INCONCLUSIVE"])[
        "verdict"
    ] == "INCONCLUSIVE"
    assert decide_panel(["BLOCKED", "PASS"])["verdict"] == "INCONCLUSIVE"
    assert decide_panel(["PASS", "PASS"])["need_pass"] == 2
    assert math.ceil(3 / 2) == 2
