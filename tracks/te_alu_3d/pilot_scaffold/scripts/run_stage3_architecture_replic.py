"""Stage-3 Architecture Independent-Source Replication — G4c (GSE201820 noIAA).

Reads frozen anchors from stage3_architecture_anchor_freeze_v1.json,
runs juicer_tools dump against two remote .hic URLs (differentiated and
undifferentiated CTCF-AID noIAA HUDEP-2), analyzes contact using
hic_contact_lib.py with bg_tol_bins=0 (primary) and bg_tol_bins=1
(informational only, excluded from verdict).

Hash chain (fail-closed):
  anchor freeze hash → G4c CLAIM hash → eligibility freeze hash
  → preflight hash → dump hashes → result JSON

Safety guards (same as run_stage3_architecture_wt_contact.py):
  - Verifies all SHA256 hashes before any dump.
  - Rejects any path containing 'holdout'.
  - Rejects any dump region overlapping chr11:64–68 Mb (sealed, hg19).
  - Skips BLOCKED slots (no analysis, retains pre-reg outcome).
  - If any juicer_tools dump fails → BLOCKED (no fallback).

No-upgrade invariant: G4c verdict does not override G4a panel verdict.

Usage:
  python run_stage3_architecture_replic.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))
from hic_contact_lib import analyze_contact, bin_of, sample_verdict, score_resolution  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"

FREEZE_JSON = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json"
FREEZE_HASH = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json.sha256"

CLAIM_MD = PROSPECTIVE / "G4c_stage3_architecture_replic_CLAIM_v1.md"
ELIG_JSON = PROSPECTIVE / "G4c_stage3_architecture_replic_eligibility_v1.json"
ELIG_HASH = PROSPECTIVE / "G4c_stage3_architecture_replic_eligibility_v1.json.sha256"
PREFLIGHT_JSON = PROSPECTIVE / "G4c_stage3_architecture_replic_preflight_v1.json"
PREFLIGHT_HASH = PROSPECTIVE / "G4c_stage3_architecture_replic_preflight_v1.json.sha256"

DUMP_DIR = PROSPECTIVE / "g4c_stage3_replic_dumps"
OUT_JSON = PROSPECTIVE / "stage3_architecture_replic_v1.json"
OUT_MD = PROSPECTIVE / "G4c_stage3_architecture_replic_decision_v1.md"

JAVA = Path(r"D:\DNK - 2\tools\jdk-17\bin\java.exe")
JAR = Path(r"D:\DNK - 2\DNA_TE_3DGenome_Context\pilot_scaffold\tools\juicer_tools.jar")

# Remote .hic URLs (eligibility verified, no fallback)
SAMPLE_URLS: dict[str, str] = {
    "noIAAdiff": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/"
        "GSE201820_hic_merge_cloneC16_C3noIAAdiff.inter_30.hic"
    ),
    "noIAAundiff": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/"
        "GSE201820_hic_merge_cloneC16_C3noIAAundiff.inter_30.hic"
    ),
}

SEALED_CHR_HG19 = "11"
SEALED_START_HG19 = 64_000_000
SEALED_END_HG19 = 68_000_000

RESOLUTIONS = [10_000, 25_000]

# Primary analysis: bg_tol_bins=0 (exact-distance background)
BG_TOL_PRIMARY = 0
# Informational: bg_tol_bins=1 (shown but excluded from verdict)
BG_TOL_INFO = 1

# Pre-registered CLAIM sha256 (locks CLAIM before any analysis)
CLAIM_SHA256_EXPECTED = (
    "1f9ec4579482a22915fd091dbec5e1da653838bfe5fa40ca80a87fc83c9f7ff1"
)


# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------


def _reject_holdout_path(p: Path | str) -> None:
    if "holdout" in str(p).lower():
        raise RuntimeError(f"FORBIDDEN: holdout path accessed: {p}")


def _reject_holdout_url(url: str) -> None:
    if "holdout" in url.lower():
        raise RuntimeError(f"FORBIDDEN: holdout URL: {url}")


def _reject_sealed_region(chrom: str, start: int, end: int) -> None:
    if chrom == SEALED_CHR_HG19 and start < SEALED_END_HG19 and end > SEALED_START_HG19:
        raise RuntimeError(
            f"FORBIDDEN: region chr{chrom}:{start}-{end} overlaps sealed interval "
            f"chr{SEALED_CHR_HG19}:{SEALED_START_HG19}-{SEALED_END_HG19}"
        )


# ---------------------------------------------------------------------------
# Hash chain verification
# ---------------------------------------------------------------------------


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_freeze_hash() -> dict:
    """Verify freeze JSON SHA256 sidecar and return parsed content."""
    if not FREEZE_JSON.exists():
        raise FileNotFoundError(f"Freeze JSON not found: {FREEZE_JSON}")
    if not FREEZE_HASH.exists():
        raise FileNotFoundError(f"Freeze hash not found: {FREEZE_HASH}")
    expected = FREEZE_HASH.read_text(encoding="utf-8").strip()
    actual = _sha256_file(FREEZE_JSON)
    if actual != expected:
        raise RuntimeError(
            f"Freeze JSON hash mismatch!\n  expected: {expected}\n  actual:   {actual}"
        )
    return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))


def verify_claim_hash() -> None:
    """Verify G4c CLAIM against the pinned SHA256 constant."""
    if not CLAIM_MD.exists():
        raise FileNotFoundError(f"G4c CLAIM not found: {CLAIM_MD}")
    actual = _sha256_file(CLAIM_MD)
    if actual != CLAIM_SHA256_EXPECTED:
        raise RuntimeError(
            f"G4c CLAIM hash changed since pre-registration!\n"
            f"  pinned:  {CLAIM_SHA256_EXPECTED}\n"
            f"  on disk: {actual}\n"
            "CLAIM must not be modified after analysis begins."
        )


def verify_eligibility_hash() -> dict:
    """Verify eligibility freeze JSON against its SHA256 sidecar."""
    if not ELIG_JSON.exists():
        raise FileNotFoundError(f"Eligibility freeze not found: {ELIG_JSON}")
    if not ELIG_HASH.exists():
        raise FileNotFoundError(f"Eligibility hash not found: {ELIG_HASH}")
    expected = ELIG_HASH.read_text(encoding="utf-8").strip()
    actual = _sha256_file(ELIG_JSON)
    if actual != expected:
        raise RuntimeError(
            f"Eligibility freeze hash mismatch!\n  expected: {expected}\n  actual: {actual}"
        )
    return json.loads(ELIG_JSON.read_text(encoding="utf-8"))


def verify_preflight_hash() -> dict:
    """Verify preflight result JSON against its SHA256 sidecar; confirm overall_status OK."""
    if not PREFLIGHT_JSON.exists():
        raise FileNotFoundError(
            f"Preflight result not found: {PREFLIGHT_JSON}\n"
            "Run _run_preflight_check.py first."
        )
    if not PREFLIGHT_HASH.exists():
        raise FileNotFoundError(f"Preflight hash not found: {PREFLIGHT_HASH}")
    expected = PREFLIGHT_HASH.read_text(encoding="utf-8").strip()
    actual = _sha256_file(PREFLIGHT_JSON)
    if actual != expected:
        raise RuntimeError(
            f"Preflight result hash changed!\n  expected: {expected}\n  actual: {actual}"
        )
    preflight = json.loads(PREFLIGHT_JSON.read_text(encoding="utf-8"))
    if preflight.get("overall_status") != "OK":
        raise RuntimeError(
            f"Preflight status is not OK: {preflight.get('overall_status')}\n"
            "Resolve BLOCKED preflight before running the analysis."
        )
    # WHY: Verify that the CLAIM pinned in the preflight matches this runner's constant.
    if preflight.get("claim_sha256") != CLAIM_SHA256_EXPECTED:
        raise RuntimeError(
            "Preflight CLAIM sha256 does not match runner constant!\n"
            f"  preflight: {preflight.get('claim_sha256')}\n"
            f"  runner:    {CLAIM_SHA256_EXPECTED}"
        )
    return preflight


def verify_cross_chain(
    eligibility: dict,
    preflight: dict,
    freeze_sha256: str,
    eligibility_sha256: str,
) -> None:
    """Verify that all signed metadata artifacts refer to the same inputs."""
    if eligibility.get("anchor_freeze_sha256") != freeze_sha256:
        raise RuntimeError("Eligibility freeze does not pin the current anchor freeze.")
    if eligibility.get("claim_sha256") != CLAIM_SHA256_EXPECTED:
        raise RuntimeError("Eligibility freeze does not pin the locked G4c CLAIM.")
    if preflight.get("eligibility_freeze_sha256") != eligibility_sha256:
        raise RuntimeError("Preflight does not pin the current eligibility freeze.")

    eligible_urls = {
        item.get("sample_label"): item.get("url")
        for item in eligibility.get("eligible_samples", [])
    }
    if eligible_urls != SAMPLE_URLS:
        raise RuntimeError("Eligibility sample URLs do not match the locked runner URLs.")
    preflight_urls = {
        label: record.get("url")
        for label, record in preflight.get("samples", {}).items()
    }
    if preflight_urls != SAMPLE_URLS:
        raise RuntimeError("Preflight sample URLs do not match the locked runner URLs.")


# ---------------------------------------------------------------------------
# Same-bin guard (for bg_tol_bins=0 primary)
# ---------------------------------------------------------------------------


class SameBinGuardError(RuntimeError):
    """Raised when E_mid_bin == P_mid_bin; bg_tol_bins=0 is undefined on diagonal."""


def check_same_bin_guard(
    e_anchor: tuple[int, int],
    p_anchor: tuple[int, int],
    binsize: int,
) -> None:
    """Raise SameBinGuardError if E_mid_bin == P_mid_bin at bg_tol_bins=0."""
    e_mid = bin_of((e_anchor[0] + e_anchor[1]) // 2, binsize)
    p_mid = bin_of((p_anchor[0] + p_anchor[1]) // 2, binsize)
    if e_mid == p_mid:
        raise SameBinGuardError(
            f"HARD-FAIL: E_mid_bin == P_mid_bin == {e_mid} at binsize={binsize}. "
            "bg_tol_bins=0 diagonal background is undefined; computation blocked."
        )


# ---------------------------------------------------------------------------
# Dump management
# ---------------------------------------------------------------------------


def _dump_region_str(chrom: str, start: int, end: int) -> str:
    return f"{chrom}:{start}:{end}"


def compute_region(
    e_hg19: dict, p_hg19: dict, pad: int = 500_000
) -> tuple[str, int, int]:
    """Compute dump region spanning both anchors with padding."""
    chrom = str(e_hg19["chrom"])
    coords = [e_hg19["start"], e_hg19["end"], p_hg19["start"], p_hg19["end"]]
    lo = max(0, min(coords) - pad)
    hi = max(coords) + pad
    return chrom, lo, hi


def dump_matrix(
    hic_url: str,
    norm: str,
    kind: str,
    binsize: int,
    region: str,
    out: Path,
) -> bool:
    """Run juicer_tools dump against remote URL; return True on success.

    Skips if output already exists and is non-empty (no freshness guard here:
    dump files are keyed by sample+slot+resolution and are content-stable).
    Returns False on failure — caller must treat this as BLOCKED.
    """
    _reject_holdout_url(hic_url)
    _reject_holdout_path(out)

    if out.exists() and out.stat().st_size > 10:
        print(f"  [cache] {out.name}")
        return True

    cmd = [
        str(JAVA),
        "-Xmx8g",
        "-jar",
        str(JAR),
        "dump",
        kind,
        norm,
        hic_url,
        region,
        region,
        "BP",
        str(binsize),
        str(out),
    ]
    print(f"  [dump] {kind} {norm} {region} @{binsize}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {out.name}")
        return False
    if r.returncode != 0:
        print(f"  [FAIL] {out.name}: {(r.stderr or r.stdout)[-400:]}")
        return False
    ok = out.exists() and out.stat().st_size > 10
    if not ok:
        print(f"  [EMPTY] {out.name}")
    return ok


# ---------------------------------------------------------------------------
# Per-slot analysis (single sample)
# ---------------------------------------------------------------------------


def analyze_slot_sample(
    slot: dict,
    sample_label: str,
    hic_url: str,
    dump_dir: Path,
    dump_hashes: dict[str, str],
) -> dict:
    """Dump and analyze one frozen slot for one sample.

    Returns a result dict. On BLOCKED (dump failure), sets outcome="BLOCKED".
    """
    result: dict = {
        "slot_id": slot["slot_id"],
        "candidate_id": slot["candidate_id"],
        "variant": slot["variant"],
        "sample_label": sample_label,
    }

    status = slot.get("status", "OK")
    if status != "OK":
        result["outcome"] = status
        result["note"] = f"Slot pre-reg status is {status}; no analysis performed."
        return result

    e37 = slot.get("E_grch37")
    p37 = slot.get("P_grch37")
    if not e37 or not p37:
        result["outcome"] = "BLOCKED_MISSING_HG19_COORDS"
        return result

    chrom, reg_start, reg_end = compute_region(e37, p37)

    _reject_sealed_region(chrom, reg_start, reg_end)
    _reject_sealed_region(chrom, e37["start"], e37["end"])
    _reject_sealed_region(chrom, p37["start"], p37["end"])

    region_str = _dump_region_str(chrom, reg_start, reg_end)
    tag = f"{slot['slot_id']}_{slot['candidate_id']}_{sample_label}"

    e_anchor = (e37["start"], e37["end"])
    p_anchor = (p37["start"], p37["end"])
    focal_1based = (e37["start"] + e37["end"]) // 2

    metrics_primary: dict[int, dict] = {}
    metrics_info: dict[int, dict] = {}
    scores_primary: dict[int, str] = {}
    dump_ok = True
    dump_blocked = False

    for binsize in RESOLUTIONS:
        obs_path = dump_dir / f"{tag}_obs_KR_{binsize // 1000}kb.txt"
        oe_path = dump_dir / f"{tag}_oe_KR_{binsize // 1000}kb.txt"

        ok_obs = dump_matrix(hic_url, "KR", "observed", binsize, region_str, obs_path)
        ok_oe = dump_matrix(hic_url, "KR", "oe", binsize, region_str, oe_path)

        if not ok_obs or not ok_oe:
            dump_ok = False
            dump_blocked = True
            metrics_primary[binsize] = {"dump_status": "BLOCKED"}
            scores_primary[binsize] = "FAIL"
            print(f"  [BLOCKED] dump failed for {tag} at {binsize // 1000}kb")
            continue

        # Hash the dump files for the output record
        for path in (obs_path, oe_path):
            dump_hashes[path.name] = _sha256_file(path)

        # Primary: bg_tol_bins=0 with same-bin guard
        try:
            check_same_bin_guard(e_anchor, p_anchor, binsize)
        except SameBinGuardError as exc:
            guard_score = "UNRESOLVED_SAME_BIN"
            scores_primary[binsize] = guard_score
            metrics_primary[binsize] = {
                "error": "same_bin_guard_violation",
                "message": str(exc),
            }
            print(f"  [SAME_BIN_GUARD] {tag} {binsize // 1000}kb: E_mid == P_mid")
            # Informational at tol=1 (no guard needed there — score_resolution handles it)
            m_info = analyze_contact(
                obs_path,
                oe_path,
                binsize,
                e_anchor,
                p_anchor,
                focal_1based,
                bg_tol_bins=BG_TOL_INFO,
            )
            metrics_info[binsize] = m_info
            continue

        m_primary = analyze_contact(
            obs_path,
            oe_path,
            binsize,
            e_anchor,
            p_anchor,
            focal_1based,
            bg_tol_bins=BG_TOL_PRIMARY,
        )
        score = score_resolution(m_primary)
        metrics_primary[binsize] = m_primary
        scores_primary[binsize] = score

        m_info = analyze_contact(
            obs_path,
            oe_path,
            binsize,
            e_anchor,
            p_anchor,
            focal_1based,
            bg_tol_bins=BG_TOL_INFO,
        )
        metrics_info[binsize] = m_info

    if dump_blocked:
        result["outcome"] = "BLOCKED"
        result["note"] = "juicer_tools dump failed for one or more resolutions."
        result["dump_ok"] = False
        result["metrics_10kb_primary"] = metrics_primary.get(10_000)
        result["metrics_25kb_primary"] = metrics_primary.get(25_000)
        return result

    verdict = sample_verdict(
        res10=scores_primary.get(10_000, "FAIL"),
        res25=scores_primary.get(25_000, "FAIL"),
    )

    result.update(
        {
            "dump_region_hg19": f"chr{chrom}:{reg_start}-{reg_end}",
            "E_hg19": e37,
            "P_hg19": p37,
            "T_gene": slot.get("T_gene"),
            "metrics_10kb_primary": metrics_primary.get(10_000),
            "metrics_25kb_primary": metrics_primary.get(25_000),
            "metrics_10kb_info": metrics_info.get(10_000),
            "metrics_25kb_info": metrics_info.get(25_000),
            "score_10kb": scores_primary.get(10_000, "FAIL"),
            "score_25kb": scores_primary.get(25_000, "FAIL"),
            "outcome": verdict,
            "dump_ok": dump_ok,
        }
    )
    return result


# ---------------------------------------------------------------------------
# Cross-sample slot verdict
# ---------------------------------------------------------------------------


def cross_sample_slot_verdict(diff_outcome: str, undiff_outcome: str) -> str:
    """Combine diff and undiff slot-sample verdicts into a slot verdict.

    Pre-registered in G4c CLAIM §5.
    """
    outcomes = (diff_outcome, undiff_outcome)
    if any(o.startswith("BLOCKED") for o in outcomes):
        return "BLOCKED"
    if any("INCONCLUSIVE" in o for o in outcomes):
        return "REPLICATION_INCONCLUSIVE"
    if diff_outcome == "PASS" and undiff_outcome == "PASS":
        return "REPLICATION_PASS"
    if diff_outcome == "UNSUPPORTED" and undiff_outcome == "UNSUPPORTED":
        return "REPLICATION_UNSUPPORTED"
    if "PASS" in outcomes:
        return "REPLICATION_PARTIAL"
    # Partial + Partial, Partial + Unsupported, etc.
    return "REPLICATION_PARTIAL"


# ---------------------------------------------------------------------------
# Panel verdict
# ---------------------------------------------------------------------------


def panel_verdict(slot_verdicts: list[str]) -> str:
    """Combine per-slot cross-sample verdicts into a panel verdict."""
    if any(v == "BLOCKED" for v in slot_verdicts):
        return "BLOCKED"
    if any("INCONCLUSIVE" in v for v in slot_verdicts):
        return "REPLICATION_INCONCLUSIVE"
    if all(v == "REPLICATION_PASS" for v in slot_verdicts):
        return "REPLICATION_SUPPORTED"
    if all(v == "REPLICATION_UNSUPPORTED" for v in slot_verdicts):
        return "REPLICATION_UNSUPPORTED"
    if any(v == "REPLICATION_PASS" for v in slot_verdicts):
        return "REPLICATION_PARTIAL"
    # CLAIM v1 omitted the all-PARTIAL panel combination. Fail closed to
    # INCONCLUSIVE; this branch is not used by the observed G4c result.
    return "REPLICATION_INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------


def _fmt_primary_metrics(m: dict | None, score: str) -> str:
    if m is None:
        return "| N/A | — |"
    if "error" in m:
        return f"| error | `{m['error']}` |\n| message | {m.get('message', '')} |"
    pair = m.get("primary_pair") or []
    same_bin_note = ""
    if isinstance(pair, list) and len(pair) == 2 and pair[0] == pair[1]:
        same_bin_note = "\n| audit | diagonal self-bin; score = UNRESOLVED_SAME_BIN |"
    return (
        f"| score (tol=0, primary) | `{score}` |\n"
        f"| primary_obs | {m.get('primary_obs')} |\n"
        f"| primary_oe | {m.get('primary_oe')} |\n"
        f"| bg_n (tol=0) | {m.get('same_distance_bg_n')} |\n"
        f"| enrich_mean | {m.get('enrich_mean')} |\n"
        f"| obs_percentile | {m.get('obs_percentile')} |\n"
        f"| focal_row_nonzero | {m.get('focal_row_nonzero')} |" + same_bin_note
    )


def _fmt_info_metrics(m: dict | None) -> str:
    if m is None:
        return "| N/A | — |"
    pair = m.get("primary_pair") or []
    note = ""
    if isinstance(pair, list) and len(pair) == 2 and pair[0] == pair[1]:
        note = "\n| audit | diagonal; metrics informational only |"
    return (
        f"| primary_obs | {m.get('primary_obs')} |\n"
        f"| bg_n (tol=1, info) | {m.get('same_distance_bg_n')} |\n"
        f"| enrich_mean | {m.get('enrich_mean')} |\n"
        f"| obs_percentile | {m.get('obs_percentile')} |" + note
    )


def write_decision_md(
    freeze: dict,
    preflight: dict,
    slot_cross_results: list[dict],
    pv: str,
    dump_hashes: dict[str, str],
) -> None:
    """Write constrained-wording decision Markdown."""
    run_at = datetime.now(timezone.utc).isoformat()

    slot_summary_rows = "\n".join(
        f"| {s['slot_id']} | {s['candidate_id']} | {s['variant']} | "
        f"{s.get('cross_sample_verdict', 'unknown')} |"
        for s in slot_cross_results
    )

    slot_blocks: list[str] = []
    for s in slot_cross_results:
        gene_info = ""
        if s.get("T_gene"):
            g = s["T_gene"]
            gene_info = (
                f"\n**Nearest protein-coding TSS (pre-registered):** "
                f"{g.get('ensg_id')} ({g.get('display_name')}), "
                f"distance {g.get('distance_to_variant_bp')} bp, "
                f"strand {g.get('strand')}"
            )

        diff_r = s.get("noIAAdiff", {})
        undiff_r = s.get("noIAAundiff", {})

        slot_blocks.append(f"""### {s["slot_id"]} — {s["candidate_id"]} ({s["variant"]})

