#!/usr/bin/env python3
"""Curate Stage-1 results: fix G2 dist==0 bug; assemble frozen panel; lock Stage-3."""
from __future__ import annotations

import csv
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "09_outputs" / "prospective"
PATH = OUT / "stage1_desk_screen_v1.json"
TSV = OUT / "stage1_desk_screen_v1.tsv"

DROP_AS_ARCH = {"chr11:35821778:C:G", "chr11:35822097:A:T"}
N3 = "chr11:108009167:T:C"
C1 = "chr11:62753923:A:G"
C2 = "chr11:62753923:A:T"
C3 = "chr11:72434037:C:T"


def fix_gates(row: dict) -> None:
    d_raw = row.get("dist_ctcf")
    d = 9999 if d_raw is None else int(d_raw)
    g = row["gates"]
    g["G2"] = {
        "pass": d <= 250,
        "note": f"dist_ctcf={d}; WT CTCF peak present; allele contact NOT measured",
    }
    mech = row.get("mechanism_prior") or "UNSPECIFIED"
    g["G3"] = {"pass": mech != "UNSPECIFIED", "note": mech}
    hard = all(g[k]["pass"] for k in ["G0", "G1", "G2", "G4", "G5", "G6", "G7"])
    soft = g["G3"]["pass"]
    if hard and soft:
        adm = "FROZEN_PANEL_CANDIDATE"
    elif hard and not soft:
        adm = "COMPUTATIONAL_ONLY"
    elif g["G2"]["pass"] and g["G0"]["pass"]:
        adm = "DESK_POOL_KEEP"
    else:
        adm = "REJECT"
    row["admission"] = adm
    row["dist_ctcf"] = d


