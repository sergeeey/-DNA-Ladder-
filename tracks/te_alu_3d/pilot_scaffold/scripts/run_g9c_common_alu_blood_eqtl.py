#!/usr/bin/env python3
"""Run G9c multi-chrom blood eQTL after freeze. HTTP 400 → MISS."""

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
from g9_eqtl_lib import (  # noqa: E402
    PRIMARY_DATASET,
    REPLIC_DATASET,
    decide_enrichment,
    fetch_eqtl_status,
)

OUT = ROOT.parent / "09_outputs" / "prospective"
FREEZE = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json.sha256"
RESULT = OUT / "g9c_common_alu_ctcf_blood_eqtl_v1.json"
DECISION = OUT / "G9c_common_alu_ctcf_blood_eqtl_decision_v1.md"
PROGRESS = OUT / "g9c_eqtl_progress.txt"


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
        rows.append(
            {"variant_id": v["variant_id"], "role": v["role"], "status": status}
        )
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
        "# G9c — Multi-chrom common Alu/SVA × CTCF blood eQTL — DECISION v1",
        "",
        f"**Date:** {payload['created_utc'][:10]}",
        "**Claim:** `G9c_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`",
        f"**Freeze sha256:** `{payload['freeze_sha256']}`",
        f"**Chromosomes:** {payload.get('chromosomes')}",
        f"**Primary dataset:** `{PRIMARY_DATASET}`",
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
        "1. Not causal Alu→CTCF→expression.",
        "2. Not erythroid-specific.",
        "3. Does not rewrite G9/G9b.",
        "4. Not wet-lab GO / holdout unlock.",
        "",
    ]
    if payload.get("replication"):
        r = payload["replication"]
        lines += [
            "## Replication",
            "",
            f"- {r['decision']['verdict']} ({r['decision'].get('reason')})",
            "",
        ]
    DECISION.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    assert holdout_is_sealed()
    if not FREEZE.exists() or not FREEZE_SHA.exists():
        raise SystemExit("missing freeze — run freeze_g9c first")
    OUT.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text("", encoding="utf-8")
    freeze = _verify_freeze()
    freeze_sha = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    cases = [v for v in freeze["variants"] if v["role"] == "CASE_CTCF_ALU"]
    ctrls = [v for v in freeze["variants"] if v["role"] == "CTRL_ALU_NONCTCF"]
    _progress(f"freeze n_case={len(cases)} n_ctrl={len(ctrls)}")

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
            "result_id": "g9c_common_alu_ctcf_blood_eqtl_v1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "claim": "G9c_common_alu_ctcf_blood_eqtl_CLAIM_v1.md",
            "freeze_sha256": freeze_sha,
            "chromosomes": freeze.get("chromosomes"),
            "primary_dataset": PRIMARY_DATASET,
            "primary": {
                "case": {
                    "n_hit": 0,
                    "n_miss": 0,
                    "n_error": 0,
                    "n_queried": 0,
                    "n_tested": 0,
                    "error_rate": 0.0,
                },
                "ctrl": {
                    "n_hit": 0,
                    "n_miss": 0,
                    "n_error": 0,
                    "n_queried": 0,
                    "n_tested": 0,
                    "error_rate": 0.0,
                },
                "decision": decision,
                "rows": [],
            },
            "eqtl_skipped": True,
        }
        RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write_decision(payload)
        return 0

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

    payload = {
        "result_id": "g9c_common_alu_ctcf_blood_eqtl_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "G9c_common_alu_ctcf_blood_eqtl_CLAIM_v1.md",
        "freeze_sha256": freeze_sha,
        "chromosomes": freeze.get("chromosomes"),
        "primary_dataset": PRIMARY_DATASET,
        "primary": {
            "case": {
                k: case_arm[k]
                for k in (
                    "n_hit",
                    "n_miss",
                    "n_error",
                    "n_queried",
                    "n_tested",
                    "error_rate",
                )
            },
            "ctrl": {
                k: ctrl_arm[k]
                for k in (
                    "n_hit",
                    "n_miss",
                    "n_error",
                    "n_queried",
                    "n_tested",
                    "error_rate",
                )
            },
            "decision": decision,
            "rows": case_arm["rows"] + ctrl_arm["rows"],
        },
    }

    if decision["verdict"] == "PASS":
        r_case = _query_arm(cases, REPLIC_DATASET)
        r_ctrl = _query_arm(ctrls, REPLIC_DATASET)
        if r_case["error_rate"] > 0.10 or r_ctrl["error_rate"] > 0.10:
            r_dec = {
                "verdict": "INCONCLUSIVE",
                "reason": "api_error_rate",
                "p_case": float("nan"),
                "p_ctrl": float("nan"),
                "risk_diff": float("nan"),
                "fisher_p": float("nan"),
            }
        else:
            r_dec = decide_enrichment(
                r_case["n_hit"],
                r_case["n_miss"],
                r_ctrl["n_hit"],
                r_ctrl["n_miss"],
            )
        payload["replication"] = {
            "dataset": REPLIC_DATASET,
            "case": {
                k: r_case[k]
                for k in (
                    "n_hit",
                    "n_miss",
                    "n_error",
                    "n_queried",
                    "n_tested",
                    "error_rate",
                )
            },
            "ctrl": {
                k: r_ctrl[k]
                for k in (
                    "n_hit",
                    "n_miss",
                    "n_error",
                    "n_queried",
                    "n_tested",
                    "error_rate",
                )
            },
            "decision": r_dec,
        }

    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_decision(payload)
    _progress(f"verdict={decision['verdict']} reason={decision.get('reason')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
