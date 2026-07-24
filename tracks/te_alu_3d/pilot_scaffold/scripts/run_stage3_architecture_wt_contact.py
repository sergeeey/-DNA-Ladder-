"""Stage-3 Architecture WT contact analysis — GSM4873113 (WT HUDEP-2 Hi-C).

Reads the frozen anchor definitions from stage3_architecture_anchor_freeze_v1.json,
dumps observed/OE KR matrices at 10 kb and 25 kb for each slot, analyzes contact
using hic_contact_lib.py, and writes JSON + decision Markdown.

Safety guards:
  - Verifies freeze JSON SHA256 before proceeding.
  - Rejects any path containing 'holdout'.
  - Rejects any dump region overlapping chr11:64–68 Mb (sealed in hg19).
  - Skips BLOCKED slots (no analysis, retains pre-reg outcome).
  - Ensures dump files are newer than the freeze JSON (freshness guard).

Dataset: GSE160422 GSM4873113 WT HUDEP-2 genome-wide Hi-C ONLY.
No allele-comparison, no G4b, no wet-lab.

Usage:
  python run_stage3_architecture_wt_contact.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Local library — import from same directory
_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))
from hic_contact_lib import analyze_contact, sample_verdict, score_resolution  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"
FREEZE_JSON = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json"
FREEZE_HASH = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json.sha256"
DUMP_DIR = PROSPECTIVE / "g4a_stage3_architecture_wt_dumps"
OUT_JSON = PROSPECTIVE / "stage3_architecture_wt_contact_v1.json"
OUT_MD = PROSPECTIVE / "G4a_stage3_architecture_wt_contact_decision_v1.md"

HIC_FILE = Path(r"D:\DNK - 2\data\HUDEP2_GSE160422\GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic")
JAVA = Path(r"D:\DNK - 2\tools\jdk-17\bin\java.exe")
JAR = Path(r"D:\DNK - 2\DNA_TE_3DGenome_Context\pilot_scaffold\tools\juicer_tools.jar")

# Sealed region in hg19 (approximate) — dump regions must not overlap
SEALED_CHR_HG19 = "11"
SEALED_START_HG19 = 64_000_000
SEALED_END_HG19 = 68_000_000

RESOLUTIONS = [10_000, 25_000]


# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------


def _reject_holdout_path(path: Path) -> None:
    if "holdout" in str(path).lower():
        raise RuntimeError(f"FORBIDDEN: holdout path accessed: {path}")


def _reject_sealed_region(chrom: str, start: int, end: int) -> None:
    if chrom == SEALED_CHR_HG19 and start < SEALED_END_HG19 and end > SEALED_START_HG19:
        raise RuntimeError(
            f"FORBIDDEN: dump region chr{chrom}:{start}-{end} overlaps sealed interval "
            f"chr{SEALED_CHR_HG19}:{SEALED_START_HG19}-{SEALED_END_HG19}"
        )


def verify_freeze_hash() -> dict:
    """Load and verify the freeze JSON against its SHA256 sidecar."""
    if not FREEZE_JSON.exists():
        raise FileNotFoundError(f"Freeze JSON not found: {FREEZE_JSON}")
    if not FREEZE_HASH.exists():
        raise FileNotFoundError(f"Freeze hash not found: {FREEZE_HASH}")
    expected = FREEZE_HASH.read_text(encoding="utf-8").strip()
    actual = hashlib.sha256(FREEZE_JSON.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(
            f"Freeze JSON hash mismatch!\n  expected: {expected}\n  actual:   {actual}\n"
            f"Re-run freeze_stage3_architecture_anchors.py to regenerate."
        )
    return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Dump management
# ---------------------------------------------------------------------------


def _dump_region_str(chrom: str, start: int, end: int) -> str:
    """Format a juicer_tools region string: 'chrom:start:end'."""
    return f"{chrom}:{start}:{end}"


def dump_matrix(
    hic: Path,
    norm: str,
    kind: str,
    binsize: int,
    region: str,
    out: Path,
    freeze_mtime: float,
) -> bool:
    """Run juicer_tools dump; return True on success.

    Skips if output already exists, is non-empty, AND is newer than the freeze JSON.
    """
    _reject_holdout_path(hic)
    _reject_holdout_path(out)

    if out.exists() and out.stat().st_size > 10:
        if out.stat().st_mtime > freeze_mtime:
            print(f"  [cache] {out.name}")
            return True
        # WHY: stale file (older than freeze) must be recomputed to ensure
        #      the dump corresponds to the current frozen anchors.
        print(f"  [stale] {out.name} — recomputing")
        out.unlink()

    cmd = [
        str(JAVA),
        "-Xmx8g",
        "-jar",
        str(JAR),
        "dump",
        kind,
        norm,
        str(hic),
        region,
        region,
        "BP",
        str(binsize),
        str(out),
    ]
    print(f"  [dump] {' '.join(cmd[-8:])}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
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
# Per-slot analysis
# ---------------------------------------------------------------------------


def compute_region(e_hg19: dict, p_hg19: dict, pad: int = 500_000) -> tuple[str, int, int]:
    """Compute a dump region spanning both anchors with padding.

    Returns (chrom_num, start, end) for hg19.
    """
    chrom = str(e_hg19["chrom"])
    all_coords = [e_hg19["start"], e_hg19["end"], p_hg19["start"], p_hg19["end"]]
    lo = max(0, min(all_coords) - pad)
    hi = max(all_coords) + pad
    return chrom, lo, hi


def analyze_slot(slot: dict, dump_dir: Path, freeze_mtime: float) -> dict:
    """Dump and analyze one frozen slot.  Returns a results dict."""
    result: dict = {
        "slot_id": slot["slot_id"],
        "candidate_id": slot["candidate_id"],
        "variant": slot["variant"],
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

    # Safety: no dump in sealed region
    _reject_sealed_region(chrom, reg_start, reg_end)
    _reject_sealed_region(chrom, e37["start"], e37["end"])
    _reject_sealed_region(chrom, p37["start"], p37["end"])

    region_str = _dump_region_str(chrom, reg_start, reg_end)
    tag = f"{slot['slot_id']}_{slot['candidate_id']}"

    metrics_by_res: dict[int, dict] = {}
    scores_by_res: dict[int, str] = {}
    dump_ok = True

    for binsize in RESOLUTIONS:
        obs_path = dump_dir / f"{tag}_obs_KR_{binsize // 1000}kb.txt"
        oe_path = dump_dir / f"{tag}_oe_KR_{binsize // 1000}kb.txt"

        ok_obs = dump_matrix(HIC_FILE, "KR", "observed", binsize, region_str, obs_path, freeze_mtime)
        ok_oe = dump_matrix(HIC_FILE, "KR", "oe", binsize, region_str, oe_path, freeze_mtime)

        if not ok_obs or not ok_oe:
            dump_ok = False
            metrics_by_res[binsize] = {"dump_status": "FAIL"}
            scores_by_res[binsize] = "FAIL"
            continue

        # Focal row = mid-point of E anchor (1-based)
        focal_1based = (e37["start"] + e37["end"]) // 2

        m = analyze_contact(
            obs_path=obs_path,
            oe_path=oe_path,
            binsize=binsize,
            e_anchor=(e37["start"], e37["end"]),
            p_anchor=(p37["start"], p37["end"]),
            focal_row_coord=focal_1based,
        )
        metrics_by_res[binsize] = m
        scores_by_res[binsize] = score_resolution(m)

    verdict = sample_verdict(
        res10=scores_by_res.get(10_000, "FAIL"),
        res25=scores_by_res.get(25_000, "FAIL"),
    )

    result.update(
        {
            "dump_region_hg19": f"chr{chrom}:{reg_start}-{reg_end}",
            "E_hg19": e37,
            "P_hg19": p37,
            "T_gene": slot.get("T_gene"),
            "metrics_10kb": metrics_by_res.get(10_000),
            "metrics_25kb": metrics_by_res.get(25_000),
            "score_10kb": scores_by_res.get(10_000, "FAIL"),
            "score_25kb": scores_by_res.get(25_000, "FAIL"),
            "outcome": verdict,
            "dump_ok": dump_ok,
        }
    )
    return result


# ---------------------------------------------------------------------------
# Panel verdict
# ---------------------------------------------------------------------------


def panel_verdict(slot_results: list[dict]) -> str:
    """Combine slot outcomes into a panel verdict."""
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
# Output writers
# ---------------------------------------------------------------------------


def _fmt_metrics(m: dict | None) -> str:
    if m is None:
        return "N/A"
    lines = [
        f"| primary_obs | {m.get('primary_obs')} |",
        f"| primary_oe | {m.get('primary_oe')} |",
        f"| bg_n | {m.get('same_distance_bg_n')} |",
        f"| enrich_mean | {m.get('enrich_mean')} |",
        f"| obs_percentile | {m.get('obs_percentile')} |",
        f"| focal_row_nonzero | {m.get('focal_row_nonzero')} |",
    ]
    pair = m.get("primary_pair")
    if isinstance(pair, list) and len(pair) == 2 and pair[0] == pair[1]:
        lines.append(
            "| audit_note | diagonal target_dist=0; metrics not interpretable "
            "as between-anchor enrichment |"
        )
    return "\n".join(lines)


def write_decision_md(freeze: dict, slot_results: list[dict], pv: str) -> None:
    """Write constrained-wording decision Markdown."""
    frozen_at = freeze.get("frozen_at", "unknown")
    run_at = datetime.now(timezone.utc).isoformat()

    blocks: list[str] = []
    for s in slot_results:
        out = s.get("outcome", "unknown")
        gene_info = ""
        if s.get("T_gene"):
            g = s["T_gene"]
            gene_info = (
                f"\n**Nearest protein-coding TSS (pre-registered):** "
                f"{g.get('ensg_id')} ({g.get('display_name')}), "
                f"distance {g.get('distance_to_variant_bp')} bp, "
                f"strand {g.get('strand')}"
            )
        blocks.append(
            f"""### {s['slot_id']} — {s['candidate_id']} ({s['variant']})

