#!/usr/bin/env python3
"""T5 replication cell type: AluSz OR on Pol II ChIA-PET vs Hi-C.

Same primary pipeline as T3 (K562):
  - Merged ≥1 kb anchors; AluSz overlap on fixed 1 kb midpoint windows
  - Fisher OR + Woolf 95% CI
  - Optional CTCF positive gate on this cell type's Hi-C (same OR≥2.0 spirit)

Frozen accessions:
  GM12878 — ACCESSION_FREEZE_replication_v1.md
    Pol II: ENCFF913VWM; Hi-C: ENCFF781ASD; CTCF: ENCFF796WRU
  HCT116 — ACCESSION_FREEZE_replication_HCT116_v1.md
    Pol II: ENCFF322FOT; Hi-C: ENCFF060QTI; CTCF: ENCFF463FGL

Does NOT change primary TE. Does NOT invent wet/holdout/C1 claims.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from t3_primary_alusz_or import (  # noqa: E402
    PRIMARY_TE,
    annotate_overlaps,
    build_units,
    chrom_block_bootstrap_ci,
    contingency_or,
    load_bedpe_anchors,
    load_rmsk_by_name,
    matched_null_permutations,
    midpoint_windows,
)

# CTCF gate helpers from t2
from t2_positive_control_ctcf_gate import (  # noqa: E402
    GATE_OR_THRESHOLD,
    build_interval_index,
    chrom_spans,
    fisher_exact_two_sided,
    load_bed_intervals,
    load_bedpe_anchors as load_hic_anchors_raw,
    overlaps_any,
    woolf_or_ci,
)

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"

CELL_CONFIGS: dict[str, dict[str, str]] = {
    "GM12878": {
        "pol2_acc": "ENCFF913VWM",
        "hic_acc": "ENCFF781ASD",
        "ctcf_acc": "ENCFF796WRU",
        "pol2_exp": "ENCSR905HWW",
        "hic_exp": "ENCSR410MDC",
        "ctcf_exp": "ENCSR000DZN",
        "freeze": "ACCESSION_FREEZE_replication_v1.md",
    },
    "HCT116": {
        "pol2_acc": "ENCFF322FOT",
        "hic_acc": "ENCFF060QTI",
        "ctcf_acc": "ENCFF463FGL",
        "pol2_exp": "ENCSR035PVZ",
        "hic_exp": "ENCSR123UVP",
        "ctcf_exp": "ENCSR240PRQ",
        "freeze": "ACCESSION_FREEZE_replication_HCT116_v1.md",
    },
}

# Back-compat module aliases (GM12878 defaults; tests / importers)
CELLTYPE = "GM12878"
POL2_ACC = CELL_CONFIGS[CELLTYPE]["pol2_acc"]
HIC_ACC = CELL_CONFIGS[CELLTYPE]["hic_acc"]
CTCF_ACC = CELL_CONFIGS[CELLTYPE]["ctcf_acc"]
POL2_EXP = CELL_CONFIGS[CELLTYPE]["pol2_exp"]
HIC_EXP = CELL_CONFIGS[CELLTYPE]["hic_exp"]
CTCF_EXP = CELL_CONFIGS[CELLTYPE]["ctcf_exp"]
MCID_FAIL = 1.1
MCID_SUPPORT = 1.3
REPL_FAIL = 1.15  # claim falsification: replication OR < 1.15 or opposite
N_PERM = 200
N_BOOT = 500
SEED = 42
CANON = {f"chr{i}" for i in range(1, 23)} | {"chrX"}


def run_ctcf_gate(
    hic_path: Path,
    ctcf_path: Path,
    *,
    celltype: str,
    hic_acc: str,
    ctcf_acc: str,
    n_shuffles: int = 50,
) -> dict:
    """Mirror t2 gate on replication Hi-C + cell-type CTCF peaks."""
    anchors = load_hic_anchors_raw(hic_path)
    ctcf = load_bed_intervals(ctcf_path)
    idx = build_interval_index(ctcf)
    obs_hits = sum(1 for c, s, e in anchors if overlaps_any(c, s, e, idx))
    n = len(anchors)
    obs_miss = n - obs_hits
    spans = chrom_spans(list(anchors) + list(ctcf))
    rng = random.Random(SEED)
    shuffle_rates: list[float] = []
    for _ in range(n_shuffles):
        shuffled: list[tuple[str, int, int]] = []
        for chrom, s, e in ctcf:
            length = e - s
            span = spans.get(chrom, e + 1_000_000)
            if span <= length:
                start = 0
            else:
                start = rng.randint(0, span - length)
            shuffled.append((chrom, start, start + length))
        sidx = build_interval_index(shuffled)
        hits = sum(1 for c, s, e in anchors if overlaps_any(c, s, e, sidx))
        shuffle_rates.append(hits / n if n else 0.0)
    null_rate = sum(shuffle_rates) / len(shuffle_rates) if shuffle_rates else 0.0
    null_hit = int(round(null_rate * n))
    null_hit = max(0, min(n, null_hit))
    null_miss = n - null_hit
    fisher_or, fisher_p = fisher_exact_two_sided(obs_hits, obs_miss, null_hit, null_miss)
    woolf_or, lo, hi = woolf_or_ci(obs_hits, obs_miss, null_hit, null_miss)
    rate_or = (obs_hits / n) / null_rate if null_rate > 0 else float("nan")
    verdict = "PASS" if fisher_or >= GATE_OR_THRESHOLD else "FAIL"
    return {
        "celltype": celltype,
        "hic_accession": hic_acc,
        "ctcf_accession": ctcf_acc,
        "n_anchors": n,
        "obs_ctcf_hits": obs_hits,
        "obs_rate": obs_hits / n if n else float("nan"),
        "null_rate_mean": null_rate,
        "n_shuffles": n_shuffles,
        "fisher_or": fisher_or,
        "fisher_p_two_sided": fisher_p,
        "woolf_or": woolf_or,
        "woolf_ci95_lo": lo,
        "woolf_ci95_hi": hi,
        "rate_ratio": rate_or,
        "gate_threshold": GATE_OR_THRESHOLD,
        "verdict": verdict,
    }


def replication_verdict(or_value: float) -> dict:
    """Replication arm thresholds for claim falsification."""
    if or_value >= MCID_SUPPORT:
        label = "SUPPORT_REPLICATION"
        note = (
            f"OR={or_value:.4f} ≥ {MCID_SUPPORT}; replication would support enrichment "
            "direction — does NOT alone upgrade claim without K562 MAPQ gate."
        )
    elif or_value < REPL_FAIL:
        label = "NULL_OR_OPPOSITE_REPLICATION"
        note = (
            f"OR={or_value:.4f} < {REPL_FAIL}; replication does not support enrichment "
            "(null or opposite). Combined with K562 OR<1.1 after mappability → claim REJECT."
        )
    else:
        label = "INCONCLUSIVE_REPLICATION"
        note = (
            f"OR={or_value:.4f} between {REPL_FAIL} and {MCID_SUPPORT}; "
            "replication inconclusive for falsification rule."
        )
    return {
        "verdict": label,
        "or": or_value,
        "mcid_support": MCID_SUPPORT,
        "replication_fail_lt": REPL_FAIL,
        "note": note,
    }


def run(
    pol2_path: Path,
    hic_path: Path,
    rmsk_path: Path,
    ctcf_path: Path | None,
    n_perm: int,
    n_boot: int,
    seed: int,
    *,
    celltype: str = "GM12878",
    cfg: dict[str, str] | None = None,
) -> dict:
    cfg = cfg or CELL_CONFIGS[celltype]
    raw_pol2 = load_bedpe_anchors(pol2_path)
    raw_hic = load_bedpe_anchors(hic_path)
    pol2_units = build_units(raw_pol2)
    hic_units = build_units(raw_hic)
    pol2 = midpoint_windows(pol2_units)
    hic = midpoint_windows(hic_units)

    rmsk_by = load_rmsk_by_name(rmsk_path, {PRIMARY_TE})
    pol2_hits = annotate_overlaps(pol2, rmsk_by, PRIMARY_TE)
    hic_hits = annotate_overlaps(hic, rmsk_by, PRIMARY_TE)
    primary = contingency_or(pol2_hits, hic_hits)

    boot = chrom_block_bootstrap_ci(pol2, hic, pol2_hits, hic_hits, n_boot, seed)
    perm = matched_null_permutations(
        pol2, hic, pol2_hits, hic_hits, n_perm=n_perm, seed=seed
    )
    rverdict = replication_verdict(primary["fisher_or"])

    ctcf_gate = None
    if ctcf_path is not None and ctcf_path.exists():
        ctcf_gate = run_ctcf_gate(
            hic_path,
            ctcf_path,
            celltype=celltype,
            hic_acc=cfg["hic_acc"],
            ctcf_acc=cfg["ctcf_acc"],
        )

    return {
        "script": "t5_replication_celltype",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembly": "GRCh38",
        "celltype": celltype,
        "status": "DONE",
        "primary_te": PRIMARY_TE,
        "unit_definition": {
            "description": (
                "Same as T3: non-redundant merged anchors ≥1 kb; AluSz on fixed "
                "1 kb midpoint windows"
            ),
            "min_anchor_bp": 1000,
            "scoring_window_bp": 1000,
        },
        "inputs": {
            "pol2_bedpe": str(pol2_path),
            "pol2_accession": cfg["pol2_acc"],
            "pol2_experiment": cfg["pol2_exp"],
            "hic_bedpe": str(hic_path),
            "hic_accession": cfg["hic_acc"],
            "hic_experiment": cfg["hic_exp"],
            "ctcf_accession": cfg["ctcf_acc"] if ctcf_path else None,
            "ctcf_experiment": cfg["ctcf_exp"] if ctcf_path else None,
            "rmsk": str(rmsk_path),
            "te_source": "UCSC hg38 RepeatMasker rmsk.txt.gz",
            "freeze": cfg["freeze"],
        },
        "anchor_counts": {
            "pol2_raw_unique": len(raw_pol2),
            "hic_raw_unique": len(raw_hic),
            "pol2_merged_ge1kb": len(pol2_units),
            "hic_merged_ge1kb": len(hic_units),
            "pol2_scoring_windows_1kb": len(pol2),
            "hic_scoring_windows_1kb": len(hic),
        },
        "ctcf_gate": ctcf_gate,
        "primary_result": {
            **primary,
            "te": PRIMARY_TE,
            "estimand": (
                f"Fisher OR for AluSz overlap in 1 kb midpoint windows: "
                f"Pol II ChIA-PET vs Hi-C ({celltype}, GRCh38)"
            ),
            "block_bootstrap": boot,
            "replication_verdict": rverdict,
        },
        "permutation_null": perm,
        "supports_enrichment": primary["fisher_or"] >= REPL_FAIL,
        "explicit_non_claims": [
            "Replication descriptive only — not causal",
            "Primary TE remains AluSz (no post-hoc switch)",
            "Holdout / C1 / wet untouched",
        ],
    }


def write_outputs(result: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    cell = result["celltype"].lower()
    json_path = RESULTS / f"replication_{cell}_OR_CI.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    primary = result["primary_result"]
    rv = primary["replication_verdict"]
    boot = primary.get("block_bootstrap", {})
    gate = result.get("ctcf_gate") or {}
    inp = result["inputs"]
    freeze = inp.get("freeze", "ACCESSION_FREEZE_replication_v1.md")
    md = f"""# Replication — AluSz OR ({result['celltype']})

