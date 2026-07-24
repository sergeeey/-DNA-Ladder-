"""Stage-3 Architecture WT contact sensitivity — bg_tol_bins=0 (exact-distance background).

Post-analysis advisory side-car for G4a_stage3_architecture_wt_contact_CLAIM_v1.md.
See CLAIM: G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_CLAIM_v1.md

Does NOT:
  - Call juicer_tools / Java (reads existing dump files only; no subprocess)
  - Access network / Ensembl REST (no urllib / requests)
  - Modify or overwrite the main result/decision files
  - Access holdout paths

Does:
  - Verify freeze hash → manifest hash → CLAIM hash → 8 dump hashes → baseline JSON pin
  - For each (slot, resolution): apply same-bin guard, then analyze_contact(bg_tol_bins=0)
  - Score with score_resolution / sample_verdict (thresholds unchanged from parent claim)
  - Classify score transitions vs bg_tol_bins=1 baseline
  - Write advisory-only sensitivity result JSON + decision MD

Outputs (in 09_outputs/prospective/):
  stage3_architecture_wt_contact_bgtol0_sensitivity_v1.json
  G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_decision_v1.md

Usage:
  python run_stage3_architecture_wt_contact_bgtol0.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))
from hic_contact_lib import (  # noqa: E402
    analyze_contact,
    bin_of,
    sample_verdict,
    score_resolution,
)

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"
FREEZE_JSON = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json"
FREEZE_HASH = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json.sha256"
MANIFEST_JSON = PROSPECTIVE / "stage3_wt_dumps_manifest_v1.json"
MANIFEST_HASH = PROSPECTIVE / "stage3_wt_dumps_manifest_v1.json.sha256"
BASELINE_JSON = PROSPECTIVE / "stage3_architecture_wt_contact_v1.json"
CLAIM_MD = (
    PROSPECTIVE
    / "G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_CLAIM_v1.md"
)
DUMP_DIR = PROSPECTIVE / "g4a_stage3_architecture_wt_dumps"
OUT_JSON = PROSPECTIVE / "stage3_architecture_wt_contact_bgtol0_sensitivity_v1.json"
OUT_MD = (
    PROSPECTIVE / "G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_decision_v1.md"
)

SEALED_CHR_HG19 = "11"
SEALED_START_HG19 = 64_000_000
SEALED_END_HG19 = 68_000_000

BG_TOL_BINS = 0
RESOLUTIONS = [10_000, 25_000]


class SameBinGuardError(RuntimeError):
    """Raised when E_mid_bin == P_mid_bin and bg_tol_bins=0 is requested.

    A diagonal (dist=0) background pool cannot serve as a same-distance
    reference for an E–P pair; the computation is undefined.
    """


# ---------------------------------------------------------------------------
# Safety guards
# ---------------------------------------------------------------------------


def _reject_holdout_path(path: Path) -> None:
    if "holdout" in str(path).lower():
        raise RuntimeError(f"FORBIDDEN: holdout path accessed: {path}")


def _reject_sealed_region(chrom: str, start: int, end: int) -> None:
    if chrom == SEALED_CHR_HG19 and start < SEALED_END_HG19 and end > SEALED_START_HG19:
        raise RuntimeError(
            f"FORBIDDEN: region chr{chrom}:{start}-{end} overlaps sealed interval "
            f"chr{SEALED_CHR_HG19}:{SEALED_START_HG19}-{SEALED_END_HG19}"
        )


# ---------------------------------------------------------------------------
# Hash verification
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze_hash() -> dict:
    """Verify freeze JSON against its .sha256 sidecar and return parsed content."""
    if not FREEZE_JSON.exists():
        raise FileNotFoundError(f"Freeze JSON not found: {FREEZE_JSON}")
    if not FREEZE_HASH.exists():
        raise FileNotFoundError(f"Freeze hash not found: {FREEZE_HASH}")
    expected = FREEZE_HASH.read_text(encoding="utf-8").strip()
    actual = _sha256_file(FREEZE_JSON)
    if actual != expected:
        raise RuntimeError(
            f"Freeze JSON hash mismatch!\n  expected: {expected}\n  actual: {actual}"
        )
    return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))


def verify_manifest_hash() -> dict:
    """Verify manifest JSON against its .sha256 sidecar and return parsed content."""
    if not MANIFEST_JSON.exists():
        raise FileNotFoundError(
            f"Manifest not found: {MANIFEST_JSON}\n"
            "Run freeze_stage3_wt_dumps_manifest.py first."
        )
    if not MANIFEST_HASH.exists():
        raise FileNotFoundError(f"Manifest hash not found: {MANIFEST_HASH}")
    expected = MANIFEST_HASH.read_text(encoding="utf-8").strip()
    actual = _sha256_file(MANIFEST_JSON)
    if actual != expected:
        raise RuntimeError(
            f"Manifest hash mismatch!\n  expected: {expected}\n  actual: {actual}"
        )
    return json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))


def verify_dump_hashes(manifest: dict) -> None:
    """Verify all 8 dump files against hashes recorded in the manifest."""
    recorded: dict[str, str] = manifest.get("dump_sha256", {})
    for name, expected_digest in recorded.items():
        p = DUMP_DIR / name
        _reject_holdout_path(p)
        if not p.exists():
            raise FileNotFoundError(f"Dump file missing: {p}")
        actual = _sha256_file(p)
        if actual != expected_digest:
            raise RuntimeError(
                f"Dump file hash mismatch for {name}!\n"
                f"  manifest: {expected_digest}\n"
                f"  on disk:  {actual}\n"
                "The dump files have changed since the manifest was created."
            )


def verify_baseline_hash(manifest: dict) -> dict:
    """Verify baseline result JSON hash matches manifest pin and return parsed content."""
    expected = manifest.get("baseline_result_sha256", "")
    if not expected:
        raise RuntimeError("Manifest does not contain baseline_result_sha256.")
    if not BASELINE_JSON.exists():
        raise FileNotFoundError(f"Baseline result JSON not found: {BASELINE_JSON}")
    actual = _sha256_file(BASELINE_JSON)
    if actual != expected:
        raise RuntimeError(
            f"Baseline result JSON hash changed since manifest!\n"
            f"  manifest pin: {expected}\n"
            f"  on disk:      {actual}\n"
            "Do not modify the baseline result between manifest creation and sensitivity run."
        )
    return json.loads(BASELINE_JSON.read_text(encoding="utf-8"))


def verify_claim_hash(manifest: dict) -> None:
    """Verify the locked sensitivity CLAIM against its manifest pin."""
    expected = manifest.get("sensitivity_claim_sha256", "")
    if not expected:
        raise RuntimeError("Manifest does not contain sensitivity_claim_sha256.")
    if manifest.get("sensitivity_claim") != CLAIM_MD.name:
        raise RuntimeError("Manifest sensitivity_claim does not match the locked CLAIM path.")
    if not CLAIM_MD.exists():
        raise FileNotFoundError(f"Sensitivity CLAIM not found: {CLAIM_MD}")
    actual = _sha256_file(CLAIM_MD)
    if actual != expected:
        raise RuntimeError(
            "Sensitivity CLAIM hash changed since manifest!\n"
            f"  manifest pin: {expected}\n"
            f"  on disk:      {actual}"
        )


def verify_manifest_freeze_pin(manifest: dict, freeze_sha256: str) -> None:
    """Require the dump manifest to pin the current frozen anchors."""
    if manifest.get("freeze_sha256") != freeze_sha256:
        raise RuntimeError(
            "Manifest freeze_sha256 does not match the current frozen anchors."
        )


def assert_output_paths_safe() -> None:
    """Allow writes only to the two sensitivity side-car outputs."""
    allowed = {
        PROSPECTIVE / "stage3_architecture_wt_contact_bgtol0_sensitivity_v1.json",
        PROSPECTIVE
        / "G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_decision_v1.md",
    }
    if {OUT_JSON, OUT_MD} != allowed:
        raise RuntimeError("Unsafe output path: sensitivity runner may write only side-car outputs.")


# ---------------------------------------------------------------------------
# Score transition classifier
# ---------------------------------------------------------------------------


def classify_score_transition(old_score: str, new_score: str) -> str:
    """Classify the change from bg_tol_bins=1 score to bg_tol_bins=0 score.

    Returns one of:
      STABLE                   — old_score == new_score
      UPGRADED                 — new_score PASS, old_score non-PASS
      DOWNGRADED               — old_score PASS, new_score non-PASS
      CHANGED                  — any other non-stable transition
      SAME_BIN_BLOCKED_HARD_FAIL — new_score is SAME_BIN_GUARD_VIOLATION
    """
    if new_score == "SAME_BIN_GUARD_VIOLATION":
        return "SAME_BIN_BLOCKED_HARD_FAIL"
    if old_score == new_score:
        return "STABLE"
    if new_score == "PASS" and old_score != "PASS":
        return "UPGRADED"
    if old_score == "PASS" and new_score != "PASS":
        return "DOWNGRADED"
    return "CHANGED"


# ---------------------------------------------------------------------------
# Same-bin guard
# ---------------------------------------------------------------------------


def check_same_bin_guard(
    e_anchor: tuple[int, int],
    p_anchor: tuple[int, int],
    binsize: int,
) -> None:
    """Raise SameBinGuardError if E_mid_bin == P_mid_bin.

    With bg_tol_bins=0 and distance=0, the background pool degenerates to
    diagonal pixels, which is not a valid same-distance E–P reference.
    """
    e_mid = bin_of((e_anchor[0] + e_anchor[1]) // 2, binsize)
    p_mid = bin_of((p_anchor[0] + p_anchor[1]) // 2, binsize)
    if e_mid == p_mid:
        raise SameBinGuardError(
            f"HARD-FAIL: E_mid_bin == P_mid_bin == {e_mid} at binsize={binsize}. "
            "bg_tol_bins=0 on a same-bin pair produces a diagonal-only background; "
            "computation blocked."
        )


# ---------------------------------------------------------------------------
# Per-slot sensitivity analysis
# ---------------------------------------------------------------------------


def _lookup_baseline_slot(baseline: dict, slot_id: str) -> dict | None:
    """Return the baseline slot result dict for slot_id, or None if not found."""
    for s in baseline.get("slots", []):
        if s.get("slot_id") == slot_id:
            return s
    return None


def analyze_slot_bgtol0(
    freeze_slot: dict,
    baseline_slot: dict | None,
) -> dict:
    """Run bg_tol_bins=0 sensitivity analysis for one frozen slot.

    Returns a result dict with per-resolution metrics, scores, transitions,
    and any guard violations.
    """
    slot_id = freeze_slot["slot_id"]
    candidate_id = freeze_slot["candidate_id"]
    variant = freeze_slot["variant"]

    result: dict = {
        "slot_id": slot_id,
        "candidate_id": candidate_id,
        "variant": variant,
        "bg_tol_bins": BG_TOL_BINS,
    }

    status = freeze_slot.get("status", "OK")
    if status != "OK":
        result["outcome"] = status
        result["note"] = f"Slot pre-reg status is {status}; no analysis performed."
        return result

    e37 = freeze_slot.get("E_grch37")
    p37 = freeze_slot.get("P_grch37")
    if not e37 or not p37:
        result["outcome"] = "BLOCKED_MISSING_HG19_COORDS"
        return result

    e_anchor = (e37["start"], e37["end"])
    p_anchor = (p37["start"], p37["end"])
    chrom = str(e37["chrom"])

    # Safety: no sealed region
    _reject_sealed_region(chrom, e37["start"], e37["end"])
    _reject_sealed_region(chrom, p37["start"], p37["end"])

    tag = f"{slot_id}_{candidate_id}"
    metrics_by_res: dict[int, dict] = {}
    scores_by_res: dict[int, str] = {}
    transitions: dict[int, dict] = {}

    for binsize in RESOLUTIONS:
        obs_path = DUMP_DIR / f"{tag}_obs_KR_{binsize // 1000}kb.txt"
        oe_path = DUMP_DIR / f"{tag}_oe_KR_{binsize // 1000}kb.txt"

        _reject_holdout_path(obs_path)
        _reject_holdout_path(oe_path)

        if not obs_path.exists() or not oe_path.exists():
            scores_by_res[binsize] = "FAIL"
            metrics_by_res[binsize] = {"error": "dump_file_missing"}
            old_score = (baseline_slot or {}).get(
                f"score_{binsize // 1000}kb", "UNKNOWN"
            )
            transitions[binsize] = {
                "old_score": old_score,
                "new_score": "FAIL",
                "transition": classify_score_transition(old_score, "FAIL"),
            }
            continue

        # Same-bin guard: must run BEFORE analyze_contact
        try:
            check_same_bin_guard(e_anchor, p_anchor, binsize)
        except SameBinGuardError as exc:
            guard_score = "SAME_BIN_GUARD_VIOLATION"
            scores_by_res[binsize] = guard_score
            metrics_by_res[binsize] = {
                "error": "same_bin_guard_violation",
                "message": str(exc),
            }
            old_score = (baseline_slot or {}).get(
                f"score_{binsize // 1000}kb", "UNKNOWN"
            )
            transitions[binsize] = {
                "old_score": old_score,
                "new_score": guard_score,
                "transition": classify_score_transition(old_score, guard_score),
            }
            continue

        focal_1based = (e37["start"] + e37["end"]) // 2
        m = analyze_contact(
            obs_path=obs_path,
            oe_path=oe_path,
            binsize=binsize,
            e_anchor=e_anchor,
            p_anchor=p_anchor,
            focal_row_coord=focal_1based,
            bg_tol_bins=BG_TOL_BINS,
        )
        score = score_resolution(m)
        metrics_by_res[binsize] = m
        scores_by_res[binsize] = score

        old_score = (baseline_slot or {}).get(f"score_{binsize // 1000}kb", "UNKNOWN")
        transition_label = classify_score_transition(old_score, score)

        # Compute metric deltas vs baseline (advisory only)
        baseline_m = (baseline_slot or {}).get(f"metrics_{binsize // 1000}kb") or {}
        delta: dict = {}
        for key in (
            "same_distance_bg_n",
            "enrich_mean",
            "obs_percentile",
            "primary_oe",
        ):
            old_val = baseline_m.get(key)
            new_val = m.get(key)
            if old_val is not None and new_val is not None:
                try:
                    delta[f"delta_{key}"] = round(float(new_val) - float(old_val), 6)
                except (TypeError, ValueError):
                    pass

        transitions[binsize] = {
            "old_score": old_score,
            "new_score": score,
            "transition": transition_label,
            **delta,
        }

    verdict = sample_verdict(
        res10=scores_by_res.get(10_000, "FAIL"),
        res25=scores_by_res.get(25_000, "FAIL"),
    )

    result.update(
        {
            "E_hg19": e37,
            "P_hg19": p37,
            "T_gene": freeze_slot.get("T_gene"),
            "metrics_10kb": metrics_by_res.get(10_000),
            "metrics_25kb": metrics_by_res.get(25_000),
            "score_10kb": scores_by_res.get(10_000, "FAIL"),
            "score_25kb": scores_by_res.get(25_000, "FAIL"),
            "transition_10kb": transitions.get(10_000, {}),
            "transition_25kb": transitions.get(25_000, {}),
            "outcome": verdict,
        }
    )
    return result


# ---------------------------------------------------------------------------
# Panel verdict
# ---------------------------------------------------------------------------


def panel_verdict(slot_results: list[dict]) -> str:
    """Combine sensitivity slot outcomes into a panel verdict (same logic as main runner)."""
    outcomes = [s.get("outcome", "INCONCLUSIVE") for s in slot_results]
    if any(o.startswith("BLOCKED") for o in outcomes):
        return "BLOCKED"
    if all(o == "PASS" for o in outcomes):
        return "SUPPORTED"
    if "PASS" in outcomes:
        return "PARTIAL"
    if all(o == "UNSUPPORTED" for o in outcomes):
        return "PANEL_UNSUPPORTED"
    return "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------


def _fmt_metric_delta(t: dict, key: str) -> str:
    delta_key = f"delta_{key}"
    v = t.get(delta_key)
    if v is None:
        return "n/a"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.4f}"


def write_sensitivity_decision(
    freeze: dict,
    manifest: dict,
    baseline: dict,
    slot_results: list[dict],
    pv: str,
    freeze_sha256: str,
    manifest_sha256: str,
    baseline_sha256: str,
) -> None:
    """Write advisory-only sensitivity decision Markdown."""
    run_at = datetime.now(timezone.utc).isoformat()

    # Transition summary table
    transition_rows: list[str] = []
    for s in slot_results:
        for res_label, res_key in [
            ("10 kb", "transition_10kb"),
            ("25 kb", "transition_25kb"),
        ]:
            t = s.get(res_key, {})
            row = (
                f"| {s['slot_id']} | {s['candidate_id']} | {res_label} | "
                f"`{t.get('old_score', 'n/a')}` | `{t.get('new_score', 'n/a')}` | "
                f"**{t.get('transition', 'n/a')}** | "
                f"{_fmt_metric_delta(t, 'same_distance_bg_n')} | "
                f"{_fmt_metric_delta(t, 'enrich_mean')} | "
                f"{_fmt_metric_delta(t, 'obs_percentile')} |"
            )
            transition_rows.append(row)

    transitions_section = "\n".join(transition_rows)

    # Per-slot detail blocks
    slot_blocks: list[str] = []
    for s in slot_results:
        t10 = s.get("transition_10kb", {})
        t25 = s.get("transition_25kb", {})
        m10 = s.get("metrics_10kb") or {}
        m25 = s.get("metrics_25kb") or {}

        def _fmt_m(m: dict, score: str) -> str:
            if "error" in m:
                return f"| error | {m.get('error')} |\n| message | {m.get('message', '')} |"
            return (
                f"| score (bg_tol=0) | `{score}` |\n"
                f"| primary_obs | {m.get('primary_obs')} |\n"
                f"| primary_oe | {m.get('primary_oe')} |\n"
                f"| bg_n (tol=0) | {m.get('same_distance_bg_n')} |\n"
                f"| enrich_mean | {m.get('enrich_mean')} |\n"
                f"| obs_percentile | {m.get('obs_percentile')} |\n"
                f"| focal_row_nonzero | {m.get('focal_row_nonzero')} |"
            )

        slot_blocks.append(
            f"""### {s["slot_id"]} — {s["candidate_id"]} ({s["variant"]})