**Slot outcome:** `{out}`  
**Score 10 kb:** `{s.get('score_10kb', 'N/A')}`  
**Score 25 kb:** `{s.get('score_25kb', 'N/A')}`  
{gene_info}

#### Metrics 10 kb

| metric | value |
|--------|-------|
{_fmt_metrics(s.get('metrics_10kb'))}

#### Metrics 25 kb

| metric | value |
|--------|-------|
{_fmt_metrics(s.get('metrics_25kb'))}
"""
        )

    slots_section = "\n".join(blocks)

    md = f"""# Stage-3 Architecture WT Contact — Decision v1

**Claim:** `G4a_stage3_architecture_wt_contact_CLAIM_v1.md`  
**Freeze:** `stage3_architecture_anchor_freeze_v1.json` (frozen {frozen_at})  
**Analysis run:** {run_at}  
**Sample:** GSE160422 GSM4873113 (WT HUDEP-2 genome-wide Hi-C), KR norm  
**Panel verdict:** `{pv}`

---

## Panel summary

| Slot | Candidate | Variant | Outcome |
|------|-----------|---------|---------|
{"".join(f"| {s['slot_id']} | {s['candidate_id']} | {s['variant']} | {s.get('outcome', 'unknown')} |" + chr(10) for s in slot_results)}

