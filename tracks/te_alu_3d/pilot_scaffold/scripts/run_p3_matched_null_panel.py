#!/usr/bin/env python3
"""P3 matched-null kill-test for frozen Stage-1 panel.

Pre-registered thresholds live in:
  09_outputs/prospective/P3_matched_null_CLAIM_v1.md

Uses SCORED Stage-1 pool only (no holdout, no new enrichment discovery).
"""

from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "09_outputs" / "prospective"
STAGE1 = OUT / "stage1_desk_screen_v1.json"
SEED = 20260715
N_PERM = 5000

# --- locked thresholds (must match CLAIM) ---
PCT_RETAIN = 90.0
PCT_KILL = 75.0
EFFECT_CHIP = 0.05
EFFECT_CONTACT = 0.05  # same number; contact values are smaller — still pre-registered
NEG_PCT_PASS = 50.0
NEG_PCT_FAIL = 90.0
MIN_CTRL = 5
BLOCK_MB = 5


def _parse_vid(vid: str) -> tuple[str, int, str, str] | None:
    if not vid or vid.startswith("P1_"):
        return None
    parts = vid.split(":")
    if len(parts) != 4:
        return None
    return parts[0], int(parts[1]), parts[2], parts[3]


def te_clade(family: str | None) -> str:
    if not family:
        return "other"
    f = family.upper()
    if f.startswith("ALUY"):
        return "AluY"
    if f.startswith("ALUS"):
        return "AluS"
    if f.startswith("ALUJ"):
        return "AluJ"
    if f.startswith("FLAM"):
        return "FLAM"
    if f.startswith("FRAM"):
        return "FRAM"
    return "other"


def ctcf_bin(d: Any) -> str:
    try:
        return "zero" if int(d) == 0 else "near"
    except (TypeError, ValueError):
        return "unk"


def chrom_block(pos: int, mb: int = BLOCK_MB) -> int:
    return pos // (mb * 1_000_000)


def fscore(x: Any) -> float | None:
    if x is None or x == "" or x == "nan":
        return None
    try:
        return abs(float(x))
    except (TypeError, ValueError):
        return None


def empirical_percentile(focal: float, others: list[float]) -> float:
    """Percentile of focal among focal+others (higher=more extreme high)."""
    xs = others + [focal]
    n = len(xs)
    if n <= 1:
        return float("nan")
    # midrank for ties
    less = sum(1 for v in xs if v < focal)
    equal = sum(1 for v in xs if v == focal)
    return 100.0 * (less + 0.5 * equal) / n


def block_perm_p(focal: float, ctrls: list[float], n_perm: int, rng: random.Random) -> float:
    """One-sided: P(null_focal >= observed) under label swap within set."""
    if not ctrls:
        return float("nan")
    pool = [focal] + ctrls
    obs = focal
    ge = 0
    for _ in range(n_perm):
        # pick a random member as "focal"
        fake = rng.choice(pool)
        if fake >= obs:
            ge += 1
    return (ge + 1) / (n_perm + 1)


