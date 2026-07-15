"""Admission gate for a non-PWM second scorer type.

ARCHCODE remains preferred primary. This gate admits an alternative
(e.g. AlphaGenome) only when artifacts exist — never promotes PWM v1.1.

Usage:
  python second_scorer_admission_gate.py
  python second_scorer_admission_gate.py --type alphagenome_variant_contact
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "score_freeze.yaml"
SPEC = ROOT.parent / "07_methods" / "second_scorer_type_spec.md"
OUT = ROOT.parent / "09_outputs" / "pilot_chr11" / "second_scorer_admission.json"

ALLOWED_TYPES = {
    "archcode_disruption",
    "alphagenome_variant_contact",
    "unichrom_or_hicompass_allele_delta",
}
FORBIDDEN_AS_PRIMARY = {"ctcf_pwm_delta_v1", "ctcf_pwm_delta_v1.1", "motif_only", "distance_only"}


def evaluate(scorer_type: str) -> dict[str, Any]:
    with FREEZE.open(encoding="utf-8") as fh:
        freeze = (yaml.safe_load(fh) or {}).get("score_freeze") or {}
    primary = freeze.get("primary_model") or {}
    exploratory = freeze.get("exploratory_scorer") or {}

    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "pass": ok, "detail": detail})

    add("type_allowed", scorer_type in ALLOWED_TYPES, f"type={scorer_type}")
    add(
        "not_pwm_promoted",
        exploratory.get("name") not in FORBIDDEN_AS_PRIMARY
        or freeze.get("status") != "CONFIRMATORY_FROZEN",
        f"exploratory={exploratory.get('name')} freeze_status={freeze.get('status')}",
    )
    add("spec_doc_present", SPEC.exists(), str(SPEC))

    if scorer_type == "archcode_disruption":
        binary = primary.get("binary_path")
        bin_ok = bool(binary and Path(binary).exists())
        add("archcode_binary", bin_ok, f"path={binary!r}")
        add("archcode_version", bool(primary.get("version")), str(primary.get("version")))
        add("archcode_hash", bool(primary.get("binary_hash")), str(primary.get("binary_hash")))
        ready = bin_ok and bool(primary.get("version")) and bool(primary.get("binary_hash"))
    elif scorer_type == "alphagenome_variant_contact":
        adapter = ROOT / "adapters" / "alphagenome_adapter.py"
        smoke = ROOT.parent / "09_outputs" / "pilot_chr11" / "alphagenome_smoke.json"
        add("adapter_present", adapter.exists(), str(adapter))
        add("smoke_run_pass", smoke.exists() and _smoke_ok(smoke), str(smoke))
        ready = adapter.exists() and smoke.exists() and _smoke_ok(smoke)
    else:
        add(
            "allele_delta_protocol",
            False,
            "UniChrom/Hi-Compass allele-delta mode not validated in-repo",
        )
        ready = False

    add(
        "exploratory_pwm_not_confirmatory",
        exploratory.get("confirmatory_status") == "exploratory",
        str(exploratory.get("confirmatory_status")),
    )

    # Hard forbid: declaring confirmatory while only PWM exists
    pwm_only = not ready
    verdict = "PASS" if ready and scorer_type in ALLOWED_TYPES else "FAIL"
    return {
        "verdict": verdict,
        "scorer_type": scorer_type,
        "ready_for_confirmatory_primary": ready and verdict == "PASS",
        "pwm_v1_1_may_be_confirmatory": False,
        "checks": checks,
        "meaning": (
            "Second/alternative primary admitted"
            if verdict == "PASS"
            else "No non-PWM primary available — confirmatory still FORBIDDEN"
        ),
        "action_if_fail": [
            "Supply ARCHCODE binary + hashes, or",
            "Run AlphaGenome smoke via adapters/alphagenome_adapter.py with credentials, or",
            "Validate UniChrom/Hi-Compass allele-delta protocol",
            "Do NOT promote ctcf_pwm_delta_v1.1 to confirmatory",
        ],
        "pwm_only_environment": pwm_only,
    }


def _smoke_ok(path: Path) -> bool:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return doc.get("status") == "PASS"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--type",
        default="archcode_disruption",
        choices=sorted(ALLOWED_TYPES),
    )
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    result = evaluate(args.type)
    # Also evaluate AlphaGenome path for the joint report
    joint = {
        "archcode_disruption": evaluate("archcode_disruption"),
        "alphagenome_variant_contact": evaluate("alphagenome_variant_contact"),
        "unichrom_or_hicompass_allele_delta": evaluate("unichrom_or_hicompass_allele_delta"),
        "selected": result,
        "overall_confirmatory_primary": "UNAVAILABLE",
    }
    if any(evaluate(t)["verdict"] == "PASS" for t in ALLOWED_TYPES):
        joint["overall_confirmatory_primary"] = "AVAILABLE"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(joint, indent=2), encoding="utf-8")
    (args.out.parent / "second_scorer_admission_pass_fail.txt").write_text(
        joint["overall_confirmatory_primary"] + "\n", encoding="utf-8"
    )
    print(json.dumps(joint, indent=2))
    return 0 if joint["overall_confirmatory_primary"] == "AVAILABLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
