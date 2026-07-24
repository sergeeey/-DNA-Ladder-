#!/usr/bin/env python3
"""Run G9 blood eQTL enrichment AFTER freeze hash exists.

Primary dataset QTD000356 only. Replication QTD000373 only if PASS.
"""

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
    fetch_eqtl_associations,
    is_eqtl_hit,
)

OUT = ROOT.parent / "09_outputs" / "prospective"
FREEZE = OUT / "g9_common_alu_ctcf_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g9_common_alu_ctcf_panel_freeze_v1.json.sha256"
RESULT = OUT / "g9_common_alu_ctcf_blood_eqtl_v1.json"
DECISION = OUT / "G9_common_alu_ctcf_blood_eqtl_decision_v1.md"


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
        print(
            f"  [{dataset_id}] {i + 1}/{len(variants)} {v['variant_id']}",
            flush=True,
        )
        try:
            assoc = fetch_eqtl_associations(
                dataset_id, int(v["pos"]), v["ref"], v["alt"]
            )
            hit = is_eqtl_hit(assoc)
            if hit:
                n_hit += 1
            else:
                n_miss += 1
            rows.append(
                {
                    "variant_id": v["variant_id"],
                    "role": v["role"],
                    "status": "HIT" if hit else "MISS",
                    "n_assoc_returned": len(assoc),
                }
            )
        except Exception as exc:  # noqa: BLE001 — counted as ERROR per claim
            n_error += 1
            rows.append(
                {
                    "variant_id": v["variant_id"],
                    "role": v["role"],
                    "status": "ERROR",
                    "error": str(exc)[:200],
                }
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
        "# G9 — Common Alu/SVA × CTCF blood eQTL — DECISION v1",
        "",
        f"**Date:** {payload['created_utc'][:10]}",
        f"**Claim:** `G9_common_alu_ctcf_blood_eqtl_CLAIM_v1.md`",
        f"**Freeze sha256:** `{payload['freeze_sha256']}`",
        f"**Primary dataset:** `{PRIMARY_DATASET}` (GTEx blood ge)",
        f"**Verdict:** **{dec['verdict']}** ({dec.get('reason', '')})",
        "",
        "## Primary counts",
        "",
        f"- cases tested: {primary['case']['n_tested']} "
        f"(hit={primary['case']['n_hit']}, miss={primary['case']['n_miss']}, "
        f"error={primary['case']['n_error']})",
        f"- controls tested: {primary['ctrl']['n_tested']} "
        f"(hit={primary['ctrl']['n_hit']}, miss={primary['ctrl']['n_miss']}, "
        f"error={primary['ctrl']['n_error']})",
        f"- p_case={dec['p_case']:.4f}  p_ctrl={dec['p_ctrl']:.4f}  "
        f"risk_diff={dec['risk_diff']:.4f}  fisher_p={dec['fisher_p']:.4g}",
        "",
        "## What this does NOT mean",
        "",
        "1. Not causal Alu → CTCF → expression.",
        "2. Not erythroid / HUDEP-2 specific (whole blood only).",
        "3. Not a rescue of Stage-3 Hi-C or G8 rare-panel gap.",
        "4. Not wet-lab GO / holdout unlock.",
        "",
    ]
    if payload.get("replication"):
        r = payload["replication"]
        lines += [
            "## Replication (QTD000373)",
            "",
            f"- verdict helper: {r['decision']['verdict']} "
            f"({r['decision'].get('reason', '')})",
            f"- p_case={r['decision']['p_case']:.4f} "
            f"p_ctrl={r['decision']['p_ctrl']:.4f} "
            f"fisher_p={r['decision']['fisher_p']:.4g}",
            "",
        ]
    DECISION.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    assert holdout_is_sealed(), "holdout must be SEALED"
    if not FREEZE.exists() or not FREEZE_SHA.exists():
        raise SystemExit("freeze artifacts missing — run freeze script first")
    freeze = _verify_freeze()
    freeze_sha = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]

    cases = [v for v in freeze["variants"] if v["role"] == "CASE_CTCF_ALU"]
    ctrls = [v for v in freeze["variants"] if v["role"] == "CTRL_ALU_NONCTCF"]
    print(f"freeze n_case={len(cases)} n_ctrl={len(ctrls)}", flush=True)

    print("PRIMARY QTD000356 cases…", flush=True)
    case_arm = _query_arm(cases, PRIMARY_DATASET)
    print("PRIMARY QTD000356 controls…", flush=True)
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
        "result_id": "g9_common_alu_ctcf_blood_eqtl_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "G9_common_alu_ctcf_blood_eqtl_CLAIM_v1.md",
        "freeze_sha256": freeze_sha,
        "primary_dataset": PRIMARY_DATASET,
        "primary": {
            "case": {k: case_arm[k] for k in ("n_hit", "n_miss", "n_error", "n_queried", "n_tested", "error_rate")},
            "ctrl": {k: ctrl_arm[k] for k in ("n_hit", "n_miss", "n_error", "n_queried", "n_tested", "error_rate")},
            "decision": decision,
            "rows": case_arm["rows"] + ctrl_arm["rows"],
        },
    }

    if decision["verdict"] == "PASS":
        print("REPLICATION QTD000373…", flush=True)
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
            "case": {k: r_case[k] for k in ("n_hit", "n_miss", "n_error", "n_queried", "n_tested", "error_rate")},
            "ctrl": {k: r_ctrl[k] for k in ("n_hit", "n_miss", "n_error", "n_queried", "n_tested", "error_rate")},
            "decision": r_dec,
        }

    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_decision(payload)
    print(f"verdict={decision['verdict']} reason={decision.get('reason')}")
    print(f"wrote {RESULT}")
    print(f"wrote {DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
