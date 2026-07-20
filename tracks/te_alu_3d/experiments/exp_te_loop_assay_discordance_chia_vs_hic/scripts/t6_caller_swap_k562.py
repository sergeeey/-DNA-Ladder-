#!/usr/bin/env python3
"""T6 caller-swap sensitivity: K562 Pol II ChIA-PET vs alternate Hi-C loop callers.

Primary Hi-C remains ENCFF693XIL (HiCCUPS / juicertools merged_loops_30).
Alternate callers on the same or paired K562 Hi-C experiments:

  - ENCFF657QKE — DELTA v1.9 predicted_loops_merged (ENCSR545YBD; same library)
  - ENCFF256ZMD — intact Hi-C localizer localized_loops_30 (ENCSR479XDG; preferred)

Mustache: no released K562 GRCh38 bedpe loop file under Mustache software on ENCODE
portal at probe time → documented as unavailable (DELTA used as caller-swap).

Same AluSz estimand as T3 (1 kb midpoint windows). Does NOT change primary TE.
Does NOT touch holdout / C1 / wet GO.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Reuse T3 primitives
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t3_primary_alusz_or import (  # noqa: E402
    DATA,
    PRIMARY_TE,
    RESULTS,
    annotate_overlaps,
    build_units,
    contingency_or,
    desk_verdict,
    load_bedpe_anchors,
    load_rmsk_by_name,
    midpoint_windows,
)

EXP = Path(__file__).resolve().parent.parent

# Primary reference (already computed in T3; recomputed here for side-by-side)
PRIMARY_HIC = {
    "accession": "ENCFF693XIL",
    "experiment": "ENCSR545YBD",
    "caller": "HiCCUPS (juicertools merged_loops_30)",
    "role": "PRIMARY_FROZEN",
    "filename": "ENCFF693XIL.bedpe.gz",
    "portal_md5": "ae663464bdbe60998e422254ea0dac2c",
}

ALTERNATES = [
    {
        "accession": "ENCFF657QKE",
        "experiment": "ENCSR545YBD",
        "caller": "DELTA v1.9 predicted_loops_merged",
        "role": "CALLER_SWAP_PRIMARY",
        "filename": "ENCFF657QKE.bedpe.gz",
        "portal_md5": "0a3751e380c7b18e8565addaa23595ff",
        "note": (
            "Same in situ Hi-C experiment as primary; different loop caller "
            "(DELTA vs HiCCUPS). Preferred caller-swap for algorithm sensitivity."
        ),
    },
    {
        "accession": "ENCFF256ZMD",
        "experiment": "ENCSR479XDG",
        "caller": "intact Hi-C localizer localized_loops_30 (juicertools)",
        "role": "CALLER_SWAP_SECONDARY_ASSAY",
        "filename": "ENCFF256ZMD.bedpe.gz",
        "portal_md5": "47a1aa77c97c340234a1da38a21b8c62",
        "note": (
            "Different Hi-C assay (intact) + localizer call path; sensitivity only. "
            "Not a pure Mustache/HiCCUPS within-library swap."
        ),
    },
]

MUSTACHE_NOTE = (
    "ENCODE portal search (2026-07-20): no released K562 GRCh38 bedpe loops tagged "
    "to Mustache software. Caller-swap uses DELTA (same experiment) instead of Mustache."
)


def run_one(pol2_path: Path, hic_path: Path, rmsk_by: dict, meta: dict) -> dict:
    raw_pol2 = load_bedpe_anchors(pol2_path)
    raw_hic = load_bedpe_anchors(hic_path)
    pol2_units = build_units(raw_pol2)
    hic_units = build_units(raw_hic)
    pol2 = midpoint_windows(pol2_units)
    hic = midpoint_windows(hic_units)
    pol2_hits = annotate_overlaps(pol2, rmsk_by, PRIMARY_TE)
    hic_hits = annotate_overlaps(hic, rmsk_by, PRIMARY_TE)
    primary = contingency_or(pol2_hits, hic_hits)
    verdict = desk_verdict(
        primary["fisher_or"], primary["woolf_ci95_lo"], primary["woolf_ci95_hi"]
    )
    return {
        **meta,
        "hic_bedpe": str(hic_path),
        "anchor_counts": {
            "pol2_raw_unique": len(raw_pol2),
            "hic_raw_unique": len(raw_hic),
            "pol2_scoring_windows_1kb": len(pol2),
            "hic_scoring_windows_1kb": len(hic),
        },
        "alusz": {
            **primary,
            "desk_verdict": verdict,
        },
    }


def write_outputs(payload: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS / "caller_swap_k562.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    primary = payload["primary_hiccups"]
    rows = [primary, *payload["alternates"]]
    lines = [
        "# Caller-swap sensitivity — K562 AluSz OR (T6)",
        "",
        f"**Computed:** `{payload['computed_at_utc']}`  ",
        f"**Pol II fixed:** `{payload['pol2_accession']}`  ",
        f"**Primary TE:** `{PRIMARY_TE}` (frozen)  ",
        f"**Mustache:** {payload['mustache_status']}",
        "",
        "## Estimand",
        "",
        "Same as T3: Fisher OR for AluSz in fixed 1 kb midpoint windows of merged",
        "anchors — Pol II ChIA-PET vs each Hi-C loop call set (K562 / GRCh38).",
        "Descriptive only; not causal; not a new primary estimand.",
        "",
        "## Results",
        "",
        "| Role | Hi-C file | Caller | n Hi-C windows | AluSz Fisher OR | Woolf 95% CI | Desk verdict |",
        "|------|-----------|--------|----------------|-----------------|--------------|--------------|",
    ]
    for r in rows:
        a = r["alusz"]
        lines.append(
            f"| {r['role']} | `{r['accession']}` | {r['caller']} | "
            f"{r['anchor_counts']['hic_scoring_windows_1kb']} | "
            f"**{a['fisher_or']:.4f}** | "
            f"{a['woolf_ci95_lo']:.4f}–{a['woolf_ci95_hi']:.4f} | "
            f"`{a['desk_verdict']['verdict']}` |"
        )

    delta = next(r for r in payload["alternates"] if r["accession"] == "ENCFF657QKE")
    d_or = delta["alusz"]["fisher_or"]
    p_or = primary["alusz"]["fisher_or"]
    lines += [
        "",
        "## Interpretation",
        "",
        f"- Primary HiCCUPS OR ≈ **{p_or:.3f}** (`FAIL_DESK_PRIMARY`).",
        f"- DELTA caller-swap OR ≈ **{d_or:.3f}** "
        f"(`{delta['alusz']['desk_verdict']['verdict']}`).",
        payload["synthesis"],
        "",
        "## Notes",
        "",
        f"- {MUSTACHE_NOTE}",
        "- Intact localizer (`ENCFF256ZMD`) is assay+caller sensitivity, not a pure",
        "  within-library algorithm swap.",
        "- Does **not** rescue K562 enrichment claim (MCID ≥ 1.3) if OR remains < 1.1,",
        "  nor convert mid-zone replication cells into SUPPORT.",
        "",
        "## What this does NOT mean",
        "",
        "1. NOT proof that HiCCUPS vs DELTA is biologically superior.",
        "2. NOT a Mustache comparison (Mustache file absent on portal).",
        "3. NOT causal TE → loop; NOT wet/holdout/C1 authorization.",
        "4. NOT a license to switch primary TE or rebrand FAIL as SUPPORT.",
        "",
    ]
    (RESULTS / "caller_swap_k562.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pol2", type=Path, default=DATA / "ENCFF511QFN.bedpe.gz")
    ap.add_argument("--rmsk", type=Path, default=DATA / "rmsk.txt.gz")
    ap.add_argument("--data-dir", type=Path, default=DATA)
    args = ap.parse_args()

    if not args.pol2.exists() or not args.rmsk.exists():
        print("Missing Pol II bedpe or rmsk", file=sys.stderr)
        return 1

    rmsk_by = load_rmsk_by_name(args.rmsk, {PRIMARY_TE})
    primary_path = args.data_dir / PRIMARY_HIC["filename"]
    if not primary_path.exists():
        print(f"Missing primary Hi-C: {primary_path}", file=sys.stderr)
        return 1

    primary_res = run_one(args.pol2, primary_path, rmsk_by, PRIMARY_HIC)
    alt_res = []
    for meta in ALTERNATES:
        path = args.data_dir / meta["filename"]
        if not path.exists():
            alt_res.append({**meta, "status": "MISSING_FILE", "path": str(path)})
            continue
        alt_res.append(run_one(args.pol2, path, rmsk_by, meta))

    # Synthesis for closure language
    delta = next((r for r in alt_res if r.get("accession") == "ENCFF657QKE" and "alusz" in r), None)
    if delta is None:
        synthesis = (
            "BLOCKED_CALLER_SWAP for DELTA file — cannot update FAIL sensitivity."
        )
        status = "BLOCKED_CALLER_SWAP"
    else:
        d_or = delta["alusz"]["fisher_or"]
        p_or = primary_res["alusz"]["fisher_or"]
        if d_or < 1.1 and p_or < 1.1:
            synthesis = (
                f"Caller-swap **does not reverse** K562 FAIL: DELTA OR {d_or:.3f} "
                f"and HiCCUPS OR {p_or:.3f} both remain < 1.1 (depletion / null "
                "enrichment). Does **not** convert three-cell pattern to REJECT "
                "(replication arms still mid-zone) nor to SUPPORT."
            )
            status = "CALLER_SWAP_DONE_FAIL_ROBUST"
        elif d_or >= 1.3:
            synthesis = (
                f"DELTA OR {d_or:.3f} ≥ MCID while HiCCUPS FAIL — caller-dependent; "
                "do not claim primary SUPPORT; flag sensitivity conflict."
            )
            status = "CALLER_SWAP_CONFLICT"
        else:
            synthesis = (
                f"DELTA OR {d_or:.3f} vs HiCCUPS {p_or:.3f}; see desk verdicts. "
                "Does not alone justify claim-level REJECT or SUPPORT."
            )
            status = "CALLER_SWAP_DONE"

    payload = {
        "script": "t6_caller_swap_k562",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembly": "GRCh38",
        "primary_te": PRIMARY_TE,
        "pol2_accession": "ENCFF511QFN",
        "mustache_status": "UNAVAILABLE_ON_ENCODE_K562_GRCh38",
        "mustache_note": MUSTACHE_NOTE,
        "status": status,
        "synthesis": synthesis,
        "primary_hiccups": primary_res,
        "alternates": alt_res,
        "explicit_non_claims": [
            "No Mustache file available — DELTA used as algorithm swap",
            "No causal TE → loop",
            "Holdout / C1 / wet untouched",
            "Primary TE remains AluSz",
        ],
    }
    write_outputs(payload)
    print(json.dumps({"status": status, "synthesis": synthesis}, indent=2))
    print(f"Wrote {RESULTS / 'caller_swap_k562.json'} and .md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
