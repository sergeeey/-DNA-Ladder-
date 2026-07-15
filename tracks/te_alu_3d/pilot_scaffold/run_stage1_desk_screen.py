#!/usr/bin/env python3
"""Stage-1 prospective panel desk-screen (non-holdout).

Expands CTCF×Alu/SVA rare SNV pool via gnomAD, merges prior AG scores,
scores PWM locally (UCSC fasta windows), applies GATE G0–G8 desk logic,
writes pool + proposed frozen panel. Does NOT touch holdout. Does NOT wet-lab.

Usage:
  python run_stage1_desk_screen.py --limit 28
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from ctcf_pwm_scorer import ctcf_pwm_disruption
from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed
from qc_filters import VariantRecord
from run_ag_cultivation_r4 import (
    CTCF,
    EXCLUDE,
    TE,
    _excluded,
    _load_bed,
    build_panel,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "09_outputs" / "prospective"
DATA = ROOT / "data"
PRIOR_AG = OUT / "ag_cultivation_r4_scores.tsv"
TMP_FA = DATA / "cultivation" / "stage1_tmp_windows"


def _ucsc_seq(chrom: str, start0: int, end0: int) -> str:
    url = (
        "https://api.genome.ucsc.edu/getData/sequence"
        f"?genome=hg38;chrom={chrom};start={start0};end={end0}"
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    seq = data.get("dna") or data.get("sequence")
    if not seq:
        raise RuntimeError(f"no DNA {chrom}:{start0}-{end0}")
    return seq.upper()


def _write_window_fa(chrom: str, pos: int, half: int = 200) -> Path:
    start0 = max(0, pos - 1 - half)
    end0 = pos - 1 + half
    seq = _ucsc_seq(chrom, start0, end0)
    TMP_FA.mkdir(parents=True, exist_ok=True)
    path = TMP_FA / f"{chrom}_{start0}_{end0}.fa"
    # 1-based header for PWM scorer convention chr:start-end
    path.write_text(f">{chrom}:{start0 + 1}-{end0}\n{seq}\n", encoding="utf-8")
    return path


def _load_prior_ag() -> dict[str, dict]:
    if not PRIOR_AG.exists():
        return {}
    out: dict[str, dict] = {}
    with PRIOR_AG.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            out[row["variant_id"]] = row
    return out


def _pam_editability(seq_around: str, pos_in_seq: int, ref: str, alt: str) -> dict:
    """Crude SpCas9 PE/BE desk flags on ±40 bp window."""
    s = seq_around.upper()
    # BE windows: C→T or A→G typical — flag if alt suggests
    be_chem = None
    if ref.upper() == "C" and alt.upper() == "T":
        be_chem = "CBE"
    elif ref.upper() == "A" and alt.upper() == "G":
        be_chem = "ABE"
    pe_spacers = []
    # search NGG PAMs such that cut is within 30 bp of variant
    for i in range(max(0, pos_in_seq - 40), min(len(s) - 3, pos_in_seq + 40)):
        if s[i + 1 : i + 3] == "GG":  # NGG with N at i
            # spacer ends at i-1, cut between spacer end and PAM (~3 bp upstream of PAM N)
            cut = i - 3
            dist = abs(cut - pos_in_seq)
            if dist <= 30:
                pe_spacers.append({"pam_i": i, "cut_dist": dist, "strand": "+"})
        # reverse NGG: CCN
        if i >= 2 and s[i - 2 : i] == "CC":
            cut = i + 3
            dist = abs(cut - pos_in_seq)
            if dist <= 30:
                pe_spacers.append({"pam_i": i, "cut_dist": dist, "strand": "-"})
    be_ok = False
    if be_chem and pe_spacers:
        # classic BE often wants edit in positions 4-8 of spacer — mark CONDITIONAL
        be_ok = any(4 <= abs(p["cut_dist"] - 17) <= 8 for p in pe_spacers)  # rough
    return {
        "be_chemistry": be_chem,
        "be_desk": "CONDITIONAL" if be_ok else ("UNLIKELY" if be_chem else "N/A"),
        "pe_geometries": len(pe_spacers),
        "pe_desk": "PASS_DESK" if pe_spacers else "FAIL_DESK",
        "best_pe_cut_dist": min((p["cut_dist"] for p in pe_spacers), default=None),
    }


def _mechanism_prior(row: dict) -> str:
    chip = row.get("ag_chip_tf_mae")
    contact = row.get("ag_contact_mae")
    pwm = row.get("pwm_delta_logodds")
    try:
        chip_f = float(chip) if chip not in (None, "", "nan") else None
    except ValueError:
        chip_f = None
    try:
        contact_f = float(contact) if contact not in (None, "", "nan") else None
    except ValueError:
        contact_f = None
    try:
        pwm_f = float(pwm) if pwm not in (None, "", "nan") else None
    except ValueError:
        pwm_f = None

    # Prefer AG channel when present (C1-style)
    if chip_f is not None and contact_f is not None:
        if chip_f >= 0.2 and (contact_f is None or chip_f > 50 * contact_f):
            return "M3_activity"
        if contact_f >= 0.002 and (chip_f is None or contact_f * 50 > chip_f):
            return "M1_architecture_lean"
        if chip_f >= 0.15:
            return "M3_activity"
        if contact_f >= 0.0015:
            return "M1_architecture_lean"
    if pwm_f is not None and abs(pwm_f) >= 0.5:
        return "M1_motif_lean"
    if row.get("dist_ctcf") is not None and int(row["dist_ctcf"]) <= 50:
        return "M1_or_M3_near_CTCF"
    return "UNSPECIFIED"


def _candidate_class(mech: str, row: dict) -> str:
    has_ag = row.get("ag_status") == "SCORED"
    pwm = row.get("pwm_delta_logodds")
    try:
        pwm_f = float(pwm) if pwm not in (None, "", "nan") else 0.0
    except ValueError:
        pwm_f = 0.0
    chip = 0.0
    try:
        chip = float(row.get("ag_chip_tf_mae") or 0)
    except ValueError:
        pass
    if mech.startswith("M1") and has_ag and chip < 0.15 and abs(pwm_f) < 0.3:
        return "principled_disagreement_candidate"
    if mech.startswith("M3") and has_ag:
        return "convergence"
    if mech.startswith("M1"):
        return "architecture_prior"
    if "near_CTCF" in mech:
        return "near_anchor_untyped"
    return "computational"


def _gates(row: dict) -> dict:
    g = {}
    # G0
    g["G0"] = {
        "pass": True,
        "note": "gnomAD r4 SNV; chr11; exclude holdout/HBB applied at build",
    }
    # G1
    g["G1"] = {"pass": True, "note": "HUDEP-2 CTCF peak context (intended cell)"}
    # G2
    d_raw = row.get("dist_ctcf")
    d = 9999 if d_raw is None else int(d_raw)
    g["G2"] = {
        "pass": d <= 250,
        "note": f"dist_ctcf={d}; WT CTCF peak present; allele contact NOT measured",
    }
    # G3
    mech = row.get("mechanism_prior") or "UNSPECIFIED"
    g["G3"] = {
        "pass": mech != "UNSPECIFIED",
        "note": mech,
    }
    # G4
    g["G4"] = {
        "pass": True,
        "note": "no ClinVar; holdout sealed/unscored; AG optional overlay only",
    }
    # G5
    pe = row.get("pe_desk")
    g["G5"] = {
        "pass": pe == "PASS_DESK",
        "note": f"pe={pe}; be={row.get('be_desk')}; geometries={row.get('pe_geometries')}",
    }
    # G6 — matched controls feasible for panel as a whole, not per-variant
    g["G6"] = {
        "pass": True,
        "note": "panel-level; N3 KEEP available; N1/N2 need reselect",
    }
    # G7
    direction = "UNKNOWN_contact; activity_decrease_if_M3" if mech.startswith("M3") else "UNKNOWN_do_not_preclaim"
    g["G7"] = {
        "pass": True,
        "note": f"direction={direction}; MCID inherit C1 template if Stage3",
    }
    # G8 — freeze only if admitted to frozen panel later
    g["G8"] = {
        "pass": False,
        "note": "claim coords not frozen until frozen_panel admission",
    }
    hard = all(g[k]["pass"] for k in ["G0", "G1", "G2", "G4", "G5", "G6", "G7"])
    soft_mech = g["G3"]["pass"]
    if hard and soft_mech:
        admission = "FROZEN_PANEL_CANDIDATE"
    elif hard and not soft_mech:
        admission = "COMPUTATIONAL_ONLY"
    elif g["G2"]["pass"] and g["G0"]["pass"]:
        admission = "DESK_POOL_KEEP"
    else:
        admission = "REJECT"
    return {"gates": g, "admission": admission}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=28)
    ap.add_argument("--max-af", type=float, default=0.001)
    ap.add_argument("--max-dist", type=int, default=250)
    ap.add_argument("--skip-fetch", action="store_true", help="reuse stage1_pool_raw.json")
    args = ap.parse_args()

    assert holdout_is_sealed()
    assert_not_scoring_holdout(DATA / "cultivation" / "stage1_ok.tsv")
    (DATA / "cultivation").mkdir(parents=True, exist_ok=True)

    prior = _load_prior_ag()
    raw_path = DATA / "cultivation" / "stage1_pool_raw.json"

    if args.skip_fetch and raw_path.exists():
        panel = json.loads(raw_path.read_text(encoding="utf-8"))
        print(f"reuse raw panel n={len(panel)}")
    else:
        ctcf = _load_bed(CTCF)
        te = _load_bed(TE)
        print("building gnomAD panel…")
        panel = build_panel(
            ctcf, te, max_af=args.max_af, max_dist=args.max_dist, limit=args.limit
        )
        # ensure prior AG variants included even if not in new draw
        seen = {p["variant_id"] for p in panel}
        for vid, row in prior.items():
            if vid in seen:
                continue
            if _excluded(int(row["pos"])):
                continue
            panel.append(
                {
                    "chrom": "chr11",
                    "pos": int(row["pos"]),
                    "ref": row["ref"],
                    "alt": row["alt"],
                    "af": float(row["af"]) if row.get("af") not in ("", None) else None,
                    "te_family": row.get("te_family"),
                    "dist_ctcf": int(float(row["dist_ctcf"])),
                    "distance_score": float(row.get("distance_score") or 0),
                    "peak_mid": int(float(row["peak_mid"])) if row.get("peak_mid") else None,
                    "variant_id": vid,
                    "source": "prior_ag_merge",
                }
            )
            seen.add(vid)
        raw_path.write_text(json.dumps(panel, indent=2), encoding="utf-8")
        print(f"raw panel n={len(panel)}")

    peaks = CTCF
    rows = []
    for i, p in enumerate(panel, 1):
        vid = p["variant_id"]
        print(f"[{i}/{len(panel)}] {vid}", flush=True)
        assert not _excluded(p["pos"])
        row = dict(p)
        ag = prior.get(vid)
        if ag and ag.get("status") == "SCORED":
            row["ag_status"] = "SCORED"
            row["ag_contact_mae"] = ag.get("contact_mae_all")
            row["ag_chip_tf_mae"] = ag.get("chip_tf_mae")
            row["ag_primary_score"] = ag.get("primary_score")
        else:
            row["ag_status"] = "ABSENT"
            row["ag_contact_mae"] = None
            row["ag_chip_tf_mae"] = None
            row["ag_primary_score"] = None

        # PWM via UCSC window
        try:
            fa = _write_window_fa("chr11", int(p["pos"]), half=200)
            v = VariantRecord(chrom="chr11", pos=int(p["pos"]), ref=p["ref"], alt=p["alt"])
            pwm = ctcf_pwm_disruption(
                v.chrom, v.pos, v.ref, v.alt, fasta_path=fa, peaks_path=peaks
            )
            row["pwm_delta_logodds"] = pwm.get("delta_logodds")
            row["pwm_error"] = pwm.get("error")
            seq = fa.read_text(encoding="utf-8").splitlines()[1]
            # pos in window: header start is 1-based
            hdr = fa.read_text(encoding="utf-8").splitlines()[0][1:]
            start1 = int(hdr.split(":")[1].split("-")[0])
            pos_in = int(p["pos"]) - start1
            edit = _pam_editability(seq, pos_in, p["ref"], p["alt"])
            row.update(edit)
            time.sleep(0.15)
        except Exception as exc:
            row["pwm_delta_logodds"] = None
            row["pwm_error"] = f"{type(exc).__name__}: {exc}"
            row["pe_desk"] = "UNKNOWN"
            row["be_desk"] = "UNKNOWN"
            row["pe_geometries"] = 0

        row["mechanism_prior"] = _mechanism_prior(row)
        row["candidate_class"] = _candidate_class(row["mechanism_prior"], row)
        gate = _gates(row)
        row["admission"] = gate["admission"]
        row["gates"] = gate["gates"]
        rows.append(row)

    # Rank for frozen proposal
    def rank_key(r):
        adm = r["admission"]
        adm_score = {"FROZEN_PANEL_CANDIDATE": 3, "DESK_POOL_KEEP": 2, "COMPUTATIONAL_ONLY": 1}.get(
            adm, 0
        )
        try:
            ag = float(r.get("ag_primary_score") or 0)
        except (TypeError, ValueError):
            ag = 0.0
        try:
            pwm = abs(float(r.get("pwm_delta_logodds") or 0))
        except (TypeError, ValueError):
            pwm = 0.0
        dist = 1.0 / (1.0 + float(r.get("dist_ctcf") or 999))
        return (adm_score, ag, pwm, dist)

    rows.sort(key=rank_key, reverse=True)

    # Propose frozen panel composition per protocol
    template = [r for r in rows if r["variant_id"] == "chr11:62753923:A:G"]
    act = [
        r
        for r in rows
        if r["admission"] == "FROZEN_PANEL_CANDIDATE"
        and r["candidate_class"] in ("convergence",)
        and r["variant_id"] != "chr11:62753923:A:G"
    ]
    arch = [
        r
        for r in rows
        if r["admission"] == "FROZEN_PANEL_CANDIDATE"
        and r["candidate_class"]
        in ("architecture_prior", "principled_disagreement_candidate", "near_anchor_untyped")
    ]
    # disagreement
    disag = [r for r in rows if r["candidate_class"] == "principled_disagreement_candidate"]
    # negatives: low AG + pe ok from prior N3 family or bottom scores
    neg_keep = [r for r in rows if r["variant_id"] == "chr11:108009167:T:C"]
    neg_extra = [
        r
        for r in rows
        if r.get("ag_status") == "SCORED"
        and float(r.get("ag_primary_score") or 99) < 0.001
        and r["pe_desk"] == "PASS_DESK"
        and r["variant_id"] not in {x["variant_id"] for x in neg_keep}
    ]

    frozen = []
    used = set()

    def take(label, lst, n):
        for r in lst:
            if r["variant_id"] in used:
                continue
            frozen.append({**r, "frozen_role": label})
            used.add(r["variant_id"])
            if sum(1 for x in frozen if x["frozen_role"] == label) >= n:
                break

    if template:
        take("TEMPLATE_DEV", template, 1)
    take("activity_m3", act, 4)
    take("architecture_m1", arch, 4)
    take("principled_disagreement", disag, 2)
    take("matched_negative", neg_keep + neg_extra, 3)

    # fill to at least 8 with next FROZEN candidates
    for r in rows:
        if len(frozen) >= 10:
            break
        if r["variant_id"] in used:
            continue
        if r["admission"] != "FROZEN_PANEL_CANDIDATE":
            continue
        take("activity_m3" if r["mechanism_prior"].startswith("M3") else "architecture_m1", [r], 1)

    # Stage-3 preregister proposal (IDs only — lock before Stage2)
    stage3 = {
        "architecture_strong_1": None,
        "architecture_strong_2": None,
        "convergence_1": None,
        "disagreement_1": None,
        "negative_1": None,
        "assignment_locked": False,
        "note": "PROPOSED from Stage-1 ranks; LOCK before any reporter readout",
    }
    arch_slots = [x for x in frozen if x["frozen_role"] in ("architecture_m1", "principled_disagreement")]
    conv_slots = [x for x in frozen if x["frozen_role"] in ("activity_m3", "TEMPLATE_DEV")]
    neg_slots = [x for x in frozen if x["frozen_role"] == "matched_negative"]
    if len(arch_slots) >= 1:
        stage3["architecture_strong_1"] = arch_slots[0]["variant_id"]
    if len(arch_slots) >= 2:
        stage3["architecture_strong_2"] = arch_slots[1]["variant_id"]
    if conv_slots:
        # prefer non-C1 for convergence stage3 if available
        non_c1 = [x for x in conv_slots if x["frozen_role"] != "TEMPLATE_DEV"]
        stage3["convergence_1"] = (non_c1[0] if non_c1 else conv_slots[0])["variant_id"]
    disag_f = [x for x in frozen if x["frozen_role"] == "principled_disagreement"]
    if disag_f:
        stage3["disagreement_1"] = disag_f[0]["variant_id"]
    elif arch_slots:
        stage3["disagreement_1"] = arch_slots[-1]["variant_id"]
    if neg_slots:
        stage3["negative_1"] = neg_slots[0]["variant_id"]

    report = {
        "status": "STAGE1_DESK_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "holdout_sealed": True,
        "ag_api": "ABSENT_this_run",
        "n_pool": len(rows),
        "n_frozen_proposed": len(frozen),
        "exclude_windows": [{"start": a, "end": b, "reason": r} for a, b, r in EXCLUDE],
        "admission_counts": {},
        "frozen_panel": [
            {
                "frozen_role": x["frozen_role"],
                "variant_id": x["variant_id"],
                "mechanism_prior": x["mechanism_prior"],
                "candidate_class": x["candidate_class"],
                "admission": x["admission"],
                "dist_ctcf": x.get("dist_ctcf"),
                "te_family": x.get("te_family"),
                "ag_contact_mae": x.get("ag_contact_mae"),
                "ag_chip_tf_mae": x.get("ag_chip_tf_mae"),
                "pwm_delta_logodds": x.get("pwm_delta_logodds"),
                "pe_desk": x.get("pe_desk"),
            }
            for x in frozen
        ],
        "stage3_advancement_proposed": stage3,
        "pool": rows,
    }
    from collections import Counter

    report["admission_counts"] = dict(Counter(r["admission"] for r in rows))

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "stage1_desk_screen_v1.json"
    # slim pool for JSON size: drop full gate detail duplication ok keep
    out_json.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    tsv = OUT / "stage1_desk_screen_v1.tsv"
    fields = [
        "variant_id",
        "pos",
        "ref",
        "alt",
        "af",
        "te_family",
        "dist_ctcf",
        "mechanism_prior",
        "candidate_class",
        "admission",
        "ag_status",
        "ag_contact_mae",
        "ag_chip_tf_mae",
        "pwm_delta_logodds",
        "pe_desk",
        "be_desk",
        "pe_geometries",
    ]
    with tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(json.dumps({"n_pool": len(rows), "n_frozen": len(frozen), "stage3": stage3}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
