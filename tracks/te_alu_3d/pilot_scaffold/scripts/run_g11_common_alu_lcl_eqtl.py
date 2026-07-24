#!/usr/bin/env python3
"""Run G11 LCL eQTL enrichment on frozen G9c panel. Primary QTD000221."""

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
from g9_eqtl_lib import decide_enrichment, fetch_eqtl_status  # noqa: E402

OUT = ROOT.parent / "09_outputs" / "prospective"
FREEZE = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json.sha256"
RESULT = OUT / "g11_common_alu_ctcf_lcl_eqtl_v1.json"
DECISION = OUT / "G11_common_alu_ctcf_lcl_eqtl_decision_v1.md"
PROGRESS = OUT / "g11_eqtl_progress.txt"
CLAIM = "G11_common_alu_ctcf_lcl_eqtl_CLAIM_v1.md"

PRIMARY_DATASET = "QTD000221"  # GTEx LCL
REPLIC_DATASET = "QTD000266"  # GTEx liver — only if PASS


def _progress(msg: str) -> None:
    print(msg, flush=True)
    with PROGRESS.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")


def _verify_freeze() -> dict:
    text = FREEZE.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    expected = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    if digest != expected:
        raise RuntimeError(f"freeze hash mismatch: {digest} != {expected}")
    return json.loads(text)


def _query_arm(variants: list[dict], dataset_id: str) -> dict:
    n_hit = n_miss = n_error = 0
    rows = []
    for i, v in enumerate(variants):
        _progress(f"  [{dataset_id}] {i + 1}/{len(variants)} {v['variant_id']}")
        status = fetch_eqtl_status(
            dataset_id,
            int(v["pos"]),
            v["ref"],
            v["alt"],
            chrom=v["chrom"],
            miss_on_http_400=True,
        )
        if status == "HIT":
            n_hit += 1
        elif status == "MISS":
            n_miss += 1
        else:
            n_error += 1
        rows.append({"variant_id": v["variant_id"], "role": v["role"], "status": status})
    n_queried = n_hit + n_miss + n_error
    return {
        "n_hit": n_hit,
        "n_miss": n_miss,
        "n_error": n_error,
        "n_queried": n_queried,
        "n_tested": n_hit + n_miss,
        "error_rate": (n_error / n_queried) if n_queried else 0.0,
        "rows": rows,
    }


def _write_decision(payload: dict) -> None:
    primary = payload["primary"]
    dec = primary["decision"]
    lines = [
        "# G11 — Common Alu∩CTCF × GTEx LCL eQTL — DECISION v1",
        "",
        f"**Date:** {payload['created_utc'][:10]}",
        f"**Claim:** `{CLAIM}`",
        f"**Freeze sha256:** `{payload['freeze_sha256']}`",
        f"**Primary dataset:** `{PRIMARY_DATASET}` (GTEx LCL)",
        f"**Verdict:** **{dec['verdict']}** ({dec.get('reason', '')})",
        "",
        "## Primary counts",
        "",
        f"- cases: hit={primary['case']['n_hit']} miss={primary['case']['n_miss']} "
        f"error={primary['case']['n_error']} tested={primary['case']['n_tested']}",
        f"- controls: hit={primary['ctrl']['n_hit']} miss={primary['ctrl']['n_miss']} "
        f"error={primary['ctrl']['n_error']} tested={primary['ctrl']['n_tested']}",
        f"- p_case={dec.get('p_case')} p_ctrl={dec.get('p_ctrl')} "
        f"risk_diff={dec.get('risk_diff')} fisher_p={dec.get('fisher_p')}",
        "",
        "## What this does NOT mean",
        "",
        "1. Not a rescue of G9c blood REJECT.",
        "2. Not erythroid / HUDEP-2 expression.",
        "3. Not causal Alu→CTCF→eQTL.",
        "4. Not wet-lab GO / holdout unlock.",
        "",
    ]
    if payload.get("replication"):
        r = payload["replication"]
        lines += [
            "## Replication (liver QTD000266)",
            "",
            f"- {r['decision']['verdict']} ({r['decision'].get('reason')})",
            "",
        ]
    DECISION.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    assert holdout_is_sealed()
    OUT.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text("", encoding="utf-8")
    freeze = _verify_freeze()
    freeze_sha = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    cases = [v for v in freeze["variants"] if v["role"] == "CASE_CTCF_ALU"]
    ctrls = [v for v in freeze["variants"] if v["role"] == "CTRL_ALU_NONCTCF"]
    _progress(f"freeze n_case={len(cases)} n_ctrl={len(ctrls)} primary={PRIMARY_DATASET}")

    case_arm = _query_arm(cases, PRIMARY_DATASET)
    ctrl_arm = _query_arm(ctrls, PRIMARY_DATASET)
    if case_arm["error_rate"] > 0.10 or ctrl_arm["error_rate"] > 0.10:
        decision = {
            "verdict": "INCONCLUSIVE",
            "reason": "api_error_rate",
            "p_case": float("nan"),
            "p_ctrl": float("nan"),
            "risk_diff": float("nan"),
            "fisher_p": float("nan"),
            "n_hit_case": case_arm["n_hit"],
            "n_miss_case": case_arm["n_miss"],
            "n_hit_ctrl": ctrl_arm["n_hit"],
            "n_miss_ctrl": ctrl_arm["n_miss"],
        }
    else:
        decision = decide_enrichment(
            case_arm["n_hit"],
            case_arm["n_miss"],
            ctrl_arm["n_hit"],
            ctrl_arm["n_miss"],
        )

    payload: dict = {
        "result_id": "g11_common_alu_ctcf_lcl_eqtl_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": CLAIM,
        "freeze_sha256": freeze_sha,
        "chromosomes": freeze.get("chromosomes"),
        "primary_dataset": PRIMARY_DATASET,
        "primary": {
            "case": {k: case_arm[k] for k in ("n_hit", "n_miss", "n_error", "n_queried", "n_tested", "error_rate")},
            "ctrl": {k: ctrl_arm[k] for k in ("n_hit", "n_miss", "n_error", "n_queried", "n_tested", "error_rate")},
            "decision": decision,
            "rows": case_arm["rows"] + ctrl_arm["rows"],
        },
    }

    if decision.get("verdict") == "PASS":
        _progress(f"REPLICATION {REPLIC_DATASET}…")
        rc = _query_arm(cases, REPLIC_DATASET)
        rr = _query_arm(ctrls, REPLIC_DATASET)
        if rc["error_rate"] > 0.10 or rr["error_rate"] > 0.10:
            rdec = {"verdict": "INCONCLUSIVE", "reason": "api_error_rate"}
        else:
            rdec = decide_enrichment(rc["n_hit"], rc["n_miss"], rr["n_hit"], rr["n_miss"])
        payload["replication"] = {
            "dataset": REPLIC_DATASET,
            "case": {k: rc[k] for k in ("n_hit", "n_miss", "n_error", "n_tested", "error_rate")},
            "ctrl": {k: rr[k] for k in ("n_hit", "n_miss", "n_error", "n_tested", "error_rate")},
            "decision": rdec,
        }

    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_decision(payload)
    _progress(f"DONE verdict={decision['verdict']} reason={decision.get('reason')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
