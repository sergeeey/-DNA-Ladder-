"""Refuse scoring holdout data while sealed."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT.parent / "07_methods" / "holdout_manifest.yaml"


def holdout_is_sealed() -> bool:
    if not MANIFEST.exists():
        return False
    with MANIFEST.open(encoding="utf-8") as fh:
        man = yaml.safe_load(fh) or {}
    h = man.get("holdout") or {}
    return h.get("status") == "SEALED" and not h.get("unblind_authorized", False)


def assert_not_scoring_holdout(path: Path | str) -> None:
    p = Path(path).resolve()
    if "holdout" in p.parts and holdout_is_sealed():
        raise RuntimeError(
            f"Holdout sealed — refusing to score {p}. "
            "Set holdout.unblind_authorized=true only after protocol note."
        )