**Sensitivity outcome (bg_tol_bins=0):** `{s.get("outcome", "unknown")}`

#### 10 kb

| metric | value |
|--------|-------|
{_fmt_m(m10, s.get("score_10kb", "n/a"))}

Transition: `{t10.get("old_score", "n/a")}` → `{t10.get("new_score", "n/a")}` — **{t10.get("transition", "n/a")}**

#### 25 kb

| metric | value |
|--------|-------|
{_fmt_m(m25, s.get("score_25kb", "n/a"))}

Transition: `{t25.get("old_score", "n/a")}` → `{t25.get("new_score", "n/a")}` — **{t25.get("transition", "n/a")}**
"""
        )

    slots_section = "\n".join(slot_blocks)

    md = f"""# Stage-3 Architecture WT Contact — bg_tol_bins=0 Sensitivity Decision

**Role:** Post-analysis advisory side-car; does NOT change the main panel verdict.
**Sensitivity CLAIM:** `G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_CLAIM_v1.md`
**Parent CLAIM / Decision:**
  `G4a_stage3_architecture_wt_contact_CLAIM_v1.md` (panel verdict **INCONCLUSIVE**)
  `G4a_stage3_architecture_wt_contact_decision_v1.md`
**Freeze:** `stage3_architecture_anchor_freeze_v1.json` (Ensembl {freeze.get("ensembl_release")};
  sha256 `{freeze_sha256[:16]}…`)