def match_controls(
    cand: dict[str, Any],
    universe: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]], dict[str, int]]:
    """Return (level, controls, counts_by_level)."""
    vid = cand["variant_id"]
    pos = int(cand["pos"])
    fam = cand.get("te_family")
    clade = te_clade(fam)
    cbin = ctcf_bin(cand.get("dist_ctcf"))
    block = chrom_block(pos)
    mut = f"{cand['ref']}>{cand['alt']}"

    def ok_base(r: dict[str, Any]) -> bool:
        if r["variant_id"] == vid:
            return False
        if int(r["pos"]) == pos:
            return False  # same-locus companion alleles out
        return True

    base = [r for r in universe if ok_base(r)]

    def L1(r: dict[str, Any]) -> bool:
        return (
            r.get("te_family") == fam
            and ctcf_bin(r.get("dist_ctcf")) == cbin
            and chrom_block(int(r["pos"])) == block
            and f"{r['ref']}>{r['alt']}" == mut
        )

    def L2(r: dict[str, Any]) -> bool:
        return (
            te_clade(r.get("te_family")) == clade
            and ctcf_bin(r.get("dist_ctcf")) == cbin
            and chrom_block(int(r["pos"])) == block
        )

    def L3(r: dict[str, Any]) -> bool:
        return te_clade(r.get("te_family")) == clade and ctcf_bin(r.get("dist_ctcf")) == cbin

    def L4(r: dict[str, Any]) -> bool:
        return ctcf_bin(r.get("dist_ctcf")) == cbin

    levels = [
        ("L1", L1),
        ("L2", L2),
        ("L3", L3),
        ("L4", L4),
    ]
    counts = {name: sum(1 for r in base if fn(r)) for name, fn in levels}
    for name, fn in levels:
        ctrls = [r for r in base if fn(r)]
        if name in ("L1", "L2", "L3") and len(ctrls) >= MIN_CTRL:
            return name, ctrls, counts
        if name == "L4":
            return name, ctrls, counts
    return "L4", [], counts


def primary_endpoint(role: str) -> str:
    if role == "architecture_m1":
        return "ag_contact_mae"
    return "ag_chip_tf_mae"


def decide(role: str, pct: float, effect: float, level: str, n_ctrl: int) -> str:
    insufficient = n_ctrl < MIN_CTRL or level == "L4"
    if role == "matched_negative":
        if math.isnan(pct):
            return "INCONCLUSIVE"
        if pct >= NEG_PCT_FAIL and effect > EFFECT_CHIP:
            return "NEGATIVE_FAIL"
        if pct <= NEG_PCT_PASS or effect <= 0:
            return "PASS_AS_NEGATIVE"
        return "INCONCLUSIVE"

    if math.isnan(pct) or insufficient:
        # still allow clear kill if effect non-positive even with thin matches
        if not math.isnan(pct) and (pct < PCT_KILL or effect <= 0):
            return "KILL_HP_DEMOTION"
        return "INCONCLUSIVE"

    thr_eff = EFFECT_CONTACT if role == "architecture_m1" else EFFECT_CHIP
    if pct >= PCT_RETAIN and effect > thr_eff and level in ("L1", "L2"):
        return "RETAIN_HP"
    if pct < PCT_KILL or effect <= 0:
        return "KILL_HP_DEMOTION"
    return "INCONCLUSIVE"