**Slot cross-sample verdict:** `{s.get("cross_sample_verdict", "unknown")}`
{gene_info}

#### noIAAdiff (differentiated)

**Slot-sample outcome:** `{diff_r.get("outcome", "N/A")}`

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
{_fmt_primary_metrics(diff_r.get("metrics_10kb_primary"), diff_r.get("score_10kb", "N/A"))}
| 25 kb | — | — |
{_fmt_primary_metrics(diff_r.get("metrics_25kb_primary"), diff_r.get("score_25kb", "N/A"))}

Informational (tol=1, excluded from verdict):

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
{_fmt_info_metrics(diff_r.get("metrics_10kb_info"))}
| 25 kb | — | — |
{_fmt_info_metrics(diff_r.get("metrics_25kb_info"))}

#### noIAAundiff (undifferentiated)

**Slot-sample outcome:** `{undiff_r.get("outcome", "N/A")}`

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
{_fmt_primary_metrics(undiff_r.get("metrics_10kb_primary"), undiff_r.get("score_10kb", "N/A"))}
| 25 kb | — | — |
{_fmt_primary_metrics(undiff_r.get("metrics_25kb_primary"), undiff_r.get("score_25kb", "N/A"))}

Informational (tol=1, excluded from verdict):

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
{_fmt_info_metrics(undiff_r.get("metrics_10kb_info"))}
| 25 kb | — | — |
{_fmt_info_metrics(undiff_r.get("metrics_25kb_info"))}
""")

    slots_section = "\n".join(slot_blocks)

    dump_hash_rows = "\n".join(
        f"| {k} | {v[:16]}… |" for k, v in sorted(dump_hashes.items())
    )

    md = f"""# Stage-3 Architecture Independent-Source Replication — G4c Decision v1

