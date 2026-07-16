#!/usr/bin/env python3
"""P8 power simulation — reporter & Capture-C MCIDs.

Claim: 09_outputs/prospective/P8_POWER_CLAIM_v1.md
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective"
SEED = 20260716
N_SIM = 5000


def reporter_power(mu: float, sigma: float, n_tx: int, rng: np.random.Generator) -> dict:
    """MCID: >=2 txs with |x|>=0.5 and same sign as mean(x)."""
    x = rng.normal(mu, sigma, size=(N_SIM, n_tx))
    means = x.mean(axis=1)
    signs = np.sign(means)
    signs[signs == 0] = 1
    hits = (np.abs(x) >= 0.5) & (np.sign(x) == signs[:, None])
    # require at least 2 hits; if mu==0, "success" is false positive rate under MCID rule
    ok = hits.sum(axis=1) >= 2
    # also require mean direction matches true mu sign when mu!=0
    if abs(mu) > 1e-12:
        ok &= np.sign(means) == np.sign(mu)
    # secondary: normal-approx two-sided test vs 0
    se = x.std(axis=1, ddof=1) / math.sqrt(n_tx)
    t = np.divide(means, se, out=np.zeros_like(means), where=se > 0)
    p = np.fromiter(
        (math.erfc(abs(float(ti)) / math.sqrt(2.0)) for ti in t),
        dtype=float,
        count=t.size,
    )
    t_ok = p < 0.05
    return {
        "power_mcid": float(ok.mean()),
        "power_ttest_alpha05": float(t_ok.mean()),
    }


def capture_power(
    delta_true: float,
    sigma: float,
    eps_edit: float,
    n_batch: int,
    rng: np.random.Generator,
) -> dict:
    """Success if |mean Delta_hat| >= 0.25 (fraction of WT)."""
    # each batch: eps * delta_true + noise
    obs = eps_edit * delta_true + rng.normal(0.0, sigma, size=(N_SIM, n_batch))
    mean_abs = np.abs(obs.mean(axis=1))
    ok_contact = mean_abs >= 0.25
    # OE proxy: treat 2*|Delta| as OE-like scale (desk only)
    ok_oe = (2.0 * mean_abs) >= 0.5
    ok = ok_contact | ok_oe
    return {
        "power_mcid_contact_or_oe_proxy": float(ok.mean()),
        "power_contact_only": float(ok_contact.mean()),
    }


def label(power_mid_at_n6: float) -> str:
    if power_mid_at_n6 < 0.5:
        return "P8_UNDERPOWERED"
    if power_mid_at_n6 < 0.8:
        return "P8_MARGINAL"
    return "P8_ADEQUATE"


def main() -> int:
    rng = np.random.default_rng(SEED)

    # Reporter grid
    sigmas = {"low": 0.25, "mid": 0.40, "high": 0.60}
    mus = [0.0, 0.35, 0.50, 0.75, 1.0]
    ns = [2, 3, 4, 6, 8]
    reporter = []
    for mu in mus:
        for sname, sigma in sigmas.items():
            for n in ns:
                p = reporter_power(mu, sigma, n, rng)
                reporter.append(
                    {
                        "assay": "reporter",
                        "mu_log2": mu,
                        "sigma": sigma,
                        "sigma_band": sname,
                        "n_tx": n,
                        **p,
                    }
                )

    # Capture grid
    csig = {"low": 0.08, "mid": 0.15, "high": 0.25}
    deltas = [0.15, 0.25, 0.40, 0.60]
    epsilons = [0.3, 0.5, 0.7, 0.9]
    nbatches = [2, 3, 4, 6]
    capture = []
    for d in deltas:
        for sname, sigma in csig.items():
            for eps in epsilons:
                for n in nbatches:
                    p = capture_power(d, sigma, eps, n, rng)
                    capture.append(
                        {
                            "assay": "capture_c",
                            "delta_true_frac_wt": d,
                            "sigma": sigma,
                            "sigma_band": sname,
                            "edit_efficiency": eps,
                            "n_batch": n,
                            **p,
                        }
                    )

    # Focus slices for labels
    def get_rep(mu, sband, n):
        return next(
            r
            for r in reporter
            if r["mu_log2"] == mu and r["sigma_band"] == sband and r["n_tx"] == n
        )

    def get_cap(d, sband, eps, n):
        return next(
            c
            for c in capture
            if c["delta_true_frac_wt"] == d
            and c["sigma_band"] == sband
            and c["edit_efficiency"] == eps
            and c["n_batch"] == n
        )

    rep_mid_mcid = get_rep(0.50, "mid", 6)["power_mcid"]
    cap_mid = get_cap(0.25, "mid", 0.7, 6)["power_mcid_contact_or_oe_proxy"]

    # recommended n: smallest n with mid power >= 0.8 for MCID-true
    def rec_n_rep():
        for n in ns:
            if get_rep(0.50, "mid", n)["power_mcid"] >= 0.8:
                return n
        return None

    def rec_n_cap():
        for n in nbatches:
            if get_cap(0.25, "mid", 0.7, n)["power_mcid_contact_or_oe_proxy"] >= 0.8:
                return n
        return None

    summary = {
        "reporter_label": label(rep_mid_mcid),
        "reporter_power_mid_mu0.5_n6": rep_mid_mcid,
        "reporter_recommended_n_tx_mid": rec_n_rep(),
        "reporter_false_pos_mu0_mid_n6": get_rep(0.0, "mid", 6)["power_mcid"],
        "capture_label": label(cap_mid),
        "capture_power_mid_d0.25_eps0.7_n6": cap_mid,
        "capture_recommended_n_batch_mid_eps0.7": rec_n_cap(),
        "capture_power_mid_d0.25_eps0.5_n6": get_cap(0.25, "mid", 0.5, 6)[
            "power_mcid_contact_or_oe_proxy"
        ],
        "capture_power_mid_d0.25_eps0.3_n6": get_cap(0.25, "mid", 0.3, 6)[
            "power_mcid_contact_or_oe_proxy"
        ],
    }

    doc = {
        "status": "P8_POWER_COMPLETE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claim": "P8_POWER_CLAIM_v1.md",
        "seed": SEED,
        "n_sim": N_SIM,
        "summary": summary,
        "reporter_grid": reporter,
        "capture_grid": capture,
    }
    out_json = OUT / "P8_power_simulation_v1.json"
    out_json.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    # markdown tables — key slices only
    lines = [
        "# P8 — Power simulation v1",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Status:** `{doc['status']}`",
        f"**Claim:** `P8_POWER_CLAIM_v1.md`",
        f"**Seed / sims:** {SEED} / {N_SIM}",
        "",
        "## Labels",
        "",
        f"| Assay | Label | Mid-noise power @ n=6 (MCID-true) |",
        f"|-------|-------|----------------------------------:|",
        f"| Reporter (μ=0.5) | **{summary['reporter_label']}** | {summary['reporter_power_mid_mu0.5_n6']:.3f} |",
        f"| Capture-C (Δ=0.25, ε=0.7) | **{summary['capture_label']}** | {summary['capture_power_mid_d0.25_eps0.7_n6']:.3f} |",
        "",
        f"- Reporter recommended n_tx (mid, power≥0.8): **{summary['reporter_recommended_n_tx_mid']}**",
        f"- Capture recommended n_batch (mid, ε=0.7, power≥0.8): **{summary['capture_recommended_n_batch_mid_eps0.7']}**",
        f"- Reporter false-positive under MCID rule (μ=0, mid, n=6): **{summary['reporter_false_pos_mu0_mid_n6']:.3f}**",
        "",
        "## Reporter — power for μ=0.5 (MCID boundary)",
        "",
        "| n_tx | low σ=0.25 | mid σ=0.40 | high σ=0.60 |",
        "|-----:|-----------:|-----------:|------------:|",
    ]
    for n in ns:
        row = [str(n)]
        for sband in ("low", "mid", "high"):
            row.append(f"{get_rep(0.50, sband, n)['power_mcid']:.3f}")
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Capture-C — power for Δ=0.25 WT (MCID boundary), mid noise",
        "",
        "| n_batch | ε=0.3 | ε=0.5 | ε=0.7 | ε=0.9 |",
        "|--------:|------:|------:|------:|------:|",
    ]
    for n in nbatches:
        row = [str(n)]
        for eps in epsilons:
            row.append(f"{get_cap(0.25, 'mid', eps, n)['power_mcid_contact_or_oe_proxy']:.3f}")
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Plain language",
        "",
        "Считаем, хватит ли 2–6 реплик, чтобы поймать ваш MCID, "
        "если шум низкий / средний / высокий, и если edit не 100% чистый. "
        "Это не обещание лаборатории — проверка, не фантазия ли план.",
        "",
        "## What this does NOT mean",
        "",
        "- Not calibrated to real HUDEP-2 variance (priors are desk assumptions)",
        "- Not wet GO / not oligo order",
        "- Capture OE path is a desk proxy (2×\\|Δ\\|), not measured OE",
        "",
        f"Full grid: `{out_json.name}`",
        "",
    ]
    (OUT / "P8_power_simulation_v1.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
