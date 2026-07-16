#!/usr/bin/env python3
"""P4 — independent model matrix for frozen prospective panel (desk).

Reuses stage1 AG + PWM fields; motif/distance baselines; G4a WT contact for C1.
Does not call AlphaGenome API. Does not unseal holdout. Does not move E/P.
"""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
PS = ROOT / "pilot_scaffold"
DATA = PS / "data"
PEAKS = DATA / "ctcf_HUDEP2_peaks.bed"

STAGE1_TSV = OUT / "stage1_desk_screen_v1.tsv"
REGISTRY = OUT / "prospective_panel_registry_v1.yaml"
G4A = OUT / "G4a_multisample_kill_test_v1.md"

# Locked thresholds (claim)
MOTIF_HIGH = 0.5
MOTIF_LOW = 0.2
ACT_HIGH = 0.20
ACT_LOW = 0.12
CONTACT_HIGH = 0.002


def motif_only_from_delta(delta: float | None) -> float | None:
    if delta is None:
        return None
    if delta >= 0:
        score = 1.0 - math.exp(-0.5 * delta)
    else:
        score = 0.5 * math.exp(0.5 * delta)
    return float(max(0.0, min(1.0, score)))


def distance_only(dist: int | None) -> float | None:
    if dist is None:
        return None
    return float(1.0 / (1.0 + float(dist)))


def fnum(x) -> float | None:
    if x is None or x == "" or x == "None":
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def classify(row: dict) -> str:
    role = row.get("role") or ""
    motif = row.get("motif_only")
    act = row.get("ag_chip_tf_mae")
    cont = row.get("ag_contact_mae")
    wt = row.get("wt_contact_status")

    if act is None and motif is None:
        return "incomplete"

    motif_high = motif is not None and motif >= MOTIF_HIGH
    motif_low = motif is not None and motif < MOTIF_LOW
    act_high = act is not None and act >= ACT_HIGH
    act_low = act is not None and act < ACT_LOW
    cont_high = cont is not None and cont >= CONTACT_HIGH
    wt_pass = isinstance(wt, str) and wt.startswith("PASS")

    if "matched_negative" in role and act_low and not motif_high:
        return "negative_consistent"

    positives = sum([motif_high, act_high, cont_high])
    if positives >= 2 or (act_high and wt_pass):
        return "convergence"
    if motif_high ^ act_high:
        mech = row.get("mechanism_prior") or ""
        if mech.startswith("M1") or mech.startswith("M3") or "disagreement" in role:
            return "principled_disagreement"
        return "unsupported"
    if positives == 1 and not wt_pass:
        return "unsupported"
    if positives == 0:
        if "matched_negative" in role:
            return "negative_consistent"
        return "unsupported"
    return "incomplete"