**Claim:** `G4c_stage3_architecture_replic_CLAIM_v1.md`
**Freeze:** `stage3_architecture_anchor_freeze_v1.json` (frozen {freeze.get("frozen_at")})
**Eligibility freeze:** `G4c_stage3_architecture_replic_eligibility_v1.json`
**Preflight:** `G4c_stage3_architecture_replic_preflight_v1.json`
  (status: {preflight.get("overall_status")}; run_at: {preflight.get("run_at")})
**Analysis run:** {run_at}
**Samples:** GSE201820 noIAAdiff (differentiated) + noIAAundiff (undifferentiated)
  CTCF-AID HUDEP-2, noIAA (active CTCF), clones C16+C3 merged, hg19, KR norm
**Primary bg_tol_bins:** 0 (exact-distance background)
**Panel verdict:** `{pv}`

---

## No-upgrade invariant

G4c verdict `{pv}` does **NOT** change the G4a panel verdict (INCONCLUSIVE).
Stage-3 slot assignments remain LOCKED (registry, 2026-07-15).

---

## Panel summary

| Slot | Candidate | Variant | Cross-sample verdict |
|------|-----------|---------|---------------------|
{slot_summary_rows}

---

## Slot details

{slots_section}

---

## Dump file hashes

| File | SHA256 (first 16 chars) |
|------|------------------------|
{dump_hash_rows if dump_hash_rows else "| (no dumps) | — |"}

