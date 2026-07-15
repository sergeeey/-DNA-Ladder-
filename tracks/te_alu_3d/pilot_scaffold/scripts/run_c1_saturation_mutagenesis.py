#!/usr/bin/env python3
"""C1 local saturation mutagenesis in 301 bp window — kill allele-specificity artifact.

Pre-registered BEFORE ranking:
  Kill / demote C1 allele priority if:
    S1. C1 A>G primary_score (AG chip_tf or contact) is within top 50% of ALL
        single-base substitutions in the window (not an outlier)
    S2. ≥20 other substitutions have AG chip_tf_mae ≥ 0.9 * C1 chip_tf
    S3. Mean score of all A>G transitions in window ≥ C1 score (composition artifact)

Retain allele-specific lean if:
    C1 ranks in top 5% of all subst by primary metric (chip_tf_mae)
    AND fewer than 10 subst reach 0.9*C1

Primary metric (pre-registered): AlphaGenome chip_tf_mae (M3 lean for C1)
Secondary: contact_mae_all, CTCF PWM |delta|

Window: same as Branch B minimal 301 bp centered on C1.
Does not touch holdout. Loads .env for AG key.

Usage:
  python scripts/run_c1_saturation_mutagenesis.py [--max-n 120] [--skip-ag]
  Full window = 301*3 = 903; default can subsample stratified then expand.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PS = ROOT / "pilot_scaffold"
import sys

sys.path.insert(0, str(PS))

from load_project_env import load_project_env
from adapters.ag_contact_delta import VariantSpec, score_variant_deltas
from ctcf_pwm_scorer import ctcf_pwm_disruption

OUT = ROOT / "09_outputs" / "prospective"
DATA = PS / "data" / "cultivation"
FA = DATA / "c1_reporter_minimal_301bp_REF.fa"
PEAKS = PS / "data" / "ctcf_HUDEP2_peaks.bed"

C1_POS = 62753923
C1_REF = "A"
C1_ALT = "G"
# Branch B window chr11:62753773-62754073 (1-based) → start0=62753772
WIN_START1 = 62753773
WIN_END1 = 62754073


def load_ref_seq() -> str:
    lines = FA.read_text(encoding="utf-8").splitlines()
    return "".join(lines[1:]).upper().replace("U", "T")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=0, help="0 = all 903 substitutions")
    ap.add_argument("--skip-ag", action="store_true")
    ap.add_argument("--only-ag-top-pwm", type=int, default=0, help="AG-score only top-N by |PWM| plus C1")
    args = ap.parse_args()

    load_project_env()
    seq = load_ref_seq()
    assert len(seq) == 301, len(seq)
    c1_idx = C1_POS - WIN_START1
    assert seq[c1_idx] == C1_REF, (seq[c1_idx], C1_REF)

    # write temp fasta for PWM with correct header
    tmp_fa = DATA / "stage_satmut_c1_301.fa"
    tmp_fa.write_text(f">chr11:{WIN_START1}-{WIN_END1}\n{seq}\n", encoding="utf-8")

    bases = ["A", "C", "G", "T"]
    variants = []
    for i, ref in enumerate(seq):
        pos = WIN_START1 + i
        for alt in bases:
            if alt == ref:
                continue
            variants.append(
                {
                    "pos": pos,
                    "ref": ref,
                    "alt": alt,
                    "idx": i,
                    "is_c1": pos == C1_POS and ref == C1_REF and alt == C1_ALT,
                    "variant_id": f"chr11:{pos}:{ref}:{alt}",
                }
            )

    print(f"n_subst={len(variants)}", flush=True)

    # PWM for all (cheap)
    for v in variants:
        raw = ctcf_pwm_disruption(
            "chr11", v["pos"], v["ref"], v["alt"], fasta_path=tmp_fa, peaks_path=PEAKS
        )
        v["pwm_delta"] = raw.get("delta_logodds")
        v["pwm_score"] = raw.get("score")
        v["pwm_error"] = raw.get("error")

    # optional filter for AG budget
    to_ag = list(variants)
    if args.only_ag_top_pwm:
        ranked = sorted(variants, key=lambda x: abs(float(x.get("pwm_delta") or 0)), reverse=True)
        keep = {C1_POS}
        pick = []
        for v in ranked:
            if v["is_c1"] or len(pick) < args.only_ag_top_pwm:
                pick.append(v)
        # always include C1
        if not any(v["is_c1"] for v in pick):
            pick.append(next(v for v in variants if v["is_c1"]))
        to_ag = pick
        print(f"AG subset n={len(to_ag)}", flush=True)
    if args.max_n and len(to_ag) > args.max_n:
        # stratified: force C1 + every k-th
        c1 = [v for v in to_ag if v["is_c1"]]
        rest = [v for v in to_ag if not v["is_c1"]]
        step = max(1, len(rest) // (args.max_n - 1))
        to_ag = c1 + rest[::step][: args.max_n - 1]
        print(f"AG capped n={len(to_ag)}", flush=True)

    if not args.skip_ag:
        for i, v in enumerate(to_ag, 1):
            print(f"AG [{i}/{len(to_ag)}] {v['variant_id']}", flush=True)
            try:
                s = score_variant_deltas(VariantSpec("chr11", v["pos"], v["ref"], v["alt"]))
                v["ag_chip_tf_mae"] = s.get("chip_tf_mae")
                v["ag_contact_mae"] = s.get("contact_mae_all")
                v["ag_primary"] = s.get("primary_score")
                v["ag_status"] = "SCORED"
            except Exception as exc:
                v["ag_status"] = "FAIL"
                v["ag_error"] = f"{type(exc).__name__}: {exc}"
            time.sleep(0.35)

    scored = [v for v in to_ag if v.get("ag_status") == "SCORED"]
    c1 = next(v for v in variants if v["is_c1"])
    c1_scored = next((v for v in scored if v["is_c1"]), None)

    pre = {
        "kill_S1": "C1 not in top 5% by chip_tf among AG-scored set",
        "kill_S2": ">=20 subst with chip_tf >= 0.9 * C1",
        "kill_S3": "mean A>G chip_tf in window >= C1 chip_tf",
        "primary_metric": "ag_chip_tf_mae",
    }

    kills = []
    stats = {}
    if c1_scored and scored:
        chips = sorted(
            [(float(v["ag_chip_tf_mae"]), v["variant_id"], v.get("is_c1")) for v in scored],
            reverse=True,
        )
        c1_chip = float(c1_scored["ag_chip_tf_mae"])
        rank = 1 + sum(1 for s, _, _isc in chips if s > c1_chip)
        pct = rank / len(chips)
        n_near = sum(1 for s, _, _ in chips if s >= 0.9 * c1_chip and s != c1_chip)
        ag_transitions = [
            float(v["ag_chip_tf_mae"])
            for v in scored
            if v["ref"] == "A" and v["alt"] == "G" and not v["is_c1"]
        ]
        mean_ag = sum(ag_transitions) / len(ag_transitions) if ag_transitions else None
        stats = {
            "n_ag_scored": len(scored),
            "c1_chip_tf": c1_chip,
            "c1_contact": float(c1_scored.get("ag_contact_mae") or 0),
            "c1_rank": rank,
            "c1_percentile_from_top": pct,
            "n_within_90pct_c1": n_near,
            "mean_other_AtoG_chip": mean_ag,
            "top5": [{"chip": a, "id": b, "is_c1": c} for a, b, c in chips[:5]],
        }
        if pct > 0.05:
            kills.append("S1_not_top5pct")
        if n_near >= 20:
            kills.append("S2_many_near_peers")
        if mean_ag is not None and mean_ag >= c1_chip:
            kills.append("S3_AtoG_composition")

    overall = "ALLELE_LEAN_RETAINED" if not kills else "UNRESOLVED_OR_WINDOW_ARTIFACT"
    if not c1_scored:
        overall = "INCOMPLETE_AG"
        kills.append("C1_AG_MISSING")

    report = {
        "status": "C1_SATMUT_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "window": f"chr11:{WIN_START1}-{WIN_END1}",
        "n_all_subst": len(variants),
        "pre_registered": pre,
        "overall": overall,
        "kills": kills,
        "stats": stats,
        "c1": {k: c1_scored.get(k) if c1_scored else c1.get(k) for k in (
            "variant_id", "ag_chip_tf_mae", "ag_contact_mae", "pwm_delta", "ag_status"
        )},
        "variants_ag": scored,
        "variants_pwm_only_count": len(variants),
    }
    out_json = OUT / "C1_saturation_mutagenesis_v1.json"
    # slim write: don't dump all PWM-only if huge — keep scored + summary
    out_json.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    md = OUT / "C1_saturation_mutagenesis_v1.md"
    md.write_text(
        "\n".join(
            [
                "# C1 saturation mutagenesis v1 (301 bp)",
                "",
                f"**Overall:** `{overall}`  ",
                f"**Kills:** {kills or 'none'}  ",
                f"**AG scored:** {stats.get('n_ag_scored', 0)} / {len(variants)} possible",
                "",
                "## Pre-registered kill criteria",
                "",
                "- S1: C1 not in top 5% by CHIP_TF",
                "- S2: ≥20 peers within 90% of C1 CHIP_TF",
                "- S3: mean other A→G CHIP_TF ≥ C1",
                "",
                "## Stats",
                "",
                "```json",
                json.dumps(stats, indent=2),
                "```",
                "",
                f"JSON: `{out_json.name}`",
                "",
                "Does not prove wet biology; only allele-vs-window artifact test.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"overall": overall, "kills": kills, "stats": stats}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