**Computed:** `{result['computed_at_utc']}`  
**Status:** `{result['status']}`  
**Primary TE:** `{PRIMARY_TE}` (frozen; same as K562)  
**Replication verdict:** `{rv['verdict']}`

## Frozen accessions

| Role | Experiment | File |
|------|------------|------|
| Pol II ChIA-PET | `{inp['pol2_experiment']}` | `{inp['pol2_accession']}` |
| Hi-C loops | `{inp['hic_experiment']}` | `{inp['hic_accession']}` |
| CTCF peaks (gate) | `{inp.get('ctcf_experiment')}` | `{inp.get('ctcf_accession')}` |

See `{freeze}`.

## Pipeline

Identical to T3 K562 desk: merged ≥1 kb anchors; Fisher OR for AluSz on fixed 1 kb
midpoint windows. Descriptive association in processed public call sets only.

## Anchor counts

| Arm | Raw unique | Merged ≥1 kb | 1 kb windows |
|-----|------------|--------------|--------------|
| Pol II | {result['anchor_counts']['pol2_raw_unique']} | {result['anchor_counts']['pol2_merged_ge1kb']} | {result['anchor_counts']['pol2_scoring_windows_1kb']} |
| Hi-C | {result['anchor_counts']['hic_raw_unique']} | {result['anchor_counts']['hic_merged_ge1kb']} | {result['anchor_counts']['hic_scoring_windows_1kb']} |

