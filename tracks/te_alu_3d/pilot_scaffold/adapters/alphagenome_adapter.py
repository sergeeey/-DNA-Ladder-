"""AlphaGenome adapter — live smoke + thin predict wrapper.

Usage:
  set ALPHAGENOME_API_KEY=...
  python adapters/alphagenome_adapter.py --smoke

Never scores holdout paths. Never writes the API key to disk.
Never claims confirmatory status from smoke alone.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "09_outputs" / "pilot_chr11" / "alphagenome_smoke.json"

# Public DeepMind README demo variant (not our holdout / not HBB labels).
_SMOKE_VARIANT = {
    "chromosome": "chr22",
    "position": 36201698,
    "reference_bases": "A",
    "alternate_bases": "C",
}


def _holdout_guard(path: Path) -> None:
    if "holdout" in path.parts:
        raise RuntimeError(f"Refusing AlphaGenome on holdout path: {path}")


def _client_version() -> str:
    try:
        import alphagenome

        return str(getattr(alphagenome, "__version__", "unknown"))
    except Exception:
        return "not_installed"


def smoke(force_mock: bool = False) -> dict:
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from load_project_env import alphagenome_api_key, load_project_env

    load_project_env()
    api_key = alphagenome_api_key()
    checkpoint = os.environ.get("ALPHAGENOME_CHECKPOINT")
    has_creds = bool(api_key or (checkpoint and Path(checkpoint).exists()))
    pkg_ver = _client_version()

    base = {
        "adapter": "alphagenome_adapter",
        "has_api_key": bool(api_key),
        "checkpoint_set": bool(checkpoint),
        "client_package_version": pkg_ver,
        "confirmatory": False,
        "scored_holdout": False,
        "smoke_variant": _SMOKE_VARIANT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if force_mock or not has_creds:
        return {
            **base,
            "status": "FAIL",
            "mode": "stub",
            "reason": "no_credentials_or_checkpoint",
            "next": [
                "Set ALPHAGENOME_API_KEY (https://deepmind.google.com/science/alphagenome)",
                "Re-run --smoke until status=PASS",
                "Then second_scorer_admission_gate.py --type alphagenome_variant_contact",
            ],
        }

    if not api_key:
        return {
            **base,
            "status": "FAIL",
            "mode": "checkpoint_only_not_wired",
            "reason": "local checkpoint path set but self-host path not implemented; use API key",
        }

    try:
        from alphagenome.data import genome
        from alphagenome.models import dna_client
    except ImportError as exc:
        return {
            **base,
            "status": "FAIL",
            "mode": "import_error",
            "reason": f"pip install alphagenome failed/import: {exc}",
        }

    try:
        model = dna_client.create(api_key)
        variant = genome.Variant(**_SMOKE_VARIANT)
        # Contact maps need a wide window; 1MB matches API docs for variant demos.
        interval = variant.reference_interval.resize(dna_client.SEQUENCE_LENGTH_1MB)
        outputs = model.predict_variant(
            interval=interval,
            variant=variant,
            organism=dna_client.Organism.HOMO_SAPIENS,
            requested_outputs=[
                dna_client.OutputType.CONTACT_MAPS,
                dna_client.OutputType.CHIP_TF,
            ],
            ontology_terms=None,
        )
        ref_cm = getattr(outputs.reference, "contact_maps", None)
        alt_cm = getattr(outputs.alternate, "contact_maps", None)
        ref_tf = getattr(outputs.reference, "chip_tf", None)
        contact_ok = ref_cm is not None and alt_cm is not None
        if not contact_ok:
            return {
                **base,
                "status": "FAIL",
                "mode": "live_api",
                "reason": "predict_variant returned without CONTACT_MAPS",
                "has_chip_tf": ref_tf is not None,
            }
        return {
            **base,
            "status": "PASS",
            "mode": "live_api",
            "reason": "predict_variant CONTACT_MAPS+CHIP_TF ok on public demo variant",
            "outputs_present": {
                "contact_maps_ref": True,
                "contact_maps_alt": True,
                "chip_tf_ref": ref_tf is not None,
            },
            "interval_width_bp": int(interval.end - interval.start),
            "next": [
                "second_scorer_admission_gate.py --type alphagenome_variant_contact",
                "Do NOT score sealed holdout until unblind + freezes",
                "Confirmatory_FROZEN still needs planted/benchmark + leakage policy",
            ],
        }
    except Exception as exc:
        return {
            **base,
            "status": "FAIL",
            "mode": "live_api_error",
            "reason": f"{type(exc).__name__}: {exc}",
            "next": [
                "Verify API key at https://deepmind.google.com/science/alphagenome",
                "Confirm non-commercial Terms acceptance",
                "Retry --smoke",
            ],
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", required=True)
    ap.add_argument("--force-mock", action="store_true")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    _holdout_guard(args.out)
    result = smoke(force_mock=args.force_mock)
    # Hard guarantee: never persist secrets
    assert "AIza" not in json.dumps(result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
