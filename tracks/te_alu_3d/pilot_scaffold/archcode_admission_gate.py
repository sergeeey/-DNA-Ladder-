"""ARCHCODE (or primary) admission gate — must PASS before confirmatory freeze.

Usage:
  python archcode_admission_gate.py
  python archcode_admission_gate.py --out ../09_outputs/pilot_chr11/archcode_admission.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "score_freeze.yaml"
DEFAULT_OUT = ROOT.parent / "09_outputs" / "pilot_chr11" / "archcode_admission.json"


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def evaluate(freeze_path: Path = FREEZE) -> dict[str, Any]:
    with freeze_path.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    sf = doc.get("score_freeze") or {}
    primary = sf.get("primary_model") or {}
    exploratory = sf.get("exploratory_scorer") or {}

    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "pass": ok, "detail": detail})

    binary = primary.get("binary_path")
    bin_path = Path(binary) if binary else None
    available = bool(bin_path and bin_path.exists())
    add(
        "binary_present",
        available,
        f"binary_path={binary!r} exists={available}",
    )
    add(
        "available_in_workspace_flag",
        bool(primary.get("available_in_workspace")) and available,
        f"flag={primary.get('available_in_workspace')}",
    )
    add(
        "version_set",
        bool(primary.get("version")),
        f"version={primary.get('version')!r}",
    )
    add(
        "binary_hash_set",
        bool(primary.get("binary_hash")),
        f"binary_hash={primary.get('binary_hash')!r}",
    )
    add(
        "config_hash_set",
        bool(primary.get("config_hash")),
        f"config_hash={primary.get('config_hash')!r}",
    )
    add(
        "input_schema_version_set",
        bool(primary.get("input_schema_version")),
        f"schema={primary.get('input_schema_version')!r}",
    )

    # Provenance / leakage checklist (documented fields; fail if missing when binary present)
    provenance_note = ROOT.parent / "07_methods" / "archcode_admission_checklist.md"
    add(
        "admission_checklist_doc",
        provenance_note.exists(),
        f"path={provenance_note}",
    )

    # Independent scorer path: exploratory may stay active, but confirmatory blocked
    exploratory_ok = (
        exploratory.get("benchmark_status") == "PASS"
        and exploratory.get("confirmatory_status") == "exploratory"
    )
    add(
        "exploratory_scorer_not_promoted",
        exploratory_ok,
        f"benchmark={exploratory.get('benchmark_status')} "
        f"confirmatory_status={exploratory.get('confirmatory_status')}",
    )

    freeze_status = sf.get("status")
    add(
        "not_yet_confirmatory_frozen",
        freeze_status != "CONFIRMATORY_FROZEN",
        f"score_freeze.status={freeze_status}",
    )

    if available and bin_path is not None:
        digest = _sha256(bin_path)
        recorded = primary.get("binary_hash")
        add(
            "binary_hash_matches",
            bool(recorded) and digest == recorded,
            f"computed={digest} recorded={recorded}",
        )

    passed = all(c["pass"] for c in checks if c["check"] != "not_yet_confirmatory_frozen")
    # Admission requires primary ready; exploratory-only is FAIL for confirmatory
    primary_ready = all(
        c["pass"]
        for c in checks
        if c["check"]
        in {
            "binary_present",
            "available_in_workspace_flag",
            "version_set",
            "binary_hash_set",
            "config_hash_set",
            "input_schema_version_set",
            "admission_checklist_doc",
        }
    )
    if available:
        primary_ready = primary_ready and all(
            c["pass"] for c in checks if c["check"] == "binary_hash_matches"
        )

    verdict = "PASS" if primary_ready else "FAIL"
    return {
        "verdict": verdict,
        "meaning": (
            "ARCHCODE (or primary) admitted for confirmatory freeze path"
            if verdict == "PASS"
            else "Primary scorer NOT admitted — confirmatory enrichment FORBIDDEN"
        ),
        "active_exploratory_scorer": exploratory.get("name"),
        "checks": checks,
        "action_if_fail": [
            "Keep EXPLORATORY_FROZEN",
            "Do not unblind holdout for confirmatory claim",
            "Either supply ARCHCODE binary+provenance OR register a second validated scorer type",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = evaluate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    (args.out.parent / "archcode_admission_pass_fail.txt").write_text(
        result["verdict"] + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
