#!/usr/bin/env python3
"""G12b: within CTCF, Alu vs non-Alu × HUDEP-2 DNase."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))

from holdout_guard import holdout_is_sealed  # noqa: E402
from g9_eqtl_lib import decide_enrichment  # noqa: E402
from run_g12_common_alu_hudep2_dnase import (  # noqa: E402
    PRIMARY,
    REPLIC,
    fetch_peaks,
    load_dnase_intervals,
    score_arm,
)

OUT = ROOT.parent / "09_outputs" / "prospective"
FREEZE = OUT / "g12b_ctcf_alu_vs_nonalu_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g12b_ctcf_alu_vs_nonalu_panel_freeze_v1.json.sha256"
RESULT = OUT / "g12b_ctcf_alu_vs_nonalu_dnase_v1.json"
DECISION = OUT / "G12b_ctcf_alu_vs_nonalu_dnase_decision_v1.md"
CLAIM = "G12b_ctcf_alu_vs_nonalu_dnase_CLAIM_v1.md"


def _verify_freeze() -> tuple[dict, str]:
    text = FREEZE.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    expected = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    if digest != expected:
        raise RuntimeError(f"freeze hash mismatch: {digest} != {expected}")
    return json.loads(text), digest


def write_decision(payload: dict) -> None:
    prim = payload["primary"]
    dec = prim["decision"]
    lines = [
        "# G12b — Within CTCF Alu vs non-Alu × HUDEP-2 DNase — DECISION v1",
        "",
        f"**Date:** {payload['created_utc'][:10]}",
        f"**Claim:** `{CLAIM}`",
        f"**Freeze sha256:** `{payload['freeze_sha256']}`",
        f"**Primary peaks:** `{prim['accession']}`",
        f"**Verdict:** **{dec['verdict']}** ({dec.get('reason', '')})",
        "",
        "## Primary counts",
        "",
        f"- CASE CTCF∩Alu: hit={prim['case']['n_hit']} miss={prim['case']['n_miss']}",
        f"- CTRL CTCF∩non-Alu: hit={prim['ctrl']['n_hit']} miss={prim['ctrl']['n_miss']}",
        f"- p_case={dec.get('p_case')} p_ctrl={dec.get('p_ctrl')} "
        f"risk_diff={dec.get('risk_diff')} fisher_p={dec.get('fisher_p')}",
        "",
        "## What this does NOT mean",
        "",
        "1. Not expression / eQTL / Hi-C.",
        "2. Not causal Alu→accessibility.",
        "3. Not wet-lab GO.",
        "",
    ]
    if payload.get("replication"):
        r = payload["replication"]
        lines += [
            "## Replication",
            "",
            f"- {r['accession']}: {r['decision']['verdict']} ({r['decision'].get('reason')})",
            "",
        ]
    DECISION.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    assert holdout_is_sealed()
    freeze, freeze_sha = _verify_freeze()
    cases = [v for v in freeze["variants"] if v["role"] == "CASE_CTCF_ALU"]
    ctrls = [v for v in freeze["variants"] if v["role"] == "CTRL_CTCF_NONALU"]
    print(f"n_case={len(cases)} n_ctrl={len(ctrls)}", flush=True)
    if len(cases) < 30 or len(ctrls) < 30:
        decision = {
            "verdict": "INCONCLUSIVE",
            "reason": "underpowered_freeze",
            "p_case": float("nan"),
            "p_ctrl": float("nan"),
            "risk_diff": float("nan"),
            "fisher_p": float("nan"),
        }
        payload = {
            "result_id": "g12b_ctcf_alu_vs_nonalu_dnase_v1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "claim": CLAIM,
            "freeze_sha256": freeze_sha,
            "primary": {"decision": decision, "eqtl_skipped": True},
        }
        RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_decision(payload)
        return 0

    peak_path, peak_sha = fetch_peaks(PRIMARY)
    peaks = load_dnase_intervals(peak_path)
    case_arm = score_arm(cases, peaks)
    ctrl_arm = score_arm(ctrls, peaks)
    decision = decide_enrichment(
        case_arm["n_hit"], case_arm["n_miss"], ctrl_arm["n_hit"], ctrl_arm["n_miss"]
    )
    payload: dict = {
        "result_id": "g12b_ctcf_alu_vs_nonalu_dnase_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": CLAIM,
        "freeze_sha256": freeze_sha,
        "primary": {
            "experiment": PRIMARY["experiment"],
            "accession": PRIMARY["accession"],
            "peaks_sha256": peak_sha,
            "case": {
                "n_hit": case_arm["n_hit"],
                "n_miss": case_arm["n_miss"],
                "n_tested": case_arm["n_tested"],
            },
            "ctrl": {
                "n_hit": ctrl_arm["n_hit"],
                "n_miss": ctrl_arm["n_miss"],
                "n_tested": ctrl_arm["n_tested"],
            },
            "decision": decision,
            "rows": case_arm["rows"] + ctrl_arm["rows"],
        },
    }
    if decision.get("verdict") == "PASS":
        rpath, rsha = fetch_peaks(REPLIC)
        rpeaks = load_dnase_intervals(rpath)
        rc = score_arm(cases, rpeaks)
        rr = score_arm(ctrls, rpeaks)
        rdec = decide_enrichment(rc["n_hit"], rc["n_miss"], rr["n_hit"], rr["n_miss"])
        payload["replication"] = {
            "experiment": REPLIC["experiment"],
            "accession": REPLIC["accession"],
            "peaks_sha256": rsha,
            "case": {"n_hit": rc["n_hit"], "n_miss": rc["n_miss"]},
            "ctrl": {"n_hit": rr["n_hit"], "n_miss": rr["n_miss"]},
            "decision": rdec,
        }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_decision(payload)
    print(f"DONE verdict={decision['verdict']} reason={decision.get('reason')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
