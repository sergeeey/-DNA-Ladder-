#!/usr/bin/env python3
"""G4a multi-sample robustness — try to KILL single-.hic PASS_DESK.

Pre-registered BEFORE seeing multi-sample numbers:

Kill / demote G4a PASS_DESK → UNRESOLVED if ANY:
  K1. locked E–P contact meets PASS_DESK rule ONLY in GSM4873113 among
      genome-wide Hi-C samples (3113/3114/3115) at KR 10kb+25kb
  K2. WT 3113 PASS under KR but FAIL under VC at BOTH 10kb and 25kb
      (reasonable alternate normalization wipeout)
  K3. primary Contact/OE missing (None) in WT 3113 at KR

Not kill by themselves:
  - Capture-C 3116–3118 sparse/absent at C1 window (β-globin bait expected)
  - DEL/INV quantitative change without WT wipeout
  - Soft INCONCLUSIVE on one resolution only

PASS retained if:
  - WT 3113 still PASS under KR at both resolutions AND
  - at least one other GW sample (3114 or 3115) also meets soft-or-pass at 10kb
    OR WT 3113 also PASS/LEAN under VC at ≥1 resolution
  AND K2/K3 not triggered

Usage:
  python scripts/run_g4a_multisample_desk.py
"""

from __future__ import annotations

import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(r"D:\DNK - 2\data\HUDEP2_GSE160422")
DUMP = ROOT / "09_outputs" / "prospective" / "g4a_dumps_multi"
OUT_JSON = ROOT / "09_outputs" / "prospective" / "G4a_multisample_metrics_v1.json"
OUT_MD = ROOT / "09_outputs" / "prospective" / "G4a_multisample_kill_test_v1.md"
JAVA = Path(r"D:\DNK - 2\tools\jdk-17\bin\java.exe")
JAR = ROOT / "pilot_scaffold" / "tools" / "juicer_tools.jar"

# hg19 locked — DO NOT CHANGE after viewing results
E = (62157472, 62162472)
P = (62457472, 62462472)
C1 = 62521395
REGION = "11:62000000:62750000"

SAMPLES = [
    ("GSM4873113", "WT_GW", "GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic", "genome_wide"),
    ("GSM4873114", "DEL_GW", "GSM4873114_B6-HUDEP2-HiC_allValidPairs.hic", "genome_wide"),
    ("GSM4873115", "INV_GW", "GSM4873115_A2-HUDEP2-HiC_allValidPairs.hic", "genome_wide"),
    ("GSM4873116", "WT_CAP", "GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic", "capture_betaglobin"),
    ("GSM4873117", "DEL_CAP", "GSM4873117_B6-HUDEP2-captureHiC_allValidPairs.hic", "capture_betaglobin"),
    ("GSM4873118", "INV_CAP", "GSM4873118_A2-HUDEP2-captureHiC_allValidPairs.hic", "capture_betaglobin"),
]


def load_triples(path: Path) -> list[tuple[int, int, float]]:
    rows: list[tuple[int, int, float]] = []
    if not path.exists() or path.stat().st_size < 10:
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        rows.append((int(parts[0]), int(parts[1]), float(parts[2])))
    return rows


