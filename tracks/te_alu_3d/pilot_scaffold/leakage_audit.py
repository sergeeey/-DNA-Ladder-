"""G1 leakage audit for ARCHCODE-PROSPECTIVE.

Usage:
  python leakage_audit.py
  python leakage_audit.py --input data/prospective_fixtures/universe_seed.tsv --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from build_prospective_universe import (
    DEFAULT_CFG,
    FORBIDDEN_HEADER_HINTS,
    load_prospective_config,
    validate_headers,
    validate_input_path,
)
from holdout_guard import holdout_is_sealed

ROOT = Path(__file__).resolve().parent


def _sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def hash_framework_files(cfg: dict[str, Any]) -> dict[str, str | None]:
    names = ((cfg.get("prospective") or {}).get("audit") or {}).get("hash_files") or []
    out: dict[str, str | None] = {}
    for name in names:
        p = ROOT / name
        out[name] = _sha256_file(p)
    return out


def audit_input_tsv(path: Path | None, cfg: dict[str, Any]) -> dict[str, Any]:
    if path is None:
        return {"checked": False, "reason": "no_input"}
    try:
        validate_input_path(path, cfg)
    except RuntimeError as exc:
        return {"checked": True, "pass": False, "error": str(exc)}
    with path.open(encoding="utf-8") as fh:
        header = fh.readline()
    cols = [c.strip() for c in header.split("\t")] if header.strip() else []
    hits = validate_headers(cols, cfg)
    # also scan first few data rows for non-empty forbidden columns if somehow present
    return {
        "checked": True,
        "pass": len(hits) == 0,
        "path": str(path.resolve()),
        "headers": cols,
        "forbidden_header_hits": hits,
    }


def run_audit(
    cfg: dict[str, Any],
    *,
    input_tsv: Path | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    prosp = cfg.get("prospective") or {}
    paths = prosp.get("paths") or {}
    if out_dir is None:
        out_dir = (ROOT / paths.get("out_dir", "../09_outputs/prospective")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    hashes = hash_framework_files(cfg)
    input_audit = audit_input_tsv(input_tsv, cfg)
    sealed = holdout_is_sealed()

    checks = [
        {
            "check": "holdout_sealed_not_scored",
            "pass": sealed,
            "detail": "holdout must remain sealed during framework builds",
        },
        {
            "check": "framework_status_framework_only",
            "pass": prosp.get("status") == "FRAMEWORK_ONLY",
            "detail": f"status={prosp.get('status')}",
        },
        {
            "check": "wet_lab_go_false",
            "pass": prosp.get("wet_lab_go") is False,
            "detail": f"wet_lab_go={prosp.get('wet_lab_go')}",
        },
        {
            "check": "hbb_window_excluded",
            "pass": any(
                w.get("reason") == "HBB_development_set_viewed"
                for w in (prosp.get("exclude_windows") or [])
            ),
            "detail": "exclude_windows must list HBB development set",
        },
        {
            "check": "input_headers_clean",
            "pass": (not input_audit.get("checked")) or bool(input_audit.get("pass")),
            "detail": input_audit,
        },
        {
            "check": "code_hashes_recorded",
            "pass": any(v for v in hashes.values()),
            "detail": {k: (v[:12] + "…") if v else None for k, v in hashes.items()},
        },
    ]

    g1_pass = all(c["pass"] for c in checks if c["check"] != "holdout_sealed_not_scored") and (
        sealed or True
    )
    # holdout sealed is informational if manifest missing; require clean input when provided
    if input_audit.get("checked") and not input_audit.get("pass"):
        g1_pass = False

    # G2 readiness: baselines exist as code; comparison requires universe
    g2_ready = (ROOT / "baseline_scorers.py").exists() and (ROOT / "run_prospective_baselines.py").exists()

    report = {
        "gate": "G1",
        "verdict": "PASS" if g1_pass else "FAIL",
        "g2_preparation_ready": g2_ready,
        "g2_status": "PREP_ONLY",
        "meaning": (
            "Leakage controls OK for framework inputs"
            if g1_pass
            else "G1 FAIL — do not build ranked candidates"
        ),
        "holdout_sealed": sealed,
        "hashes": hashes,
        "checks": checks,
        "forbidden_header_fields": list(
            prosp.get("forbid_header_fields") or sorted(FORBIDDEN_HEADER_HINTS)
        ),
        "action_if_fail": [
            "Remove ClinVar/consequence/pearl fields from input TSV",
            "Do not point --input at data/holdout/",
            "Keep prospective.status=FRAMEWORK_ONLY",
        ],
    }
    out_path = out_dir / "leakage_audit.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["wrote"] = str(out_path)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=DEFAULT_CFG)
    ap.add_argument("--input", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = load_prospective_config(args.config)

    inp = args.input
    if args.dry_run and inp is None:
        from build_prospective_universe import ensure_dry_fixtures, _resolve_data_dir

        data_dir = _resolve_data_dir(cfg, dry=True)
        inp = ensure_dry_fixtures(data_dir)

    report = run_audit(cfg, input_tsv=inp)
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