def main() -> int:
    if not STAGE1_TSV.is_file() or not REGISTRY.is_file():
        payload = {"status": "P4_BLOCKED", "label": "P4_BLOCKED", "error": "missing stage1/registry"}
        (OUT / "P4_independent_model_matrix_v1.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    slots = [s for s in (reg.get("slots") or []) if s.get("variant_id") and not str(s["variant_id"]).startswith("P1_")]
    with STAGE1_TSV.open(encoding="utf-8") as fh:
        stage_by = {r["variant_id"]: r for r in csv.DictReader(fh, delimiter="\t")}

    g4a_txt = G4A.read_text(encoding="utf-8") if G4A.is_file() else ""
    c1_wt = "PASS_DESK_ROBUST" if "PASS_DESK_ROBUST" in g4a_txt else ("PASS_DESK" if "PASS_DESK" in g4a_txt else "UNAVAILABLE")

    rows: list[dict] = []
    incomplete = 0
    for s in slots:
        vid = s["variant_id"]
        st = stage_by.get(vid) or {}
        pwm = fnum(st.get("pwm_delta_logodds"))
        motif = motif_only_from_delta(pwm)
        dist_ctcf = None
        if st.get("dist_ctcf") not in (None, ""):
            try:
                dist_ctcf = int(float(st["dist_ctcf"]))
            except ValueError:
                dist_ctcf = None
        act = fnum(st.get("ag_chip_tf_mae"))
        cont = fnum(st.get("ag_contact_mae"))
        wt = c1_wt if vid == "chr11:62753923:A:G" else "NOT_MEASURED_FOR_THIS_ALLELE"

        row = {
            "candidate_id": s.get("candidate_id"),
            "slot_id": s.get("slot_id"),
            "role": s.get("role"),
            "registry_class": s.get("class"),
            "variant_id": vid,
            "archcode": {
                "status": "UNAVAILABLE_EXPLORATORY_PRIOR_ONLY",
                "mechanism_prior_lean": st.get("mechanism_prior") or s.get("class"),
                "note": "Not an independent validation score",
            },
            "motif_only": motif,
            "pwm_delta_logodds": pwm,
            "distance_only": distance_only(dist_ctcf),
            "dist_ctcf": dist_ctcf,
            "activity_prediction_ag_chip_tf": act,
            "ag_chip_tf_mae": act,
            "alphagenome_contact_mae": cont,
            "ag_contact_mae": cont,
            "wt_contact_status": wt,
            "mechanism_prior": st.get("mechanism_prior") or s.get("class"),
            "flags": {
                "motif_high": motif is not None and motif >= MOTIF_HIGH,
                "motif_low": motif is not None and motif < MOTIF_LOW,
                "activity_high": act is not None and act >= ACT_HIGH,
                "activity_low": act is not None and act < ACT_LOW,
                "ag_contact_high": cont is not None and cont >= CONTACT_HIGH,
            },
        }
        row["p4_class"] = classify(row)
        if row["p4_class"] == "incomplete":
            incomplete += 1
        rows.append(row)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["p4_class"]] = counts.get(r["p4_class"], 0) + 1

    label = "P4_MATRIX_COMPLETE" if incomplete == 0 else "P4_PARTIAL"

    # independence honesty notes
    indep = {
        "AlphaGenome_CHIP_TF_vs_contact": "SAME_MODEL_FAMILY — not independent lines",
        "motif_only_vs_distance_only": "SHARED_CTCF_PEAK_LAYER — partially dependent",
        "ARCHCODE": "NOT_RUN — exploratory prior lean only",
        "WT_HiC_G4a": "INDEPENDENT_OBSERVATIONAL for C1 E–P only",
        "panel_note": "Multi-model agreement ≠ wet-lab proof; correlated sequence nets ≠ Arm A gold",
    }

    payload = {
        "status": "P4_INDEPENDENT_MODEL_COMPLETE",
        "label": label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim": "P4_INDEPENDENT_MODEL_CLAIM_v1.md",
        "thresholds": {
            "motif_high": MOTIF_HIGH,
            "motif_low": MOTIF_LOW,
            "activity_high": ACT_HIGH,
            "activity_low": ACT_LOW,
            "ag_contact_high": CONTACT_HIGH,
        },
        "independence_notes": indep,
        "n_alleles": len(rows),
        "class_counts": counts,
        "rows": rows,
        "peaks_path_used_for_dist_field": str(PEAKS.relative_to(ROOT)) if PEAKS.is_file() else None,
    }

    (OUT / "P4_independent_model_matrix_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    table = []
    for r in rows:
        def fmt(x, nd=3):
            return f"{x:.{nd}f}" if isinstance(x, float) else "—"

        table.append(
            f"| {r.get('candidate_id') or '—'} | `{r['variant_id']}` | {r['role']} | "
            f"**{r['p4_class']}** | {fmt(r['motif_only'])} | {fmt(r['distance_only'])} | "
            f"{fmt(r['ag_chip_tf_mae'])} | {fmt(r['ag_contact_mae'], 4)} | {r['wt_contact_status']} |"
        )

    count_lines = "\n".join(f"| `{k}` | {v} |" for k, v in sorted(counts.items()))

    md = f"""# P4 — Independent model matrix v1

**Date:** 2026-07-16
**Status:** `P4_INDEPENDENT_MODEL_COMPLETE`
**Claim:** `P4_INDEPENDENT_MODEL_CLAIM_v1.md`
**Label:** **`{label}`**
**Alleles:** {len(rows)} (P1 system control excluded — not an SNV row)

## Class counts

| Class | n |
|-------|--:|
{count_lines}

## Matrix

| ID | Variant | Role | P4 class | Motif | Dist | AG CHIP | AG contact | WT contact |
|----|---------|------|----------|------:|-----:|--------:|-----------:|------------|
{chr(10).join(table)}

## Independence honesty

| Pair | Note |
|------|------|
| AG CHIP vs AG contact | **same model family** — not independent evidence |
| Motif vs distance | share CTCF peak layer — partially dependent |
| ARCHCODE | **UNAVAILABLE** — exploratory prior lean only |
| G4a WT Hi-C | independent observational for **C1 E–P only** |

## C1 reading

C1: high AG activity + low motif + WT contact PASS → typically **convergence** via activity+WT rule (not motif convergence).

## Plain language

Таблица «кто с кем согласен» по frozen-панели. Согласие моделей ≠ лаборатория. ARCHCODE здесь не валидатор.

## What this does NOT mean

- Not wet GO / not Stage-3 reshuffle
- Not ARCHCODE validation
- Not allele-specific contact proof (except C1 WT contact desk)

Full dump: `P4_independent_model_matrix_v1.json`
"""
    (OUT / "P4_independent_model_matrix_v1.md").write_text(md, encoding="utf-8")

    notes = f"""# P4 / G2b — independence notes (desk fill)

**Date:** 2026-07-16
**Related template:** `templates/G2b_model_independence_matrix.yaml` (still mostly empty for external nets)

## What we actually ran

| Model / track | Run status | Allele-Δ validated | Dependence |
|---------------|------------|--------------------|------------|
| AlphaGenome CHIP_TF | PRESENT (stage1) | desk MAE only | sequence net |
| AlphaGenome contact | PRESENT (stage1) | desk MAE only | **same net as CHIP_TF** |
| motif_only CTCF PWM | PRESENT | exploratory | shares peak layer with distance |
| distance_only | PRESENT | n/a | shares peak layer with motif |
| ARCHCODE | NOT_RUN | n/a | — |
| UniChrom / Hi-Compass / enhancer3D | NOT_RUN | — | — |
| HUDEP-2 WT Hi-C (G4a) | PRESENT for C1 E–P | observational | independent of sequence nets |

## Rule

Do not sell AG CHIP + AG contact as two independent votes.
"""
    (OUT / "P4_G2b_independence_notes_v1.md").write_text(notes, encoding="utf-8")

    print(
        json.dumps(
            {"label": label, "class_counts": counts, "n": len(rows), "c1": next((r["p4_class"] for r in rows if r["variant_id"].endswith("62753923:A:G")), None)},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