---

## Interpretation constraints (pre-registered)

- This analysis tests Contact(anchor_ctcf, anchor_tss) in CTCF-AID HUDEP-2 noIAA cells.
- **NOT CLAIMED:** enhancer–promoter contact, target-gene identity, allele effect,
  expression change, regulation, or pathogenicity.
- G4b allele ΔContact: **NOT TESTED**.
- Wet-lab: **NO-GO** (B0 UNSIGNED as of 2026-07-21; user confirmed desk-only).
- tol=1 informational output is labelled as such and **excluded from the verdict**.
- Outcome does not change Stage-3 slot assignments.

## Caveats

- Background-direction wording in the locked G4a/G4c claims is corrected by
  `G4_stage3_background_direction_ERRATUM_v1.md`; tol=1 inflated, rather than
  compressed, A754 enrichment in the parent matrix.
- bg_tol_bins=0 (exact-distance only): bg_n may be lower than tol=1 baseline.
  If bg_n < 20, score is INSUFFICIENT_BG regardless of signal.
- A518 at 25 kb (ARCH_02): E and P map to the same 25 kb bin (UNRESOLVED_SAME_BIN);
  this is expected from the frozen anchor geometry, same as in G4a.
- Remote .hic access via juicer_tools: dump performance depends on NCBI FTP bandwidth.
- CTCF-AID noIAA ≠ WT Hi-C: chromatin state may differ from GSM4873113.
  A replicated contact in both is stronger independent evidence; a difference is
  informative about condition-dependence, not about anchor correctness.