---

## Slot details

{slots_section}

---

## Interpretation constraints (pre-registered)

- This analysis tests Contact(anchor_ctcf, anchor_tss) in WT HUDEP-2 at pre-registered anchors.
- **NOT CLAIMED:** enhancer–promoter contact, target-gene identity, allele effect, expression
  change, regulation, or pathogenicity.
- G4b allele ΔContact: **NOT TESTED** (desk-only).
- Wet-lab: **NO-GO** (B0 UNSIGNED as of 2026-07-21; user confirmed desk-only).
- Outcome does not change Stage-3 slot assignments (see registry, locked 2026-07-15).

## Caveats

- Post-analysis correction: a same-bin E/P pair is `UNRESOLVED_SAME_BIN`,
  not FAIL (`CLAIM v1`, integrity amendment §8).
- Without that correction, A518 would have been labelled UNSUPPORTED; the
  panel verdict would still have remained INCONCLUSIVE.
- A518 25 kb metrics use `target_dist=0` diagonal background and are shown
  only for audit; they are not interpretable as between-anchor enrichment.
- `bg_tol_bins=1` mixes 0/1/2-bin distances when anchors are one bin apart.
  This inherited near-diagonal background is conservative but heterogeneous.
- Single WT replicate (.hic file); no independent replicate Hi-C available for this
  specific combination of sample + method + reference.