**Manifest:** `stage3_wt_dumps_manifest_v1.json` (sha256 `{manifest_sha256[:16]}…`)
**Baseline pin:** `stage3_architecture_wt_contact_v1.json` (sha256 `{baseline_sha256[:16]}…`)
**Analysis run:** {run_at}
**bg_tol_bins:** 0 (exact-distance background only)
**Advisory panel verdict (tol=0):** `{pv}`
**Main panel verdict (tol=1):** `INCONCLUSIVE` — **UNCHANGED**

---

## Score transition summary

| Slot | Candidate | Res | Score (tol=1) | Score (tol=0) | Transition | Δbg_n | Δenrich_mean | Δobs_pct |
|------|-----------|-----|--------------|--------------|-----------|-------|-------------|---------|
{transitions_section}

---

## Per-slot details

{slots_section}

---

## Interpretation constraints

- **This is an advisory-only sensitivity check.**
- The main panel verdict (**INCONCLUSIVE**) is unchanged.
- Stage-3 slot assignments remain LOCKED (see registry, 2026-07-15).
- No enhanced contact language is permitted from this result alone.
- NOT CLAIMED: enhancer–promoter contact, target-gene identity, allele effect, expression
  change, regulation, or pathogenicity.
- G4b allele ΔContact: NOT TESTED.
- Wet-lab: NO-GO (B0 UNSIGNED as of 2026-07-21).
- Single WT replicate; no independent replicate Hi-C available.

