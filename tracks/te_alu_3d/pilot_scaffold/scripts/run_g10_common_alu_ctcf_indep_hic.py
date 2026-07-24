#!/usr/bin/env python3
"""G10: independent-source Hi-C contact for common Alu∩CTCF anchors (GSE201820)."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))
from hic_contact_lib import analyze_contact, bin_of, sample_verdict, score_resolution  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"
FREEZE_JSON = PROSPECTIVE / "g10_common_alu_ctcf_anchor_freeze_v1.json"
FREEZE_SHA = PROSPECTIVE / "g10_common_alu_ctcf_anchor_freeze_v1.json.sha256"
CLAIM_MD = PROSPECTIVE / "G10_common_alu_ctcf_indep_hic_CLAIM_v1.md"
DUMP_DIR = PROSPECTIVE / "g10_indep_hic_dumps"
OUT_JSON = PROSPECTIVE / "g10_common_alu_ctcf_indep_hic_v1.json"
OUT_MD = PROSPECTIVE / "G10_common_alu_ctcf_indep_hic_decision_v1.md"

JAVA = Path(r"D:\DNK - 2\tools\jdk-17\bin\java.exe")
JAR = Path(r"D:\DNK - 2\DNA_TE_3DGenome_Context\pilot_scaffold\tools\juicer_tools.jar")

# Prefer local mirrors of the same GSE201820 files (identical accession content).
# Remote URLs remain the provenance; local paths avoid repeated FTP per dump.
_LOCAL_HIC_DIR = Path(r"D:\DNK - 2\data\HUDEP2_GSE201820")
_REMOTE = {
    "noIAAdiff": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/"
        "GSE201820_hic_merge_cloneC16_C3noIAAdiff.inter_30.hic"
    ),
    "noIAAundiff": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/"
        "GSE201820_hic_merge_cloneC16_C3noIAAundiff.inter_30.hic"
    ),
}
_LOCAL_NAMES = {
    "noIAAdiff": "GSE201820_hic_merge_cloneC16_C3noIAAdiff.inter_30.hic",
    "noIAAundiff": "GSE201820_hic_merge_cloneC16_C3noIAAundiff.inter_30.hic",
}


def _hic_source(label: str) -> str:
    local = _LOCAL_HIC_DIR / _LOCAL_NAMES[label]
    if local.exists() and local.stat().st_size > 1_000_000:
        return str(local)
    return _REMOTE[label]

SEALED_CHR_HG19 = "11"
SEALED_START_HG19 = 64_000_000
SEALED_END_HG19 = 68_000_000
RESOLUTIONS = [10_000, 25_000]
BG_TOL_PRIMARY = 0
BG_TOL_INFO = 1


class SameBinGuardError(RuntimeError):
    pass


def check_same_bin_guard(e_anchor: tuple[int, int], p_anchor: tuple[int, int], binsize: int) -> None:
    e_mid = (e_anchor[0] + e_anchor[1]) // 2
    p_mid = (p_anchor[0] + p_anchor[1]) // 2
    if bin_of(e_mid, binsize) == bin_of(p_mid, binsize):
        raise SameBinGuardError(
            f"E_mid bin == P_mid bin at {binsize}: {bin_of(e_mid, binsize)}"
        )


def _reject_holdout_path(p: Path | str) -> None:
    if "holdout" in str(p).lower():
        raise RuntimeError(f"FORBIDDEN: holdout path accessed: {p}")


def _reject_sealed_region(chrom: str, start: int, end: int) -> None:
    if chrom == SEALED_CHR_HG19 and start < SEALED_END_HG19 and end > SEALED_START_HG19:
        raise RuntimeError(
            f"FORBIDDEN: region chr{chrom}:{start}-{end} overlaps sealed interval"
        )


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_freeze() -> dict:
    expected = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    actual = _sha256_file(FREEZE_JSON)
    if actual != expected:
        raise RuntimeError(f"freeze hash mismatch: {actual} != {expected}")
    return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))


def compute_region(e_hg19: dict, p_hg19: dict, pad: int = 500_000) -> tuple[str, int, int]:
    chrom = str(e_hg19["chrom"])
    coords = [e_hg19["start"], e_hg19["end"], p_hg19["start"], p_hg19["end"]]
    lo = max(0, min(coords) - pad)
    hi = max(coords) + pad
    return chrom, lo, hi


def dump_matrix(hic_url: str, kind: str, binsize: int, region: str, out: Path) -> bool:
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
        "KR",
        hic_url,
        region,
        region,
        "BP",
        str(binsize),
        str(out),
    ]
    print(f"  [dump] {kind} {region} @{binsize}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {out.name}")
        return False
    if r.returncode != 0:
        print(f"  [FAIL] {out.name}: {(r.stderr or r.stdout)[-400:]}")
        return False
    return out.exists() and out.stat().st_size > 10


def analyze_slot(slot: dict, sample_label: str, hic_url: str, dump_hashes: dict) -> dict:
    result: dict = {
        "slot_id": slot["slot_id"],
        "candidate_id": slot["candidate_id"],
        "variant": slot["variant"],
        "sample_label": sample_label,
    }
    status = slot.get("status", "OK")
    if status != "OK":
        result["outcome"] = status
        return result

    e37 = slot["E_grch37"]
    p37 = slot["P_grch37"]
    chrom, reg_start, reg_end = compute_region(e37, p37)
    _reject_sealed_region(chrom, reg_start, reg_end)
    region = f"{chrom}:{reg_start}:{reg_end}"
    tag = f"{slot['slot_id']}_{slot['candidate_id']}_{sample_label}"
    e_anchor = (e37["start"], e37["end"])
    p_anchor = (p37["start"], p37["end"])
    focal = (e37["start"] + e37["end"]) // 2

    scores: dict[int, str] = {}
    metrics: dict[int, dict] = {}
    dump_blocked = False

    for binsize in RESOLUTIONS:
        obs = DUMP_DIR / f"{tag}_obs_KR_{binsize // 1000}kb.txt"
        oe = DUMP_DIR / f"{tag}_oe_KR_{binsize // 1000}kb.txt"
        if not dump_matrix(hic_url, "observed", binsize, region, obs):
            dump_blocked = True
            scores[binsize] = "FAIL"
            continue
        if not dump_matrix(hic_url, "oe", binsize, region, oe):
            dump_blocked = True
            scores[binsize] = "FAIL"
            continue
        dump_hashes[obs.name] = _sha256_file(obs)
        dump_hashes[oe.name] = _sha256_file(oe)
        try:
            check_same_bin_guard(e_anchor, p_anchor, binsize)
        except SameBinGuardError as exc:
            scores[binsize] = "UNRESOLVED_SAME_BIN"
            metrics[binsize] = {"error": "same_bin", "message": str(exc)}
            continue
        m = analyze_contact(
            obs, oe, binsize, e_anchor, p_anchor, focal, bg_tol_bins=BG_TOL_PRIMARY
        )
        scores[binsize] = score_resolution(m)
        metrics[binsize] = {
            "primary_obs": m.get("primary_obs"),
            "primary_oe": m.get("primary_oe"),
            "enrich_mean": m.get("enrich_mean"),
            "obs_percentile": m.get("obs_percentile"),
            "same_distance_bg_n": m.get("same_distance_bg_n"),
            "score": scores[binsize],
            "info_tol1_enrich_mean": analyze_contact(
                obs, oe, binsize, e_anchor, p_anchor, focal, bg_tol_bins=BG_TOL_INFO
            ).get("enrich_mean"),
        }

    if dump_blocked:
        result["outcome"] = "BLOCKED"
        result["scores"] = {str(k): v for k, v in scores.items()}
        return result

    verdict = sample_verdict(
        scores.get(10_000, "FAIL"),
        scores.get(25_000, "FAIL"),
    )
    result["outcome"] = verdict
    result["scores"] = {str(k): v for k, v in scores.items()}
    result["metrics"] = {str(k): v for k, v in metrics.items()}
    return result


def decide_panel(primary_outcomes: list[str]) -> dict:
    """Panel rule from G10 CLAIM §5."""
    blocked_prefixes = ("BLOCKED",)
    ok = [o for o in primary_outcomes if not any(o.startswith(p) for p in blocked_prefixes)]
    n_ok = len(ok)
    n_pass = sum(1 for o in ok if o == "PASS")
    n_unsup = sum(1 for o in ok if o == "UNSUPPORTED")
    out = {
        "n_ok": n_ok,
        "n_pass": n_pass,
        "n_unsupported": n_unsup,
        "outcomes": primary_outcomes,
    }
    if n_ok < 2:
        out["verdict"] = "INCONCLUSIVE"
        out["reason"] = "underpowered_freeze"
        return out
    need = max(2, math.ceil(n_ok / 2))
    out["need_pass"] = need
    if n_pass >= need:
        out["verdict"] = "PASS"
        out["reason"] = "panel_contact_enriched"
        return out
    if n_pass == 0 and n_unsup >= 2:
        out["verdict"] = "REJECT"
        out["reason"] = "no_pass_majority_unsupported"
        return out
    out["verdict"] = "INCONCLUSIVE"
    out["reason"] = "mixed_or_partial"
    return out


def write_decision(payload: dict) -> None:
    panel = payload["panel_primary"]
    lines = [
        "# G10 — Common Alu∩CTCF × independent HUDEP-2 Hi-C — DECISION v1",
        "",
        f"**Date:** {payload['created_utc'][:10]}",
        f"**Claim:** `{CLAIM_MD.name}`",
        f"**Freeze sha256:** `{payload['freeze_sha256']}`",
        f"**Primary matrix:** GSE201820 noIAAdiff (bg_tol_bins=0)",
        f"**Panel verdict:** **{panel['verdict']}** ({panel.get('reason')})",
        "",
        "## Per-slot (primary)",
        "",
    ]
    for s in payload["slots_primary"]:
        lines.append(
            f"- `{s['slot_id']}` {s['variant']}: **{s['outcome']}** "
            f"(10kb={s.get('scores', {}).get('10000')}; "
            f"25kb={s.get('scores', {}).get('25000')})"
        )
    lines += [
        "",
        "## What this does NOT mean",
        "",
        "1. Not Stage-3 A754/A518 rescue; those slots were excluded.",
        "2. Not GSM4873113 re-analysis.",
        "3. Not regulatory / causal / architecture language.",
        "4. Not wet-lab GO / holdout unlock.",
        "5. noIAAundiff is informational only.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not JAVA.exists():
        raise SystemExit(f"java missing: {JAVA}")
    if not JAR.exists():
        raise SystemExit(f"juicer jar missing: {JAR}")
    freeze = verify_freeze()
    freeze_sha = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    claim_sha = _sha256_file(CLAIM_MD)
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    dump_hashes: dict[str, str] = {}

    src_primary = _hic_source("noIAAdiff")
    src_info = _hic_source("noIAAundiff")
    print(f"[INFO] primary hic source: {src_primary}", flush=True)
    print(f"[INFO] info hic source: {src_info}", flush=True)

    primary_slots = []
    for slot in freeze["slots"]:
        print(f"\n=== PRIMARY noIAAdiff {slot['slot_id']} ===", flush=True)
        primary_slots.append(analyze_slot(slot, "noIAAdiff", src_primary, dump_hashes))

    info_slots: list[dict] = []
    # Info arm only if local mirror exists (panel verdict does not use it).
    if Path(src_info).exists() and not str(src_info).startswith("http"):
        for slot in freeze["slots"]:
            print(f"\n=== INFO noIAAundiff {slot['slot_id']} ===", flush=True)
            info_slots.append(analyze_slot(slot, "noIAAundiff", src_info, dump_hashes))
    else:
        print(
            "[INFO] skipping noIAAundiff dumps (local mirror absent; "
            "informational only per CLAIM)",
            flush=True,
        )
        info_slots = [{"outcome": "SKIPPED_NO_LOCAL_MIRROR", "sample_label": "noIAAundiff"}]

    panel = decide_panel([s["outcome"] for s in primary_slots])
    payload = {
        "result_id": "g10_common_alu_ctcf_indep_hic_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": CLAIM_MD.name,
        "claim_sha256": claim_sha,
        "freeze_sha256": freeze_sha,
        "primary_sample": "noIAAdiff",
        "bg_tol_bins_primary": BG_TOL_PRIMARY,
        "panel_primary": panel,
        "slots_primary": primary_slots,
        "slots_info_undiff": info_slots,
        "dump_sha256": dump_hashes,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_decision(payload)
    print(f"\n[OK] panel={panel['verdict']} ({panel.get('reason')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
