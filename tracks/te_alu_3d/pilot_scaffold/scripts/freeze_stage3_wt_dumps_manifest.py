"""Stage-3 WT dumps manifest freeze.

Creates a content-hash manifest of the 8 existing juicer_tools dump files,
the baseline result JSON, and the freeze JSON, pinning their exact state
before the bg_tol_bins=0 sensitivity run.

Outputs (written to 09_outputs/prospective/):
  stage3_wt_dumps_manifest_v1.json         — manifest with all sha256 hashes
  stage3_wt_dumps_manifest_v1.json.sha256  — hash of the manifest itself

Safety:
  - Verifies freeze JSON against its existing .sha256 sidecar before proceeding.
  - Asserts the sensitivity CLAIM file exists (ordering guarantee).
  - Rejects any path containing 'holdout'.
  - Raises FileNotFoundError if any of the 8 expected dump files is missing.

Must be run AFTER writing the sensitivity CLAIM and BEFORE executing the runner.

Usage:
  python freeze_stage3_wt_dumps_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"
FREEZE_JSON = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json"
FREEZE_HASH = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json.sha256"
DUMP_DIR = PROSPECTIVE / "g4a_stage3_architecture_wt_dumps"
BASELINE_JSON = PROSPECTIVE / "stage3_architecture_wt_contact_v1.json"
CLAIM_FILE = (
    PROSPECTIVE / "G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_CLAIM_v1.md"
)
MANIFEST_JSON = PROSPECTIVE / "stage3_wt_dumps_manifest_v1.json"
MANIFEST_HASH = PROSPECTIVE / "stage3_wt_dumps_manifest_v1.json.sha256"

# Canonical names for all 8 dump files (2 slots × 2 resolutions × 2 types)
EXPECTED_DUMPS: list[str] = [
    "ARCH_01_A754_obs_KR_10kb.txt",
    "ARCH_01_A754_oe_KR_10kb.txt",
    "ARCH_01_A754_obs_KR_25kb.txt",
    "ARCH_01_A754_oe_KR_25kb.txt",
    "ARCH_02_A518_obs_KR_10kb.txt",
    "ARCH_02_A518_oe_KR_10kb.txt",
    "ARCH_02_A518_obs_KR_25kb.txt",
    "ARCH_02_A518_oe_KR_25kb.txt",
]


def sha256_file(path: Path) -> str:
    """Return lowercase SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_holdout_path(path: Path) -> None:
    """Raise RuntimeError if path contains the literal string 'holdout'."""
    if "holdout" in str(path).lower():
        raise RuntimeError(f"FORBIDDEN: holdout path accessed: {path}")


def verify_freeze_hash() -> dict:
    """Verify freeze JSON against its .sha256 sidecar and return parsed content."""
    if not FREEZE_JSON.exists():
        raise FileNotFoundError(f"Freeze JSON not found: {FREEZE_JSON}")
    if not FREEZE_HASH.exists():
        raise FileNotFoundError(f"Freeze hash not found: {FREEZE_HASH}")
    expected = FREEZE_HASH.read_text(encoding="utf-8").strip()
    actual = hashlib.sha256(FREEZE_JSON.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(
            f"Freeze JSON hash mismatch!\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n"
            f"Re-run freeze_stage3_architecture_anchors.py to regenerate."
        )
    return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))


def main() -> None:
    print("=== Stage-3 WT Dumps Manifest Freeze ===")

    # Gate: CLAIM must exist before manifest is created
    if not CLAIM_FILE.exists():
        print(
            f"[ERROR] Sensitivity CLAIM not found — write the CLAIM first:\n"
            f"  {CLAIM_FILE}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"[OK] CLAIM present: {CLAIM_FILE.name}")

    # Holdout guard on all paths
    for p in [FREEZE_JSON, DUMP_DIR, BASELINE_JSON, MANIFEST_JSON]:
        reject_holdout_path(p)

    # Step 1: verify freeze
    print("\n[Step 1] Verifying freeze hash …")
    freeze = verify_freeze_hash()
    freeze_sha256 = FREEZE_HASH.read_text(encoding="utf-8").strip()
    print(f"         freeze: {FREEZE_JSON.name}")
    print(f"         Ensembl release: {freeze.get('ensembl_release')}")
    print(f"         frozen_at: {freeze.get('frozen_at')}")

    # Step 2: verify baseline result JSON
    print("\n[Step 2] Verifying baseline result JSON …")
    if not BASELINE_JSON.exists():
        print(
            f"[ERROR] Baseline result JSON not found: {BASELINE_JSON}", file=sys.stderr
        )
        sys.exit(1)
    baseline_sha256 = sha256_file(BASELINE_JSON)
    print(f"         {BASELINE_JSON.name}: {baseline_sha256[:16]}…")

    # Step 3: hash all 8 dump files
    print("\n[Step 3] Hashing dump files …")
    if not DUMP_DIR.exists():
        print(f"[ERROR] Dump directory not found: {DUMP_DIR}", file=sys.stderr)
        sys.exit(1)
    dump_sha256: dict[str, str] = {}
    for name in EXPECTED_DUMPS:
        p = DUMP_DIR / name
        reject_holdout_path(p)
        if not p.exists():
            print(f"[ERROR] Expected dump file missing: {p}", file=sys.stderr)
            sys.exit(1)
        if p.stat().st_size < 5:
            print(f"[ERROR] Dump file appears empty: {p}", file=sys.stderr)
            sys.exit(1)
        digest = sha256_file(p)
        dump_sha256[name] = digest
        print(f"  {name}: {digest[:16]}…  ({p.stat().st_size:,} bytes)")

    # Step 4: hash the CLAIM file itself
    claim_sha256 = sha256_file(CLAIM_FILE)
    print(f"\n[Step 4] CLAIM sha256: {claim_sha256[:16]}…")

    # Step 5: write manifest
    print("\n[Step 5] Writing manifest …")
    payload: dict = {
        "manifest_version": "stage3_wt_dumps_manifest_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Content-hash manifest created BEFORE bg_tol_bins=0 sensitivity run. "
            "Sensitivity runner must verify all hashes before proceeding."
        ),
        "freeze_json": FREEZE_JSON.name,
        "freeze_sha256": freeze_sha256,
        "baseline_result_json": BASELINE_JSON.name,
        "baseline_result_sha256": baseline_sha256,
        "sensitivity_claim": CLAIM_FILE.name,
        "sensitivity_claim_sha256": claim_sha256,
        "dump_dir": DUMP_DIR.name,
        "dump_sha256": dump_sha256,
    }
    MANIFEST_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    manifest_digest = hashlib.sha256(MANIFEST_JSON.read_bytes()).hexdigest()
    MANIFEST_HASH.write_text(manifest_digest + "\n", encoding="utf-8")

    print(f"\n[OK] Manifest written:  {MANIFEST_JSON.name}")
    print(f"[OK] Manifest SHA256:   {manifest_digest}")
    print("\nNext: run  python run_stage3_architecture_wt_contact_bgtol0.py")


if __name__ == "__main__":
    main()