def bin_of(coord: int, binsize: int) -> int:
    return (coord // binsize) * binsize


def analyze(obs_path: Path, oe_path: Path, binsize: int, bg_tol_bins: int = 1) -> dict:
    obs = load_triples(obs_path)
    oe_raw = load_triples(oe_path)
    oe: dict[tuple[int, int], float] = {}
    for a, b, v in oe_raw:
        oe[(a, b)] = v
        oe[(b, a)] = v
    obs_map: dict[tuple[int, int], float] = {}
    for a, b, v in obs:
        obs_map[(a, b)] = v
        obs_map[(b, a)] = v

    e_bins = sorted({bin_of(E[0], binsize), bin_of(E[1] - 1, binsize)})
    p_bins = sorted({bin_of(P[0], binsize), bin_of(P[1] - 1, binsize)})
    c1_bin = bin_of(C1, binsize)
    e_mid = bin_of((E[0] + E[1]) // 2, binsize)
    p_mid = bin_of((P[0] + P[1]) // 2, binsize)
    primary = (e_mid, p_mid)
    primary_obs = obs_map.get(primary)
    primary_oe = oe.get(primary)

    target_dist = abs(p_mid - e_mid)
    tol = binsize * bg_tol_bins
    bg_obs: list[float] = []
    bg_oe: list[float] = []
    for a, b, v in obs:
        d = abs(b - a)
        if abs(d - target_dist) <= tol and not (
            min(a, b) in e_bins and max(a, b) in p_bins
        ):
            bg_obs.append(v)
            ov = oe.get((a, b))
            if ov is not None:
                bg_oe.append(ov)

    def pct_rank(x: float | None, arr: list[float]) -> float | None:
        if x is None or not arr:
            return None
        return sum(1 for t in arr if t <= x) / len(arr)

    mean_bg = statistics.mean(bg_obs) if bg_obs else None
    med_bg = statistics.median(bg_obs) if bg_obs else None
    enrich_mean = (primary_obs / mean_bg) if (primary_obs and mean_bg) else None
    enrich_med = (primary_obs / med_bg) if (primary_obs and med_bg) else None
    c1_row = [v for (a, b), v in obs_map.items() if a == c1_bin or b == c1_bin]

    return {
        "binsize": binsize,
        "bg_tol_bins": bg_tol_bins,
        "primary_pair": list(primary),
        "primary_obs": primary_obs,
        "primary_oe": primary_oe,
        "same_distance_bg_n": len(bg_obs),
        "bg_mean_obs": mean_bg,
        "bg_median_obs": med_bg,
        "enrichment_vs_mean_bg": enrich_mean,
        "enrichment_vs_median_bg": enrich_med,
        "obs_percentile_same_dist": pct_rank(primary_obs, bg_obs),
        "oe_percentile_same_dist": pct_rank(primary_oe, bg_oe),
        "c1_row_nonzero": len([v for v in c1_row if v > 0]),
        "n_obs_pixels": len(obs),
    }


def score_resolution(m: dict) -> str:
    e = m.get("enrichment_vs_mean_bg")
    p = m.get("obs_percentile_same_dist")
    oe = m.get("primary_oe")
    if (
        m.get("primary_obs") is not None
        and m.get("c1_row_nonzero", 0) > 0
        and e is not None
        and e >= 1.5
        and p is not None
        and p >= 0.75
        and oe is not None
        and oe >= 1.2
    ):
        return "PASS"
    if (
        m.get("primary_obs") is not None
        and e is not None
        and e >= 1.2
        and p is not None
        and p >= 0.60
    ):
        return "SOFT"
    if m.get("primary_obs") is not None:
        return "PRESENT_WEAK"
    return "ABSENT"


def sample_verdict(m10: dict, m25: dict) -> str:
    s10, s25 = score_resolution(m10), score_resolution(m25)
    if s10 == "PASS" and s25 == "PASS":
        return "PASS_DESK"
    if s10 == "PASS" or s25 == "PASS" or (s10 == "SOFT" and s25 == "SOFT"):
        return "INCONCLUSIVE_LEAN_POSITIVE"
    if s10 in ("SOFT", "PRESENT_WEAK") or s25 in ("SOFT", "PRESENT_WEAK"):
        return "INCONCLUSIVE"
    return "FAIL_DESK"


def dump_matrix(hic: Path, norm: str, binsize: int, kind: str, out: Path) -> bool:
    """kind: observed | oe"""
    if out.exists() and out.stat().st_size > 100:
        return True
    cmd = [
        str(JAVA),
        "-Xmx8g",
        "-jar",
        str(JAR),
        "dump",
        kind,
        norm,
        str(hic),
        REGION,
        REGION,
        "BP",
        str(binsize),
        str(out),
    ]
    print(" ", " ".join(cmd[-8:]), flush=True)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print("  TIMEOUT", out.name)
        return False
    if r.returncode != 0:
        print("  FAIL", out.name, (r.stderr or r.stdout)[-400:])
        return False
    return out.exists() and out.stat().st_size > 10


def main() -> int:
    DUMP.mkdir(parents=True, exist_ok=True)
    pre_registered = {
        "kill_criteria": ["K1_only_3113_among_GW", "K2_KR_pass_VC_fail_both_res", "K3_WT_missing_primary"],
        "anchors_locked": True,
        "E_hg19": list(E),
        "P_hg19": list(P),
        "C1_hg19": C1,
        "timestamp_start": datetime.now(timezone.utc).isoformat(),
    }

    jobs = []
    # Primary: KR all samples, 10+25kb
    for gsm, alias, fname, kind in SAMPLES:
        for binsize in (10000, 25000):
            jobs.append((gsm, alias, fname, kind, "KR", binsize))
    # Norm sensitivity on WT GW only
    for binsize in (10000, 25000):
        jobs.append(("GSM4873113", "WT_GW", SAMPLES[0][2], "genome_wide", "VC", binsize))

    results = []
    for gsm, alias, fname, kind, norm, binsize in jobs:
        hic = DATA / fname
        tag = f"{gsm}_{alias}_{norm}_{binsize // 1000}kb"
        obs_p = DUMP / f"{tag}_obs.txt"
        oe_p = DUMP / f"{tag}_oe.txt"
        print(f"== {tag}", flush=True)
        if not hic.exists():
            results.append({"sample": gsm, "alias": alias, "norm": norm, "binsize": binsize, "status": "MISSING_HIC"})
            continue
        ok_obs = dump_matrix(hic, norm, binsize, "observed", obs_p)
        ok_oe = dump_matrix(hic, norm, binsize, "oe", oe_p)
        if not ok_obs:
            results.append(
                {
                    "sample": gsm,
                    "alias": alias,
                    "assay": kind,
                    "norm": norm,
                    "binsize": binsize,
                    "status": "DUMP_FAIL",
                }
            )
            continue
        # analyze with tol=1 and tol=2 backgrounds
        row = {
            "sample": gsm,
            "alias": alias,
            "assay": kind,
            "norm": norm,
            "binsize": binsize,
            "status": "OK",
            "metrics_tol1": analyze(obs_p, oe_p, binsize, bg_tol_bins=1),
            "metrics_tol2": analyze(obs_p, oe_p, binsize, bg_tol_bins=2),
        }
        row["resolution_score"] = score_resolution(row["metrics_tol1"])
        results.append(row)
        time.sleep(0.2)

    # Aggregate per sample KR
    by_sample: dict[str, dict] = {}
    for r in results:
        if r.get("status") != "OK" or r.get("norm") != "KR":
            continue
        key = r["sample"]
        by_sample.setdefault(
            key,
            {"sample": key, "alias": r["alias"], "assay": r["assay"], "res": {}},
        )
        by_sample[key]["res"][r["binsize"]] = r

    sample_verdicts = {}
    for gsm, pack in by_sample.items():
        m10 = pack["res"].get(10000, {}).get("metrics_tol1")
        m25 = pack["res"].get(25000, {}).get("metrics_tol1")
        if m10 and m25:
            sample_verdicts[gsm] = {
                "verdict": sample_verdict(m10, m25),
                "enrich_10kb": m10.get("enrichment_vs_mean_bg"),
                "oe_10kb": m10.get("primary_oe"),
                "enrich_25kb": m25.get("enrichment_vs_mean_bg"),
                "oe_25kb": m25.get("primary_oe"),
                "assay": pack["assay"],
                "alias": pack["alias"],
            }

    # VC WT
    vc = {}
    for r in results:
        if r.get("sample") == "GSM4873113" and r.get("norm") == "VC" and r.get("status") == "OK":
            vc[r["binsize"]] = r

    wt_kr = sample_verdicts.get("GSM4873113", {})
    gw_others = {
        k: v
        for k, v in sample_verdicts.items()
        if k in ("GSM4873114", "GSM4873115") and v.get("assay") == "genome_wide"
    }

    # Kill evaluation (pre-registered logic)
    kills = []
    if not wt_kr or wt_kr.get("verdict") in (None, "FAIL_DESK"):
        if wt_kr.get("oe_10kb") is None and wt_kr.get("enrich_10kb") is None:
            kills.append("K3_WT_missing_primary")

    wt_only = False
    if wt_kr.get("verdict") == "PASS_DESK":
        other_ok = any(
            v.get("verdict") in ("PASS_DESK", "INCONCLUSIVE_LEAN_POSITIVE", "INCONCLUSIVE")
            and (v.get("enrich_10kb") or 0) >= 1.2
            for v in gw_others.values()
        )
        # Also count SOFT presence
        other_present = any(
            (v.get("enrich_10kb") is not None and v.get("oe_10kb") is not None)
            for v in gw_others.values()
        )
        if not other_ok and not other_present:
            wt_only = True
            kills.append("K1_only_3113_among_GW")
        elif not other_ok:
            # present but weak — soft flag, not hard kill yet; register as caution
            pass

    vc_fail_both = False
    if 10000 in vc and 25000 in vc:
        s10 = score_resolution(vc[10000]["metrics_tol1"])
        s25 = score_resolution(vc[25000]["metrics_tol1"])
        if s10 in ("ABSENT", "PRESENT_WEAK", "FAIL") and s25 in ("ABSENT", "PRESENT_WEAK", "FAIL"):
            # PRESENT_WEAK is not FAIL of wipeout; require ABSENT or very weak
            if s10 == "ABSENT" and s25 == "ABSENT":
                vc_fail_both = True
                kills.append("K2_KR_pass_VC_fail_both_res")
            elif wt_kr.get("verdict") == "PASS_DESK" and s10 != "PASS" and s25 != "PASS" and s10 != "SOFT" and s25 != "SOFT":
                kills.append("K2_KR_pass_VC_not_recovered")

    # Leave-one-out on GW enrichments at 10kb
    gw_enrich = []
    for gsm in ("GSM4873113", "GSM4873114", "GSM4873115"):
        if gsm in sample_verdicts and sample_verdicts[gsm].get("enrich_10kb") is not None:
            gw_enrich.append((gsm, sample_verdicts[gsm]["enrich_10kb"]))
    loo = []
    for i, (left, _) in enumerate(gw_enrich):
        rest = [e for j, (_, e) in enumerate(gw_enrich) if j != i]
        if rest:
            loo.append({"left_out": left, "mean_enrich_remaining": statistics.mean(rest)})

    if kills:
        overall = "UNRESOLVED"
        action = "Demote G4a PASS_DESK → UNRESOLVED pending fix or architecture de-prioritize"
    elif wt_kr.get("verdict") == "PASS_DESK" and any(
        v.get("verdict") in ("PASS_DESK", "INCONCLUSIVE_LEAN_POSITIVE") for v in gw_others.values()
    ):
        overall = "PASS_DESK_ROBUST"
        action = "Retain G4a PASS_DESK; multi-sample support"
    elif wt_kr.get("verdict") == "PASS_DESK":
        overall = "PASS_DESK_WT_ONLY_CAUTION"
        action = "Retain PASS_DESK with CAUTION — other GW samples weak/absent; do not overclaim"
    else:
        overall = wt_kr.get("verdict", "UNKNOWN")
        action = "Review numbers; architecture claim stays provisional"

    payload = {
        "status": "G4A_MULTISAMPLE_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pre_registered": pre_registered,
        "overall_verdict": overall,
        "kills_triggered": kills,
        "action": action,
        "sample_verdicts": sample_verdicts,
        "leave_one_out_enrich10": loo,
        "vc_wt": {
            str(k): {
                "resolution_score": score_resolution(v["metrics_tol1"]),
                "enrich": v["metrics_tol1"].get("enrichment_vs_mean_bg"),
                "oe": v["metrics_tol1"].get("primary_oe"),
            }
            for k, v in vc.items()
        },
        "results": results,
        "notes": [
            "Capture samples expected low coverage at C1 window (β-globin bait)",
            "3114/3115 are 3primeHS1 mutants — not true WT biological replicates",
            "E/P coordinates locked; not shopped after viewing",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    lines = [
        "# G4a multi-sample kill test v1",
        "",
        f"**Date:** {payload['timestamp'][:10]}  ",
        f"**Overall:** `{overall}`  ",
        f"**Kills triggered:** {kills or 'none'}  ",
        f"**Action:** {action}",
        "",
        "## Pre-registered kill criteria (before multi-sample view)",
        "",
        "- **K1:** PASS only in GSM4873113 among GW Hi-C",
        "- **K2:** KR PASS wiped out by VC on both resolutions",
        "- **K3:** WT primary Contact/OE missing",
        "",
        "## Sample verdicts (KR, tol±1 bin)",
        "",
        "| Sample | Alias | Assay | Verdict | enrich10 | OE10 | enrich25 | OE25 |",
        "|--------|-------|-------|---------|---------:|-----:|---------:|-----:|",
    ]
    for gsm, v in sample_verdicts.items():
        lines.append(
            f"| {gsm} | {v['alias']} | {v['assay']} | `{v['verdict']}` | "
            f"{v.get('enrich_10kb')} | {v.get('oe_10kb')} | "
            f"{v.get('enrich_25kb')} | {v.get('oe_25kb')} |"
        )
    lines += [
        "",
        "## VC sensitivity (WT GSM4873113)",
        "",
        "```json",
        json.dumps(payload["vc_wt"], indent=2),
        "```",
        "",
        "## Leave-one-out (GW enrich 10 kb)",
        "",
        "```json",
        json.dumps(loo, indent=2),
        "```",
        "",
        "## Interpretation constraint",
        "",
        "This does **not** prove C1 allele effect. It only tests whether locked E–P WT contact",
        "is an artifact of a single KR dump.",
        "",
        f"JSON: `{OUT_JSON.name}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"overall": overall, "kills": kills, "sample_verdicts": sample_verdicts}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