- KR normalization; VC sensitivity not repeated for Stage-3 (robustness established
  at G4a Stage-2 for the same .hic file, see `G4a_multisample_kill_test_v1.md`).
- hg19 coordinates derived from GRCh38 via Ensembl REST; small rounding differences
  at bin boundaries are possible.
- Architecture candidates; contact evidence alone does not confirm causal role.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"[OK] Decision MD: {OUT_MD.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=== Stage-3 Architecture WT Contact Analysis ===")
    print(f"HiC: {HIC_FILE}")
    print(f"Java: {JAVA}")
    print(f"JAR: {JAR}")

    # Preflight checks
    _reject_holdout_path(HIC_FILE)
    if not HIC_FILE.exists():
        print(f"[ERROR] Hi-C file not found: {HIC_FILE}")
        sys.exit(1)
    if not JAVA.exists():
        print(f"[ERROR] Java not found: {JAVA}")
        sys.exit(1)
    if not JAR.exists():
        print(f"[ERROR] juicer_tools JAR not found: {JAR}")
        sys.exit(1)

    # Verify freeze
    print("\n[Step 1] Verifying freeze JSON hash …")
    freeze = verify_freeze_hash()
    print(f"         Ensembl release: {freeze.get('ensembl_release')}")
    print(f"         Frozen at: {freeze.get('frozen_at')}")
    freeze_mtime = FREEZE_JSON.stat().st_mtime

    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    _reject_holdout_path(DUMP_DIR)

    # Analyze slots
    print("\n[Step 2] Analyzing slots …")
    slot_results: list[dict] = []
    for slot in freeze.get("slots", []):
        print(f"\n--- {slot['slot_id']} ({slot['candidate_id']}) ---")
        r = analyze_slot(slot, DUMP_DIR, freeze_mtime)
        slot_results.append(r)
        print(f"    outcome = {r.get('outcome')}")

    pv = panel_verdict(slot_results)
    print(f"\n[Panel verdict] {pv}")

    # Write outputs
    payload = {
        "analysis": "stage3_architecture_wt_contact_v1",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "freeze_json": FREEZE_JSON.name,
        "freeze_sha256": FREEZE_HASH.read_text(encoding="utf-8").strip(),
        "hic_file": str(HIC_FILE),
        "sample": "GSM4873113",
        "biosource": "HUDEP-2 WT",
        "norm": "KR",
        "panel_verdict": pv,
        "allele_effect": "NOT_TESTED",
        "g4b": "NOT_TESTED",
        "wet": "NO_GO",
        "slots": slot_results,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[OK] JSON: {OUT_JSON.name}")

    write_decision_md(freeze, slot_results, pv)


if __name__ == "__main__":
    main()