def main() -> None:
    r = json.loads(PATH.read_text(encoding="utf-8"))

    for p in r["pool"]:
        if p.get("ag_status") == "SCORED":
            chip = float(p.get("ag_chip_tf_mae") or 0)
            contact = float(p.get("ag_contact_mae") or 0)
            if chip >= 0.2:
                p["mechanism_prior"] = "M3_activity"
                p["candidate_class"] = "convergence"
            elif contact >= 0.0015 and chip < 0.15:
                p["mechanism_prior"] = "M1_architecture_lean"
                p["candidate_class"] = "principled_disagreement_candidate"
            elif contact < 0.0012 and chip < 0.12:
                if p["variant_id"] in (N3, "chr11:108009167:T:A"):
                    p["mechanism_prior"] = "M0_neutral_lean"
                    p["candidate_class"] = "matched_negative_candidate"
        fix_gates(p)

    by_id = {p["variant_id"]: p for p in r["pool"]}
    frozen: list[dict] = []
    used: set[str] = set()

    def add(role: str, vid: str, note: str = "") -> None:
        if vid in used:
            return
        p = deepcopy(by_id[vid])
        p["frozen_role"] = role
        p["curation_note"] = note
        # force admission for curated scientific inclusions
        p["admission"] = "FROZEN_PANEL_CANDIDATE"
        p["gates"]["G8"] = {
            "pass": True,
            "note": "coords/claim provisional-frozen at Stage-1 curated admission",
        }
        frozen.append(p)
        used.add(vid)

    add("TEMPLATE_DEV", C1, "desk template; M3 primary; G4b ready; not auto Stage-3 winner")
    add("activity_m3", C2, "same-site allelic amplitude vs C1")
    add("activity_m3", C3, "motif competitor / historical PWM strong")

    ag_m3 = sorted(
        [
            p
            for p in r["pool"]
            if p.get("ag_status") == "SCORED"
            and float(p.get("ag_chip_tf_mae") or 0) >= 0.15
            and p["variant_id"] not in {C1, C2, C3}
        ],
        key=lambda x: float(x.get("ag_chip_tf_mae") or 0),
        reverse=True,
    )
    for p in ag_m3[:2]:
        add("activity_m3", p["variant_id"], "AG CHIP_TF lean")

    arch_cands = [
        p
        for p in r["pool"]
        if p["admission"] == "FROZEN_PANEL_CANDIDATE"
        and p["variant_id"] not in used
        and p["variant_id"] not in DROP_AS_ARCH
        and not (
            p.get("ag_status") == "SCORED" and float(p.get("ag_chip_tf_mae") or 0) >= 0.2
        )
    ]
    seen_pos: set[int] = set()
    arch_pick: list[dict] = []
    for p in sorted(
        arch_cands,
        key=lambda x: (
            0 if x.get("ag_status") != "SCORED" else 1,
            -abs(float(x.get("pwm_delta_logodds") or 0)),
        ),
    ):
        if p["pos"] in seen_pos:
            continue
        seen_pos.add(p["pos"])
        arch_pick.append(p)
        if len(arch_pick) >= 4:
            break
    for p in arch_pick:
        add(
            "architecture_m1",
            p["variant_id"],
            "Stage1 motif/anchor prior; allele contact untested",
        )

    add("matched_negative", N3, "G6 KEEP; GC+ATAC matched vs C1")
    if "chr11:108009167:T:A" in by_id:
        add(
            "matched_negative",
            "chr11:108009167:T:A",
            "same-locus allelic negative companion",
        )

    frozen.append(
        {
            "frozen_role": "known_positive",
            "variant_id": "P1_SYSTEM_3primeHS1",
            "mechanism_prior": "M1_architecture_control",
            "candidate_class": "known_positive",
            "admission": "FROZEN_PANEL_CANDIDATE",
            "curation_note": "Historical HUDEP-2 3primeHS1 del/inv PASS_DESK; not an Alu SNV",
            "pe_desk": "N/A_system_control",
            "dist_ctcf": None,
            "te_family": None,
            "ag_contact_mae": None,
            "ag_chip_tf_mae": None,
            "pwm_delta_logodds": None,
        }
    )

    disag = [
        p
        for p in r["pool"]
        if p.get("candidate_class") == "principled_disagreement_candidate"
        and p["variant_id"] not in used
    ]
    if not disag:
        disag = [
            p
            for p in r["pool"]
            if p.get("ag_status") == "SCORED"
            and float(p.get("ag_chip_tf_mae") or 0) < 0.15
            and float(p.get("ag_contact_mae") or 0) >= 0.0010
            and p["variant_id"] not in used
            and p["variant_id"] not in DROP_AS_ARCH
        ]
    if disag:
        d0 = sorted(disag, key=lambda x: float(x.get("ag_contact_mae") or 0), reverse=True)[0]
        add(
            "principled_disagreement",
            d0["variant_id"],
            "contact vs activity channel tension (pre-registered class)",
        )

    arch_ids = [x["variant_id"] for x in frozen if x["frozen_role"] == "architecture_m1"]
    disag_id = next(
        (x["variant_id"] for x in frozen if x["frozen_role"] == "principled_disagreement"),
        arch_ids[-1] if arch_ids else None,
    )
    stage3 = {
        "architecture_strong_1": arch_ids[0] if len(arch_ids) > 0 else None,
        "architecture_strong_2": arch_ids[1] if len(arch_ids) > 1 else None,
        "convergence_1": C3,
        "disagreement_1": disag_id,
        "negative_1": N3,
        "assignment_locked": True,
        "locked_date": "2026-07-15",
        "lock_rule": "LOCKED before Stage-2 reporter readout per SCALE_PROTOCOL",
        "template_excluded_from_stage3_slots": C1,
        "known_positive_assay_chain": "P1_SYSTEM_3primeHS1",
    }

    r["status"] = "STAGE1_DESK_COMPLETE_CURATED"
    r["admission_counts"] = dict(Counter(p["admission"] for p in r["pool"]))
    r["n_pool"] = len(r["pool"])
    r["n_frozen_proposed"] = len(frozen)
    keys = [
        "frozen_role",
        "variant_id",
        "mechanism_prior",
        "candidate_class",
        "admission",
        "dist_ctcf",
        "te_family",
        "ag_contact_mae",
        "ag_chip_tf_mae",
        "pwm_delta_logodds",
        "pe_desk",
        "curation_note",
    ]
    r["frozen_panel"] = [{k: x.get(k) for k in keys} for x in frozen]
    r["stage3_advancement_proposed"] = stage3
    r["curation"] = {
        "g2_bugfix": "dist_ctcf=0 was treated as missing via `0 or 9999`",
        "pwm_caveat": "many |delta|~4.09 — exploratory ordinal only; not Stage-3 decision sole input",
        "g6_drop_excluded_from_arch_strong": sorted(DROP_AS_ARCH),
        "ag_api_this_run": "ABSENT — used prior R4 AG overlay for 12 alleles",
    }

    PATH.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")

    fields = list(csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t").fieldnames or [])
    with TSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        for p in r["pool"]:
            w.writerow(p)

    print("adm", r["admission_counts"])
    print("n_frozen", len(frozen))
    for x in r["frozen_panel"]:
        print(x["frozen_role"], x["variant_id"], x.get("mechanism_prior"))
    print("stage3", json.dumps(stage3, indent=2))


if __name__ == "__main__":
    main()