- KR normalisation; VC not repeated for G4c.
- hg19 coordinates from frozen G4a anchors (Ensembl REST, release 116).
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"[OK] Decision MD: {OUT_MD.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=== Stage-3 Architecture Independent-Source Replication (G4c) ===")
    print(f"Java: {JAVA}")
    print(f"JAR: {JAR}")

    # Holdout guard on all critical paths
    for p in [
        FREEZE_JSON,
        CLAIM_MD,
        ELIG_JSON,
        PREFLIGHT_JSON,
        DUMP_DIR,
        OUT_JSON,
        OUT_MD,
    ]:
        _reject_holdout_path(p)
    for url in SAMPLE_URLS.values():
        _reject_holdout_url(url)

    # Preflight check (must exist and pass before any dump)
    if not JAVA.exists():
        print(f"[ERROR] Java not found: {JAVA}")
        sys.exit(1)
    if not JAR.exists():
        print(f"[ERROR] juicer_tools JAR not found: {JAR}")
        sys.exit(1)

    print("\n[Step 1] Verifying freeze hash …")
    freeze = verify_freeze_hash()
    print(f"         Ensembl release: {freeze.get('ensembl_release')}")
    print(f"         Frozen at: {freeze.get('frozen_at')}")

    print("\n[Step 2] Verifying G4c CLAIM hash …")
    verify_claim_hash()
    print(f"         CLAIM SHA256: OK ({CLAIM_SHA256_EXPECTED[:16]}…)")

    print("\n[Step 3] Verifying eligibility freeze hash …")
    elig = verify_eligibility_hash()
    print(
        f"         Samples eligible: {[s['sample_label'] for s in elig.get('eligible_samples', [])]}"
    )

    print("\n[Step 4] Verifying preflight result hash and status …")
    preflight = verify_preflight_hash()
    verify_cross_chain(
        eligibility=elig,
        preflight=preflight,
        freeze_sha256=FREEZE_HASH.read_text(encoding="utf-8").strip(),
        eligibility_sha256=ELIG_HASH.read_text(encoding="utf-8").strip(),
    )
    print(f"         Preflight status: {preflight['overall_status']}")
    print(f"         Preflight run_at: {preflight['run_at']}")

    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    _reject_holdout_path(DUMP_DIR)

    dump_hashes: dict[str, str] = {}

    print("\n[Step 5] Analyzing slots for each sample …")
    slots = freeze.get("slots", [])

    # Collect per-slot, per-sample results
    # Structure: {slot_id: {sample_label: result_dict}}
    per_slot_samples: dict[str, dict[str, dict]] = {s["slot_id"]: {} for s in slots}

    for sample_label, hic_url in SAMPLE_URLS.items():
        print(f"\n  === Sample: {sample_label} ===")
        print(f"  URL: …{hic_url[-60:]}")
        for slot in slots:
            sid = slot["slot_id"]
            cid = slot["candidate_id"]
            print(f"\n  --- {sid} ({cid}) ---")
            r = analyze_slot_sample(slot, sample_label, hic_url, DUMP_DIR, dump_hashes)
            per_slot_samples[sid][sample_label] = r
            print(f"      outcome = {r.get('outcome')}")

    print("\n[Step 6] Computing cross-sample and panel verdicts …")
    slot_cross_results: list[dict] = []
    slot_cross_verdicts: list[str] = []

    for slot in slots:
        sid = slot["slot_id"]
        diff_r = per_slot_samples[sid].get("noIAAdiff", {})
        undiff_r = per_slot_samples[sid].get("noIAAundiff", {})

        diff_out = diff_r.get("outcome", "BLOCKED")
        undiff_out = undiff_r.get("outcome", "BLOCKED")
        csv = cross_sample_slot_verdict(diff_out, undiff_out)
        slot_cross_verdicts.append(csv)
        print(f"  {sid}: diff={diff_out}, undiff={undiff_out} -> {csv}")

        slot_cross_results.append(
            {
                "slot_id": sid,
                "candidate_id": slot["candidate_id"],
                "variant": slot["variant"],
                "T_gene": slot.get("T_gene"),
                "cross_sample_verdict": csv,
                "noIAAdiff": diff_r,
                "noIAAundiff": undiff_r,
            }
        )

    pv = panel_verdict(slot_cross_verdicts)
    print(f"\n[Panel verdict] {pv}")
    print("[No-upgrade invariant] G4a panel verdict (INCONCLUSIVE) UNCHANGED")

    print("\n[Step 7] Writing outputs …")
    payload = {
        "analysis": "stage3_architecture_replic_v1",
        "g4c_version": "G4c",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "freeze_json": FREEZE_JSON.name,
        "freeze_sha256": FREEZE_HASH.read_text(encoding="utf-8").strip(),
        "claim_md": CLAIM_MD.name,
        "claim_sha256": CLAIM_SHA256_EXPECTED,
        "eligibility_json": ELIG_JSON.name,
        "eligibility_sha256": ELIG_HASH.read_text(encoding="utf-8").strip(),
        "preflight_json": PREFLIGHT_JSON.name,
        "preflight_sha256": PREFLIGHT_HASH.read_text(encoding="utf-8").strip(),
        "samples": list(SAMPLE_URLS.keys()),
        "biosource": "CTCF-AID HUDEP-2 noIAA, clones C16+C3, hg19",
        "geo_series": "GSE201820",
        "norm": "KR",
        "bg_tol_bins_primary": BG_TOL_PRIMARY,
        "bg_tol_bins_informational": BG_TOL_INFO,
        "panel_verdict": pv,
        "g4a_panel_verdict": "INCONCLUSIVE",
        "no_upgrade_invariant": "G4c verdict does not override G4a panel verdict",
        "allele_effect": "NOT_TESTED",
        "g4b": "NOT_TESTED",
        "wet": "NO_GO",
        "dump_sha256": dump_hashes,
        "slots": slot_cross_results,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[OK] Result JSON: {OUT_JSON.name}")

    write_decision_md(freeze, preflight, slot_cross_results, pv, dump_hashes)


if __name__ == "__main__":
    main()
