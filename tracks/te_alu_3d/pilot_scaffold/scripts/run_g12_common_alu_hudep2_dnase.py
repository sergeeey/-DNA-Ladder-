#!/usr/bin/env python3
"""G12: G9c panel × HUDEP-2 DNase peak overlap enrichment."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))

from holdout_guard import holdout_is_sealed  # noqa: E402
from g9_eqtl_lib import decide_enrichment, in_half_open  # noqa: E402

OUT = ROOT.parent / "09_outputs" / "prospective"
DATA = ROOT / "data" / "dnase_hudep2"
FREEZE = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json"
FREEZE_SHA = OUT / "g9c_common_alu_ctcf_panel_freeze_v1.json.sha256"
RESULT = OUT / "g12_common_alu_ctcf_hudep2_dnase_v1.json"
DECISION = OUT / "G12_common_alu_ctcf_hudep2_dnase_decision_v1.md"
CLAIM = "G12_common_alu_ctcf_hudep2_dnase_CLAIM_v1.md"

PRIMARY = {
    "experiment": "ENCSR978CYN",
    "accession": "ENCFF626FHU",
    "url": "https://www.encodeproject.org/files/ENCFF626FHU/@@download/ENCFF626FHU.bed.gz",
}
REPLIC = {
    "experiment": "ENCSR013QDF",
    "accession": "ENCFF895OQX",
    "url": "https://www.encodeproject.org/files/ENCFF895OQX/@@download/ENCFF895OQX.bed.gz",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_freeze() -> tuple[dict, str]:
    text = FREEZE.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    expected = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    if digest != expected:
        raise RuntimeError(f"freeze hash mismatch: {digest} != {expected}")
    return json.loads(text), digest


def fetch_peaks(meta: dict) -> tuple[Path, str]:
    DATA.mkdir(parents=True, exist_ok=True)
    dest = DATA / f"g12_hudep2_dnase_peaks_{meta['accession']}.bed.gz"
    sha_path = dest.with_suffix(dest.suffix + ".sha256")
    if dest.exists() and sha_path.exists():
        raw = dest.read_bytes()
        digest = _sha256_bytes(raw)
        expected = sha_path.read_text(encoding="utf-8").strip().split()[0]
        if digest != expected:
            raise RuntimeError(f"peak hash mismatch for {dest.name}")
        return dest, digest
    print(f"[fetch] {meta['accession']} …", flush=True)
    req = urllib.request.Request(
        meta["url"],
        headers={"User-Agent": "DNA-Ladder-G12/1.0 (research)"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = resp.read()
    digest = _sha256_bytes(raw)
    dest.write_bytes(raw)
    sha_path.write_text(digest + "\n", encoding="utf-8")
    print(f"[ok] {dest.name} sha256={digest} bytes={len(raw)}", flush=True)
    return dest, digest


def load_dnase_intervals(path: Path) -> list[tuple[str, int, int, str]]:
    """Load gzipped or plain BED; keep chrom/start/end only."""
    opener = gzip.open if path.suffix == ".gz" or path.name.endswith(".bed.gz") else open
    rows: list[tuple[str, int, int, str]] = []
    with opener(path, "rt", encoding="utf-8") as fh:  # type: ignore[arg-type]
        for line in fh:
            if not line or line.startswith("#") or line.startswith("track"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            chrom = parts[0] if parts[0].startswith("chr") else f"chr{parts[0]}"
            rows.append((chrom, int(parts[1]), int(parts[2]), "."))
    return rows


def variant_in_peaks(
    peaks: list[tuple[str, int, int, str]], chrom: str, pos: int
) -> bool:
    for ch, s, e, _ in peaks:
        if ch != chrom:
            continue
        if in_half_open(pos, s, e):
            return True
    return False


def score_arm(
    variants: list[dict], peaks: list[tuple[str, int, int, str]]
) -> dict:
    n_hit = n_miss = 0
    rows = []
    for v in variants:
        hit = variant_in_peaks(peaks, v["chrom"], int(v["pos"]))
        if hit:
            n_hit += 1
            status = "HIT"
        else:
            n_miss += 1
            status = "MISS"
        rows.append({"variant_id": v["variant_id"], "role": v["role"], "status": status})
    return {
        "n_hit": n_hit,
        "n_miss": n_miss,
        "n_tested": n_hit + n_miss,
        "rows": rows,
    }


def write_decision(payload: dict) -> None:
    prim = payload["primary"]
    dec = prim["decision"]
    lines = [
        "# G12 — Common Alu∩CTCF × HUDEP-2 DNase — DECISION v1",
        "",
        f"**Date:** {payload['created_utc'][:10]}",
        f"**Claim:** `{CLAIM}`",
        f"**Freeze sha256:** `{payload['freeze_sha256']}`",
        f"**Primary peaks:** `{prim['accession']}` ({prim['experiment']})",
        f"**Peaks sha256:** `{prim['peaks_sha256']}`",
        f"**Verdict:** **{dec['verdict']}** ({dec.get('reason', '')})",
        "",
        "## Primary counts",
        "",
        f"- cases: hit={prim['case']['n_hit']} miss={prim['case']['n_miss']}",
        f"- controls: hit={prim['ctrl']['n_hit']} miss={prim['ctrl']['n_miss']}",
        f"- p_case={dec.get('p_case')} p_ctrl={dec.get('p_ctrl')} "
        f"risk_diff={dec.get('risk_diff')} fisher_p={dec.get('fisher_p')}",
        "",
        "## What this does NOT mean",
        "",
        "1. Not eQTL / expression enrichment.",
        "2. Not Hi-C contact or architecture.",
        "3. Not causal Alu→CTCF→accessibility.",
        "4. Not wet-lab GO / holdout unlock.",
        "",
    ]
    if payload.get("replication"):
        r = payload["replication"]
        lines += [
            "## Replication",
            "",
            f"- {r['accession']}: {r['decision']['verdict']} ({r['decision'].get('reason')})",
            "",
        ]
    DECISION.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    assert holdout_is_sealed()
    OUT.mkdir(parents=True, exist_ok=True)
    freeze, freeze_sha = _verify_freeze()
    cases = [v for v in freeze["variants"] if v["role"] == "CASE_CTCF_ALU"]
    ctrls = [v for v in freeze["variants"] if v["role"] == "CTRL_ALU_NONCTCF"]
    print(f"n_case={len(cases)} n_ctrl={len(ctrls)}", flush=True)

    peak_path, peak_sha = fetch_peaks(PRIMARY)
    peaks = load_dnase_intervals(peak_path)
    print(f"n_peaks={len(peaks)}", flush=True)

    case_arm = score_arm(cases, peaks)
    ctrl_arm = score_arm(ctrls, peaks)
    decision = decide_enrichment(
        case_arm["n_hit"],
        case_arm["n_miss"],
        ctrl_arm["n_hit"],
        ctrl_arm["n_miss"],
    )
    payload: dict = {
        "result_id": "g12_common_alu_ctcf_hudep2_dnase_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": CLAIM,
        "freeze_sha256": freeze_sha,
        "chromosomes": freeze.get("chromosomes"),
        "primary": {
            "experiment": PRIMARY["experiment"],
            "accession": PRIMARY["accession"],
            "peaks_sha256": peak_sha,
            "n_peaks": len(peaks),
            "case": {
                "n_hit": case_arm["n_hit"],
                "n_miss": case_arm["n_miss"],
                "n_tested": case_arm["n_tested"],
            },
            "ctrl": {
                "n_hit": ctrl_arm["n_hit"],
                "n_miss": ctrl_arm["n_miss"],
                "n_tested": ctrl_arm["n_tested"],
            },
            "decision": decision,
            "rows": case_arm["rows"] + ctrl_arm["rows"],
        },
    }

    if decision.get("verdict") == "PASS":
        print("[replic] fetching ENCSR013QDF …", flush=True)
        rpath, rsha = fetch_peaks(REPLIC)
        rpeaks = load_dnase_intervals(rpath)
        rc = score_arm(cases, rpeaks)
        rr = score_arm(ctrls, rpeaks)
        rdec = decide_enrichment(rc["n_hit"], rc["n_miss"], rr["n_hit"], rr["n_miss"])
        payload["replication"] = {
            "experiment": REPLIC["experiment"],
            "accession": REPLIC["accession"],
            "peaks_sha256": rsha,
            "n_peaks": len(rpeaks),
            "case": {"n_hit": rc["n_hit"], "n_miss": rc["n_miss"]},
            "ctrl": {"n_hit": rr["n_hit"], "n_miss": rr["n_miss"]},
            "decision": rdec,
        }

    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_decision(payload)
    print(f"DONE verdict={decision['verdict']} reason={decision.get('reason')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