## AluSz statistics

| Metric | Value |
|--------|-------|
| Pol II AluSz+ / n | {primary['a_pol2_te_pos']} / {primary['n_pol2']} (rate {primary['pol2_rate']:.4f}) |
| Hi-C AluSz+ / n | {primary['c_hic_te_pos']} / {primary['n_hic']} (rate {primary['hic_rate']:.4f}) |
| Fisher OR | **{primary['fisher_or']:.4f}** |
| Woolf 95% CI | {primary['woolf_ci95_lo']:.4f} – {primary['woolf_ci95_hi']:.4f} |
| Chrom block-bootstrap 95% CI | {boot.get('ci95_lo', float('nan')):.4f} – {boot.get('ci95_hi', float('nan')):.4f} |
| Matched-null emp. p | {result['permutation_null']['emp_p_two_sided']:.4g} (n_perm={result['permutation_null']['n_perm']}) |

**Verdict note:** {rv['note']}

## CTCF positive gate ({result['celltype']})

| Metric | Value |
|--------|-------|
| Fisher OR | {gate.get('fisher_or', float('nan')):.4f} |
| Woolf 95% CI | {gate.get('woolf_ci95_lo', float('nan')):.4f} – {gate.get('woolf_ci95_hi', float('nan')):.4f} |
| Gate threshold | ≥ {gate.get('gate_threshold', GATE_OR_THRESHOLD)} |
| Verdict | **{gate.get('verdict', 'N/A')}** |

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT a license to switch primary TE post-hoc.
3. NOT wet-lab / holdout / C1 authorization.
4. NOT multi-assay MAPQ on BAM (processed bedpe only).
"""
    (RESULTS / f"replication_{cell}_OR_CI.md").write_text(md + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--celltype",
        choices=sorted(CELL_CONFIGS.keys()),
        default="GM12878",
        help="Replication cell type (frozen accession set)",
    )
    ap.add_argument("--pol2", type=Path, default=None)
    ap.add_argument("--hic", type=Path, default=None)
    ap.add_argument("--rmsk", type=Path, default=DATA / "rmsk.txt.gz")
    ap.add_argument("--ctcf", type=Path, default=None)
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    cfg = CELL_CONFIGS[args.celltype]
    pol2 = args.pol2 or (DATA / f"{cfg['pol2_acc']}.bedpe.gz")
    hic = args.hic or (DATA / f"{cfg['hic_acc']}.bedpe.gz")
    ctcf_path = args.ctcf or (DATA / f"{cfg['ctcf_acc']}.bed.gz")

    for p, label in ((pol2, "Pol II"), (hic, "Hi-C"), (args.rmsk, "rmsk")):
        if not p.exists():
            print(f"Missing {label}: {p}", file=sys.stderr)
            return 1

    ctcf = ctcf_path if ctcf_path.exists() else None
    if ctcf is None:
        print(f"WARN: CTCF peaks missing at {ctcf_path}; gate skipped", file=sys.stderr)

    result = run(
        pol2,
        hic,
        args.rmsk,
        ctcf,
        n_perm=args.n_perm,
        n_boot=args.n_boot,
        seed=args.seed,
        celltype=args.celltype,
        cfg=cfg,
    )
    write_outputs(result)
    primary = result["primary_result"]
    print(
        json.dumps(
            {
                "celltype": result["celltype"],
                "fisher_or": primary["fisher_or"],
                "woolf_ci95": [
                    primary["woolf_ci95_lo"],
                    primary["woolf_ci95_hi"],
                ],
                "replication_verdict": primary["replication_verdict"]["verdict"],
                "ctcf_gate": (result.get("ctcf_gate") or {}).get("verdict"),
                "ctcf_gate_or": (result.get("ctcf_gate") or {}).get("fisher_or"),
                "n_pol2": primary["n_pol2"],
                "n_hic": primary["n_hic"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
