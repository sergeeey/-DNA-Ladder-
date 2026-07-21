#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent


def test_claim_and_t0():
    claim = (ROOT / "claim.md").read_text(encoding="utf-8")
    assert "C-E1" in claim
    assert "non-HBB" in claim
    assert "holdout" in claim.lower() or "HO" in claim
    assert "0.20" in claim
    data = json.loads((ROOT / "data" / "t0_accession_probe.json").read_text(encoding="utf-8"))
    assert data["candidate_id"] == "C-E1"
    assert data["verdict"] == "T0_PASS_FREEZE"
    assert data["genomewide_non_hbb_rare_snv_panel_on_disk"] is False


if __name__ == "__main__":
    test_claim_and_t0()
    print("OK")