## Caveats

- Terminology in the locked parent claim is corrected by
  `G4_stage3_background_direction_ERRATUM_v1.md`: the mixed tol=1 pool
  inflated A754 enrichment in the observed parent matrix.
- A754 10 kb is the principal sensitivity finding: `PASS` at tol=1 becomes
  `FAIL` at exact distance because enrich_mean falls below 1.5. The original
  PASS is therefore background-definition-sensitive and must not be upgraded.
- A518 25 kb: `SAME_BIN_GUARD_VIOLATION` (E_mid == P_mid at 25 kb; diagonal background
  at bg_tol_bins=0 is undefined; computation hard-failed, consistent with parent UNRESOLVED_SAME_BIN).
- A754 25 kb: bg_n at tol=0 is much smaller than at tol=1 (only exact-distance pixels);
  result validity depends on bg_n remaining ≥ 20.
- Enrichment comparisons with tol=1 baseline are informational only; same-distance pool
  composition differs.
- hg19 coordinates derived from GRCh38 via Ensembl REST (same as parent claim).
- Architecture candidates; contact evidence alone does not confirm causal role.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"[OK] Sensitivity decision MD: {OUT_MD.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=== Stage-3 Architecture WT Contact — bg_tol_bins=0 Sensitivity ===")
    print(f"bg_tol_bins: {BG_TOL_BINS}  (exact-distance background)")
    assert_output_paths_safe()

    # Holdout guard on critical paths
    for p in [FREEZE_JSON, MANIFEST_JSON, BASELINE_JSON, DUMP_DIR, OUT_JSON, OUT_MD]:
        _reject_holdout_path(p)

    # Step 1: verify freeze hash
    print("\n[Step 1] Verifying freeze hash …")
    freeze = verify_freeze_hash()
    freeze_sha256 = FREEZE_HASH.read_text(encoding="utf-8").strip()
    print(f"         Ensembl release: {freeze.get('ensembl_release')}")
    print(f"         frozen_at: {freeze.get('frozen_at')}")

    # Step 2: verify manifest hash
    print("\n[Step 2] Verifying manifest hash …")
    manifest = verify_manifest_hash()
    manifest_sha256 = MANIFEST_HASH.read_text(encoding="utf-8").strip()
    verify_claim_hash(manifest)
    verify_manifest_freeze_pin(manifest, freeze_sha256)
    print(f"         created_at: {manifest.get('created_at')}")
    print(f"         sensitivity CLAIM: OK ({CLAIM_MD.name})")

    # Step 3: verify all 8 dump hashes
    print("\n[Step 3] Verifying dump file hashes (8 files) …")
    verify_dump_hashes(manifest)
    print(f"         All {len(manifest.get('dump_sha256', {}))} dump hashes verified.")

    # Step 4: verify baseline JSON pin
    print("\n[Step 4] Verifying baseline JSON pin …")
    baseline = verify_baseline_hash(manifest)
    baseline_sha256 = manifest["baseline_result_sha256"]
    print(
        f"         {BASELINE_JSON.name}: OK (baseline panel = {baseline.get('panel_verdict')})"
    )

    # Step 5: analyze slots
    print("\n[Step 5] Analyzing slots (bg_tol_bins=0, no Java/network) …")
    slot_results: list[dict] = []
    for freeze_slot in freeze.get("slots", []):
        sid = freeze_slot["slot_id"]
        cid = freeze_slot["candidate_id"]
        print(f"\n--- {sid} ({cid}) ---")
        baseline_slot = _lookup_baseline_slot(baseline, sid)
        r = analyze_slot_bgtol0(freeze_slot, baseline_slot)
        slot_results.append(r)
        print(f"    10 kb: {r.get('score_10kb')}  |  25 kb: {r.get('score_25kb')}")
        print(f"    outcome: {r.get('outcome')}")
        for res in [10_000, 25_000]:
            t = r.get(f"transition_{res // 1000}kb", {})
            if t:
                print(
                    f"    {res // 1000} kb transition: "
                    f"{t.get('old_score')} -> {t.get('new_score')} "
                    f"[{t.get('transition')}]"
                )

    pv = panel_verdict(slot_results)
    print(f"\n[Advisory panel verdict (tol=0)] {pv}")
    print("[Main panel verdict (tol=1)    ] INCONCLUSIVE  (unchanged)")

    # Step 6: write outputs
    payload: dict = {
        "analysis": "stage3_architecture_wt_contact_bgtol0_sensitivity_v1",
        "role": "post_analysis_advisory_sidecar",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "bg_tol_bins": BG_TOL_BINS,
        "freeze_json": FREEZE_JSON.name,
        "freeze_sha256": freeze_sha256,
        "manifest_json": MANIFEST_JSON.name,
        "manifest_sha256": manifest_sha256,
        "baseline_result_json": BASELINE_JSON.name,
        "baseline_result_sha256": baseline_sha256,
        "sample": "GSM4873113",
        "biosource": "HUDEP-2 WT",
        "norm": "KR",
        "main_panel_verdict": "INCONCLUSIVE",
        "advisory_panel_verdict_tol0": pv,
        "allele_effect": "NOT_TESTED",
        "g4b": "NOT_TESTED",
        "wet": "NO_GO",
        "slots": slot_results,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[OK] Sensitivity JSON: {OUT_JSON.name}")

    write_sensitivity_decision(
        freeze=freeze,
        manifest=manifest,
        baseline=baseline,
        slot_results=slot_results,
        pv=pv,
        freeze_sha256=freeze_sha256,
        manifest_sha256=manifest_sha256,
        baseline_sha256=baseline_sha256,
    )


if __name__ == "__main__":
    main()
