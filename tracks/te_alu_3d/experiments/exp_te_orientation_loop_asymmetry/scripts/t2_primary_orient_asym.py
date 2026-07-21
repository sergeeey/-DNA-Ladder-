#!/usr/bin/env python3
"""C-J1 primary: TE insertion strand vs left/right Hi-C loop-anchor asymmetry.

Prereg: claim.md — |Δ_orient| = |p(+|left) − p(+|right)| ≥ 0.10 SUPPORT; <0.05 REJECT.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c_j1_lib import (  # noqa: E402
    MCID_KILL,
    MCID_SUPPORT,
    SEED,
    chrom_block_bootstrap_delta,
    fisher_or_woolf,
    load_bedpe_loops,
    load_te_strand_intervals,
    max_overlap_strand,
    verdict_abs_delta,
)

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"


def annotate_side(
    loops,
    te_by,
) -> tuple[list[tuple[str, int]], list[tuple[str, int]], dict]:
    """Return left/right (chrom, is_plus) flags and both-TE opposite counts."""
    left_flags: list[tuple[str, int]] = []
    right_flags: list[tuple[str, int]] = []
    both_opp = 0
    both_same = 0
    both_n = 0
    for left, right in loops:
        c_l, s_l, e_l = left
        c_r, s_r, e_r = right
        st_l = max_overlap_strand(s_l, e_l, te_by.get(c_l, []))
        st_r = max_overlap_strand(s_r, e_r, te_by.get(c_r, []))
        if st_l is not None:
            left_flags.append((c_l, 1 if st_l == "+" else 0))
        if st_r is not None:
            right_flags.append((c_r, 1 if st_r == "+" else 0))
        if st_l is not None and st_r is not None:
            both_n += 1
            if st_l == st_r:
                both_same += 1
            else:
                both_opp += 1
    meta = {
        "n_both_te_loops": both_n,
        "n_both_same_strand": both_same,
        "n_both_opposite_strand": both_opp,
        "f_opposite": (both_opp / both_n) if both_n else None,
        "abs_f_opp_minus_half": abs(both_opp / both_n - 0.5) if both_n else None,
    }
    return left_flags, right_flags, meta


def summarize(left_flags, right_flags, meta, *, label: str) -> dict:
    n_l = len(left_flags)
    n_r = len(right_flags)
    if n_l == 0 or n_r == 0:
        return {
            "label": label,
            "status": "SKIP_EMPTY",
            "n_left": n_l,
            "n_right": n_r,
            "both_te": meta,
        }
    p_l = sum(f for _, f in left_flags) / n_l
    p_r = sum(f for _, f in right_flags) / n_r
    delta = p_l - p_r
    abs_d = abs(delta)
    ci_lo, ci_hi = chrom_block_bootstrap_delta(left_flags, right_flags)
    # Contingency: +left, −left, +right, −right → OR(+ | left) vs right
    a = sum(1 for _, f in left_flags if f == 1)
    b = n_l - a
    c = sum(1 for _, f in right_flags if f == 1)
    d = n_r - c
    or_, or_lo, or_hi, p_fisher = fisher_or_woolf(a, b, c, d)
    verdict = verdict_abs_delta(abs_d)
    return {
        "label": label,
        "n_left_te_hit": n_l,
        "n_right_te_hit": n_r,
        "n_plus_left": a,
        "n_plus_right": c,
        "p_plus_left": p_l,
        "p_plus_right": p_r,
        "delta_orient": delta,
        "abs_delta_orient": abs_d,
        "bootstrap_ci_95": [ci_lo, ci_hi],
        "fisher_or_plus_left_vs_right": {
            "or": or_,
            "ci95": [or_lo, or_hi],
            "p": p_fisher,
        },
        "mcid_support": MCID_SUPPORT,
        "mcid_kill": MCID_KILL,
        "verdict": verdict,
        "both_te_exploratory": meta,
        "seed": SEED,
    }


def run_analysis(hic_path: Path, rmsk_path: Path, *, alu_only: bool, label: str) -> dict:
    print(f"[{label}] loading bedpe loops…", flush=True)
    loops = load_bedpe_loops(hic_path)
    print(f"[{label}] loops={len(loops)}; loading rmsk…", flush=True)
    te_by = load_te_strand_intervals(rmsk_path, alu_only=alu_only)
    print(f"[{label}] rmsk chroms={len(te_by)}; annotating…", flush=True)
    left_flags, right_flags, meta = annotate_side(loops, te_by)
    result = summarize(left_flags, right_flags, meta, label=label)
    result["n_loops"] = len(loops)
    result["alu_only"] = alu_only
    return result


def write_md(result: dict, path: Path) -> None:
    lines = [
        f"# C-J1 {result['label']}",
        "",
        f"- n_loops: {result.get('n_loops')}",
        f"- n_left TE-hit: {result.get('n_left_te_hit')}",
        f"- n_right TE-hit: {result.get('n_right_te_hit')}",
        f"- p(+|left): {result.get('p_plus_left')}",
        f"- p(+|right): {result.get('p_plus_right')}",
        f"- Δ_orient: {result.get('delta_orient')}",
        f"- |Δ_orient|: {result.get('abs_delta_orient')}",
        f"- bootstrap 95% CI: {result.get('bootstrap_ci_95')}",
        f"- verdict: **{result.get('verdict')}**",
        f"- both-TE f_opp: {(result.get('both_te_exploratory') or {}).get('f_opposite')}",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    hic = DATA / "ENCFF693XIL.bedpe.gz"
    rmsk = DATA / "rmsk.txt.gz"
    if not hic.exists() or not rmsk.exists():
        print("MISSING inputs — run t1_download_inputs.py first", file=sys.stderr)
        return 2
    RESULTS.mkdir(parents=True, exist_ok=True)

    primary = run_analysis(hic, rmsk, alu_only=False, label="primary")
    primary["ts_utc"] = datetime.now(timezone.utc).isoformat()
    primary["candidate_id"] = "C-J1"
    (RESULTS / "primary_delta_orient.json").write_text(
        json.dumps(primary, indent=2) + "\n", encoding="utf-8"
    )
    write_md(primary, RESULTS / "primary_delta_orient.md")
    print(
        f"PRIMARY |Δ|={primary.get('abs_delta_orient')} verdict={primary.get('verdict')}",
        flush=True,
    )

    alu = run_analysis(hic, rmsk, alu_only=True, label="alu_only")
    alu["ts_utc"] = datetime.now(timezone.utc).isoformat()
    alu["candidate_id"] = "C-J1"
    n_ok = (
        (alu.get("n_left_te_hit") or 0) >= 200
        and (alu.get("n_right_te_hit") or 0) >= 200
    )
    if not n_ok and alu.get("verdict") not in {None, "SKIP_EMPTY"}:
        alu["verdict_note"] = "n arms may be small; see claim SKIP rule"
    if (alu.get("n_left_te_hit") or 0) < 200 or (alu.get("n_right_te_hit") or 0) < 200:
        alu["verdict"] = "SKIP_N"
    (RESULTS / "sensitivity_alu_only.json").write_text(
        json.dumps(alu, indent=2) + "\n", encoding="utf-8"
    )
    write_md(alu, RESULTS / "sensitivity_alu_only.md")
    print(
        f"ALU |Δ|={alu.get('abs_delta_orient')} verdict={alu.get('verdict')}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
