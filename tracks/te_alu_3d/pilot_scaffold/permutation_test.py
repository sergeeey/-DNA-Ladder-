"""Permutation test — gate 6 (redesign v2).

Primary: block permutation within matched sets.
Software control only: global label shuffle.
KC1: report Δ_MAD; biological gate suspended until calibration;
      interim direction gate + permutation gate.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any

from qc_filters import load_config

ROOT = Path(__file__).resolve().parent


def wilcoxon_greater(x: list[float], y: list[float]) -> tuple[float, float]:
    """Mann-Whitney approximate one-sided p (x > y) + median delta."""
    if len(x) < 2 or len(y) < 2:
        return float("nan"), float("nan")
    pooled = [(v, 1) for v in x] + [(v, 0) for v in y]
    pooled.sort(key=lambda t: t[0])
    ranks: list[tuple[float, int]] = []
    i = 0
    while i < len(pooled):
        j = i
        while j + 1 < len(pooled) and pooled[j + 1][0] == pooled[i][0]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks.append((avg_rank, pooled[k][1]))
        i = j + 1
    r1 = sum(r for r, g in ranks if g == 1)
    n1, n2 = len(x), len(y)
    u1 = r1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    if sigma == 0:
        return float("nan"), float("nan")
    z = (u1 - mu) / sigma
    p = 0.5 * math.erfc(z / math.sqrt(2))
    effect = statistics.median(x) - statistics.median(y)
    return p, effect


def mad(xs: list[float]) -> float:
    if not xs:
        return float("nan")
    med = statistics.median(xs)
    return statistics.median([abs(x - med) for x in xs])


def delta_mad(te: list[float], ctrl: list[float]) -> float:
    if not te or not ctrl:
        return float("nan")
    scale = 1.4826 * mad(ctrl)
    if scale == 0 or math.isnan(scale):
        return float("nan")
    return (statistics.median(te) - statistics.median(ctrl)) / scale


def _stat_from_sets(sets: list[tuple[float, list[float]]]) -> tuple[float, float, list[float], list[float]]:
    """Return (median_delta, delta_MAD, te_list, ctrl_list)."""
    te = [s[0] for s in sets]
    ctrl = [c for _, cs in sets for c in cs]
    if not te or not ctrl:
        return float("nan"), float("nan"), te, ctrl
    return statistics.median(te) - statistics.median(ctrl), delta_mad(te, ctrl), te, ctrl


def block_permutation_null(
    matched_sets: list[tuple[float, list[float]]],
    n_perm: int,
    rng: random.Random,
) -> dict[str, Any]:
    """Shuffle labels within each matched set; compare observed median Δ.

    Each set = (te_score, [control_scores...]).
    """
    if not matched_sets:
        return {"error": "no_matched_sets", "mode": "block_matched"}

    usable = [(t, cs) for t, cs in matched_sets if cs]
    if len(usable) < 2:
        return {"error": "insufficient_matched_sets", "mode": "block_matched", "n_sets": len(usable)}

    obs_delta, obs_dmad, te, ctrl = _stat_from_sets(usable)
    obs_p, _ = wilcoxon_greater(te, ctrl)

    # One-sided: TE more disruptive ⇒ larger positive delta
    count = 0
    for _ in range(n_perm):
        sim_sets: list[tuple[float, list[float]]] = []
        for t, cs in usable:
            pool = [t] + list(cs)
            rng.shuffle(pool)
            sim_sets.append((pool[0], pool[1:]))
        sim_delta, _, _, _ = _stat_from_sets(sim_sets)
        if not math.isnan(sim_delta) and sim_delta >= obs_delta:
            count += 1

    perm_p = (count + 1) / (n_perm + 1)
    return {
        "mode": "block_matched",
        "observed_p": obs_p,
        "observed_effect_median_delta": obs_delta,
        "observed_delta_MAD": obs_dmad,
        "perm_p": perm_p,
        "n_perm": n_perm,
        "n_sets": len(usable),
        "n_te": len(te),
        "n_control": len(ctrl),
    }


def permutation_null(
    te_scores: list[float],
    control_scores: list[float],
    n_perm: int,
    rng: random.Random,
) -> dict[str, Any]:
    """Global shuffle — software negative control only (not primary)."""
    observed, obs_effect = wilcoxon_greater(te_scores, control_scores)
    dmad = delta_mad(te_scores, control_scores)
    combined = te_scores + control_scores
    n_te = len(te_scores)
    if n_te == 0 or len(control_scores) == 0:
        return {
            "mode": "global_shuffle",
            "error": "insufficient_data",
            "observed_p": observed,
            "observed_effect_median_delta": obs_effect,
            "observed_delta_MAD": dmad,
        }

    count = 0
    for _ in range(n_perm):
        rng.shuffle(combined)
        sim_te = combined[:n_te]
        sim_ctrl = combined[n_te:]
        _, sim_effect = wilcoxon_greater(sim_te, sim_ctrl)
        if not math.isnan(sim_effect) and sim_effect >= obs_effect:
            count += 1
    perm_p = (count + 1) / (n_perm + 1)
    return {
        "mode": "global_shuffle",
        "role": "software_negative_control_only",
        "observed_p": observed,
        "observed_effect_median_delta": obs_effect,
        "observed_delta_MAD": dmad,
        "perm_p": perm_p,
        "n_perm": n_perm,
        "n_te": n_te,
        "n_control": len(control_scores),
    }


def evaluate_kill_criteria(
    perm_result: dict[str, Any],
    cfg: dict[str, Any],
    qc_audit: dict[str, Any] | None = None,
    *,
    estimand: str = "T",
    kc0: dict[str, Any] | None = None,
    score_freeze: dict[str, Any] | None = None,
    used_fallback: bool = False,
) -> dict[str, Any]:
    """Kill criteria v1.2 — estimand-aware."""
    kc = cfg.get("kill_criteria", {})
    kc1_cfg = kc.get("kc1", {})
    status: dict[str, Any] = {"estimand": estimand}

    # KC0
    kc0 = kc0 or {}
    status["KC0"] = {
        "triggered": bool(kc0.get("confirmatory_blocked")),
        "reason": kc0.get("reason", "not_evaluated"),
        "action": "exploratory_only" if kc0.get("confirmatory_blocked") else "continue",
        "flags": kc0.get("flags", []),
    }

    effect = perm_result.get("observed_effect_median_delta", float("nan"))
    dmad = perm_result.get("observed_delta_MAD", float("nan"))
    perm_p = perm_result.get("perm_p", 1.0)
    direction_fail = (not math.isnan(effect)) and effect <= 0

    bio_gate = kc1_cfg.get("biological_gate", "suspended_until_calibration")
    status["KC1"] = {
        "triggered": direction_fail,
        "reason": (
            f"direction_fail median_delta={effect:.4f}; delta_MAD={dmad}; "
            f"perm_p={perm_p:.4g}; biological_gate={bio_gate}"
        ),
        "action": "STOP primary claim" if direction_fail else "report_effect_size_only",
        "median_delta": effect,
        "delta_MAD": dmad,
        "biological_gate": bio_gate,
    }

    # KC4
    status["KC4"] = {
        "triggered": False,
        "reason": "requires real mappability audit",
        "action": "check qc_dropout",
    }
    if qc_audit:
        inp = max(qc_audit.get("input", 1), 1)
        poor_frac = (
            qc_audit.get("gate_2_mappability", 0)
            + qc_audit.get("gate_3_segdup", 0)
            + qc_audit.get("gate_1_blacklist", 0)
        ) / inp
        max_frac = kc.get("kc4", {}).get("poor_mappability_fraction_max", 0.5)
        status["KC4"] = {
            "triggered": poor_frac > max_frac,
            "reason": f"qc_dropout_fraction={poor_frac:.2f} max={max_frac}",
            "action": "FIX QC or STOP" if poor_frac > max_frac else "continue",
        }

    alpha = cfg.get("qc_gates", {}).get("gate_6_permutation", {}).get("alpha", 0.05)
    null_ok = (not math.isnan(perm_p)) and perm_p < alpha
    freeze = score_freeze or {}
    freeze_ok = freeze.get("status") in {"FROZEN"}
    # EXPLORATORY_FROZEN allows reproducible exploratory claims machinery but not confirmatory
    exploratory_freeze_ok = freeze.get("status") in {"FROZEN", "EXPLORATORY_FROZEN"}
    confirmatory_ok = (
        null_ok
        and not direction_fail
        and not status["KC0"]["triggered"]
        and freeze_ok
        and not used_fallback
    )

    status["permutation_gate"] = {
        "passed": null_ok and not direction_fail,
        "perm_p": perm_p,
        "mode": perm_result.get("mode"),
        "message": (
            "enrichment_summary FORBIDDEN"
            if not (null_ok and not direction_fail)
            else "exploratory enrichment allowed (not biology)"
        ),
    }
    status["confirmatory_gate"] = {
        "passed": confirmatory_ok,
        "reason": (
            "ok"
            if confirmatory_ok
            else "blocked: "
            + ", ".join(
                x
                for x, bad in [
                    ("perm/direction", not (null_ok and not direction_fail)),
                    ("KC0", status["KC0"]["triggered"]),
                    ("score_not_confirmatory_frozen", not freeze_ok),
                    ("fallback_scorer", used_fallback),
                ]
                if bad
            )
        ),
    }
    status["exploratory_freeze"] = {
        "status": freeze.get("status"),
        "ok_for_exploratory_machinery": exploratory_freeze_ok,
    }
    return status


def load_score_freeze(path: Path | None = None) -> dict[str, Any]:
    import yaml

    p = path or ROOT / "score_freeze.yaml"
    if not p.exists():
        return {"status": "UNFROZEN", "reason": "missing_score_freeze.yaml"}
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    card = data.get("score_freeze", data)
    return card


def evaluate_kc0(cfg: dict[str, Any]) -> dict[str, Any]:
    """Cell-type / locus congruence (redesign v2)."""
    ctx = cfg.get("three_d_context", {})
    cell = ctx.get("preferred_cell_line", "")
    rules = (ctx.get("kc0") or {}).get("rules") or []
    locus_priors = (cfg.get("scoring") or {}).get("archcode", {}).get("locus_priors") or []
    flags: list[str] = []
    blocked = False
    reasons: list[str] = []

    cell_norm = cell.replace("_", "-").upper()
    for rule in rules:
        locus = rule.get("locus")
        forbidden = {x.replace("_", "-").upper() for x in (rule.get("forbidden_as_confirmatory") or [])}
        allowed = {x.replace("_", "-").upper() for x in (rule.get("allowed_cell_types") or [])}
        if locus not in locus_priors:
            continue
        if cell_norm in forbidden:
            blocked = True
            flags.append("cell_type_mismatch")
            reasons.append(f"{locus}+{cell}=exploratory_only")
        elif allowed and cell_norm not in allowed and cell.upper() not in {a.replace("-", "") for a in allowed}:
            # allow HUDEP-2 / HUDEP2 variants
            aliases = {a.replace("-", "") for a in allowed}
            if cell_norm.replace("-", "") not in aliases:
                blocked = True
                flags.append("cell_type_mismatch")
                reasons.append(f"{locus}+{cell} not in allowed {sorted(allowed)}")
        elif cell_norm in allowed or cell_norm.replace("-", "") in {a.replace("-", "") for a in allowed}:
            reasons.append(f"{locus}+{cell}=kc0_pass")

    return {
        "confirmatory_blocked": blocked,
        "reason": "; ".join(dict.fromkeys(reasons)) if reasons else "kc0_pass_or_no_rule",
        "flags": list(dict.fromkeys(flags)),
        "cell_line": cell,
        "locus_priors": locus_priors,
    }


def dry_run_matched_sets(cfg: dict[str, Any]) -> tuple[list[tuple[float, list[float]]], dict[str, Any]]:
    rng = random.Random(cfg["pilot"]["random_seed"])
    sets = []
    for _ in range(8):
        te = rng.uniform(0.12, 0.35)
        ctrls = [rng.uniform(0.10, 0.32) for _ in range(5)]
        sets.append((te, ctrls))
    audit = {
        "input": 50,
        "gate_1_blacklist": 2,
        "gate_2_mappability": 3,
        "gate_3_segdup": 1,
        "gate_4_discordance": 0,
        "passed": 12,
    }
    return sets, audit


def main() -> int:
    dry = "--dry-run" in sys.argv
    cfg = load_config()
    out_dir = ROOT / cfg["outputs"]["base_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "exploratory").mkdir(exist_ok=True)
    rng = random.Random(cfg["pilot"]["random_seed"])
    n_perm = min(cfg["qc_gates"]["gate_6_permutation"]["n_perm"], 1000)

    if not dry:
        print("Use --dry-run or run_pilot.py", file=sys.stderr)
        return 1

    sets, audit = dry_run_matched_sets(cfg)
    perm = block_permutation_null(sets, n_perm=n_perm, rng=rng)
    te = [s[0] for s in sets]
    ctrl = [c for _, cs in sets for c in cs]
    soft = permutation_null(te, ctrl, n_perm=min(n_perm, 200), rng=rng)
    kc0 = evaluate_kc0(cfg)
    freeze = load_score_freeze()
    kill = evaluate_kill_criteria(
        perm, cfg, audit, estimand="T", kc0=kc0, score_freeze=freeze, used_fallback=True
    )

    payload = {"primary_block": perm, "software_global": soft, "kill_criteria": kill}
    (out_dir / "permutation_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "kill_criteria_status.json").write_text(json.dumps(kill, indent=2), encoding="utf-8")
    (out_dir / "exploratory" / "enrichment_summary.csv").write_text(
        "metric,value\nstatus,BLOCKED_BY_PERMUTATION_GATE\n"
        if not kill["permutation_gate"]["passed"]
        else "metric,value\nstatus,exploratory_only\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