def main() -> None:
    doc = json.loads(STAGE1.read_text(encoding="utf-8"))
    pool = doc["pool"]
    pool_by_vid = {r["variant_id"]: r for r in pool}

    # enrich frozen rows from pool / parse vid
    frozen_raw = doc["frozen_panel"]
    results: list[dict[str, Any]] = []
    rng = random.Random(SEED)

    activity_ids = []
    for fr in frozen_raw:
        role = fr.get("frozen_role") or fr.get("role")
        vid = fr["variant_id"]
        if role == "known_positive" or str(vid).startswith("P1_"):
            results.append(
                {
                    "variant_id": vid,
                    "frozen_role": role,
                    "verdict": "SKIP_KNOWN_ASSAY_CONTROL",
                    "note": "no AG SNV score in Stage-1 pool",
                }
            )
            continue

        src = pool_by_vid.get(vid, {})
        parsed = _parse_vid(vid)
        if not parsed:
            results.append(
                {
                    "variant_id": vid,
                    "frozen_role": role,
                    "verdict": "INCONCLUSIVE",
                    "note": "unparseable variant_id",
                }
            )
            continue
        chrom, pos, ref, alt = parsed
        cand = {
            "variant_id": vid,
            "frozen_role": role,
            "chrom": chrom,
            "pos": pos,
            "ref": src.get("ref") or ref,
            "alt": src.get("alt") or alt,
            "te_family": src.get("te_family") or fr.get("te_family"),
            "dist_ctcf": src.get("dist_ctcf") if src.get("dist_ctcf") is not None else fr.get("dist_ctcf"),
            "ag_chip_tf_mae": src.get("ag_chip_tf_mae") or fr.get("ag_chip_tf_mae"),
            "ag_contact_mae": src.get("ag_contact_mae") or fr.get("ag_contact_mae"),
            "pwm_delta_logodds": src.get("pwm_delta_logodds"),
            "pe_desk": src.get("pe_desk"),
            "ag_status": src.get("ag_status"),
        }

        ep = primary_endpoint(role)
        s_focal = fscore(cand.get(ep))
        if s_focal is None:
            results.append(
                {
                    "variant_id": vid,
                    "frozen_role": role,
                    "endpoint": ep,
                    "verdict": "INCONCLUSIVE",
                    "note": "missing primary score",
                }
            )
            continue

        level, ctrls, counts = match_controls(cand, pool)
        ctrl_scores = [fscore(c.get(ep)) for c in ctrls]
        ctrl_scores = [x for x in ctrl_scores if x is not None]
        n_ctrl = len(ctrl_scores)
        pct = empirical_percentile(s_focal, ctrl_scores) if n_ctrl else float("nan")
        med = statistics.median(ctrl_scores) if ctrl_scores else float("nan")
        effect = s_focal - med if ctrl_scores else float("nan")
        p_perm = block_perm_p(s_focal, ctrl_scores, N_PERM, rng) if ctrl_scores else float("nan")

        # leave-one-out percentile stability
        loo = []
        for i in range(n_ctrl):
            sub = ctrl_scores[:i] + ctrl_scores[i + 1 :]
            if not sub:
                continue
            loo.append(empirical_percentile(s_focal, sub))
        loo_range = (max(loo) - min(loo)) if len(loo) >= 2 else float("nan")

        # secondary
        sec_key = "ag_chip_tf_mae" if ep == "ag_contact_mae" else "ag_contact_mae"
        s_sec = fscore(cand.get(sec_key))
        ctrl_sec = [fscore(c.get(sec_key)) for c in ctrls]
        ctrl_sec = [x for x in ctrl_sec if x is not None]
        pct_sec = empirical_percentile(s_sec, ctrl_sec) if s_sec is not None and ctrl_sec else float("nan")

        pe_bal = defaultdict(int)
        for c in ctrls:
            pe_bal[str(c.get("pe_desk"))] += 1

        verdict = decide(role, pct, effect if not math.isnan(effect) else 0.0, level, n_ctrl)
        if role in ("TEMPLATE_DEV", "activity_m3"):
            activity_ids.append((vid, verdict))

        results.append(
            {
                "variant_id": vid,
                "frozen_role": role,
                "te_family": cand.get("te_family"),
                "te_clade": te_clade(cand.get("te_family")),
                "dist_ctcf": cand.get("dist_ctcf"),
                "mut": f"{cand['ref']}>{cand['alt']}",
                "endpoint": ep,
                "score": s_focal,
                "match_level": level,
                "n_ctrl": n_ctrl,
                "match_counts": counts,
                "median_ctrl": med,
                "effect": effect,
                "empirical_percentile": pct,
                "block_perm_p_one_sided": p_perm,
                "loo_percentile_range": loo_range,
                "secondary_endpoint": sec_key,
                "secondary_percentile": pct_sec,
                "pe_desk_balance": dict(pe_bal),
                "ctrl_variant_ids": [c["variant_id"] for c in ctrls],
                "verdict": verdict,
            }
        )

    # panel-level
    act_kill = sum(1 for _, v in activity_ids if v == "KILL_HP_DEMOTION")
    neg_fail = any(r.get("verdict") == "NEGATIVE_FAIL" for r in results)
    panel = {
        "PANEL_ACTIVITY_CLAIM_WEAKENED": act_kill >= 2,
        "n_activity_kill_demotion": act_kill,
        "PANEL_NEGATIVE_BROKEN": neg_fail,
    }

    out = {
        "status": "P3_MATCHED_NULL_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claim": "P3_matched_null_CLAIM_v1.md",
        "seed": SEED,
        "n_perm": N_PERM,
        "thresholds": {
            "PCT_RETAIN": PCT_RETAIN,
            "PCT_KILL": PCT_KILL,
            "EFFECT_CHIP": EFFECT_CHIP,
            "NEG_PCT_PASS": NEG_PCT_PASS,
            "NEG_PCT_FAIL": NEG_PCT_FAIL,
            "MIN_CTRL": MIN_CTRL,
        },
        "universe": "stage1_desk_screen_v1.json pool SCORED (n=28)",
        "panel_summary": panel,
        "results": results,
    }

    out_json = OUT / "P3_matched_null_panel_v1.json"
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    def _fmt(x: Any, kind: str) -> str:
        if x is None:
            return "—"
        if isinstance(x, float) and math.isnan(x):
            return "—"
        if kind == "f4":
            return f"{x:.4f}"
        if kind == "f1":
            return f"{x:.1f}"
        if kind == "f3":
            return f"{x:.3f}"
        if kind == "eff":
            return f"{x:+.4f}"
        return str(x)

    lines = [
        "# P3 — Matched-null panel ×13",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Status:** `{out['status']}`",
        "**Claim (pre-registered):** `P3_matched_null_CLAIM_v1.md`",
        f"**Machine:** `{out_json.name}`",
        "",
        "## Panel-level",
        "",
        f"- `PANEL_ACTIVITY_CLAIM_WEAKENED`: **{panel['PANEL_ACTIVITY_CLAIM_WEAKENED']}** "
        f"(activity KILL_HP_DEMOTION count = {panel['n_activity_kill_demotion']})",
        f"- `PANEL_NEGATIVE_BROKEN`: **{panel['PANEL_NEGATIVE_BROKEN']}**",
        "",
        "## Per-candidate",
        "",
        "| Variant | Role | Endp | Level | n_ctrl | Score | Eff | Pct | p_perm | Verdict |",
        "|---------|------|------|------:|-------:|------:|----:|----:|-------:|---------|",
    ]
    for r in results:
        if r.get("verdict") == "SKIP_KNOWN_ASSAY_CONTROL":
            lines.append(
                f"| `{r['variant_id']}` | {r.get('frozen_role')} | — | — | — | — | — | — | — | **SKIP** |"
            )
            continue
        ep = (r.get("endpoint") or "").replace("ag_", "").replace("_mae", "")
        lines.append(
            f"| `{r['variant_id']}` | {r.get('frozen_role')} | {ep} | {r.get('match_level')} | "
            f"{r.get('n_ctrl')} | {_fmt(r.get('score'), 'f4')} | {_fmt(r.get('effect'), 'eff')} | "
            f"{_fmt(r.get('empirical_percentile'), 'f1')} | {_fmt(r.get('block_perm_p_one_sided'), 'f3')} | "
            f"**{r.get('verdict')}** |"
        )

    lines += [
        "",
        "## Plain language",
        "",
        "Сравниваем каждый из 13 не с «всем миром», а с похожими Alu/SVA аллелями "
        "(семейство/клада, дистанция до CTCF, блок хроматина, тип замены). "
        "Если «хит» не выделяется на этом фоне — снимаем high-priority, не лабораторный GO.",
        "",
        "## What this does NOT mean",
        "",
        "- Not wet-lab proof or kill of biology",
        "- Not permission to reopen holdout or reshape Stage-3",
        "- Pool n=28 limits L1/L2; thin matches force INCONCLUSIVE by design",
        "",
    ]
    out_md = OUT / "P3_matched_null_panel_v1.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"wrote": str(out_json), "panel": panel, "n": len(results)}, indent=2))


if __name__ == "__main__":
    main()
