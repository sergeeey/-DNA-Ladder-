#!/usr/bin/env python3
"""T4 mappability / MAPQ-spirit sensitivity for primary AluSz OR (K562).

Preregistered kill-test (claim.md / controls.md):
  - Processed ENCODE bedpe lack per-anchor MAPQ → document MAPQ=N/A
  - Proxy: Hoffman/Karimzadeh Umap multi-read mappability (k100) mean over
    fixed 1 kb midpoint scoring windows
  - Primary filter: mean umap ≥ 0.3; report ≥ 0.5 as sensitivity
  - Recompute Fisher OR AluSz Pol II ChIA-PET vs Hi-C under each filter
  - If OR still < 1.1 after ≥0.3 → strengthens FAIL_DESK_PRIMARY

Does NOT change primary TE (AluSz). Does NOT touch holdout / C1 / wet.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyBigWig

# Reuse T3 helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t3_primary_alusz_or import (  # noqa: E402
    PRIMARY_TE,
    annotate_overlaps,
    build_units,
    contingency_or,
    load_bedpe_anchors,
    load_rmsk_by_name,
    midpoint_windows,
    woolf_or_ci,
)

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"

UMAP_DEFAULT = DATA / "k100.Umap.MultiTrackMappability.bw"
UMAP_URL = (
    "https://hgdownload.soe.ucsc.edu/gbdb/hg38/hoffmanMappability/"
    "k100.Umap.MultiTrackMappability.bw"
)
THRESHOLDS = (0.3, 0.5)
MCID_FAIL = 1.1


def mean_umap(
    bw: "pyBigWig.pyBigWig", anchors: list[tuple[str, int, int]]
) -> list[float]:
    """Mean multi-read umap over each interval; missing → 0.0."""
    out: list[float] = []
    chroms = bw.chroms() or {}
    for chrom, s, e in anchors:
        if chrom not in chroms:
            out.append(0.0)
            continue
        # clamp to chrom length
        clen = chroms[chrom]
        s2 = max(0, min(s, clen))
        e2 = max(s2 + 1, min(e, clen))
        try:
            m = bw.stats(chrom, s2, e2, type="mean")[0]
        except RuntimeError:
            m = None
        out.append(float(m) if m is not None else 0.0)
    return out


def filter_by_umap(
    anchors: list[tuple[str, int, int]],
    hits: list[bool],
    umap_means: list[float],
    thr: float,
) -> tuple[list[tuple[str, int, int]], list[bool], list[float]]:
    keep_a, keep_h, keep_u = [], [], []
    for a, h, u in zip(anchors, hits, umap_means):
        if u >= thr:
            keep_a.append(a)
            keep_h.append(h)
            keep_u.append(u)
    return keep_a, keep_h, keep_u


def or_block(
    pol2_hits: list[bool], hic_hits: list[bool], label: str, thr: float | None
) -> dict:
    row = contingency_or(pol2_hits, hic_hits)
    woolf_or, lo, hi = woolf_or_ci(
        row["a_pol2_te_pos"],
        row["b_pol2_te_neg"],
        row["c_hic_te_pos"],
        row["d_hic_te_neg"],
    )
    or_v = row["fisher_or"]
    return {
        **row,
        "label": label,
        "umap_threshold": thr,
        "te": PRIMARY_TE,
        "woolf_or": woolf_or,
        "woolf_ci95_lo": lo,
        "woolf_ci95_hi": hi,
        "below_fail_threshold_1_1": or_v < MCID_FAIL,
        "desk_note": (
            f"OR={or_v:.4f} {'<' if or_v < MCID_FAIL else '≥'} {MCID_FAIL} "
            f"({'strengthens FAIL' if or_v < MCID_FAIL else 'does not strengthen FAIL'})"
        ),
    }


def run(
    pol2_path: Path,
    hic_path: Path,
    rmsk_path: Path,
    umap_path: Path,
) -> dict:
    raw_pol2 = load_bedpe_anchors(pol2_path)
    raw_hic = load_bedpe_anchors(hic_path)
    pol2_units = build_units(raw_pol2)
    hic_units = build_units(raw_hic)
    pol2 = midpoint_windows(pol2_units)
    hic = midpoint_windows(hic_units)

    rmsk_by = load_rmsk_by_name(rmsk_path, {PRIMARY_TE})
    pol2_hits = annotate_overlaps(pol2, rmsk_by, PRIMARY_TE)
    hic_hits = annotate_overlaps(hic, rmsk_by, PRIMARY_TE)

    bw = pyBigWig.open(str(umap_path))
    if bw is None:
        raise RuntimeError(f"Cannot open umap bigWig: {umap_path}")
    try:
        pol2_umap = mean_umap(bw, pol2)
        hic_umap = mean_umap(bw, hic)
    finally:
        bw.close()

    unfiltered = or_block(pol2_hits, hic_hits, "unfiltered_baseline", None)
    filtered: dict[str, dict] = {}
    for thr in THRESHOLDS:
        p2_a, p2_h, p2_u = filter_by_umap(pol2, pol2_hits, pol2_umap, thr)
        hc_a, hc_h, hc_u = filter_by_umap(hic, hic_hits, hic_umap, thr)
        block = or_block(p2_h, hc_h, f"umap_ge_{thr}", thr)
        block["n_pol2_kept"] = len(p2_a)
        block["n_hic_kept"] = len(hc_a)
        block["frac_pol2_kept"] = len(p2_a) / len(pol2) if pol2 else float("nan")
        block["frac_hic_kept"] = len(hc_a) / len(hic) if hic else float("nan")
        block["mean_umap_pol2_kept"] = (
            sum(p2_u) / len(p2_u) if p2_u else float("nan")
        )
        block["mean_umap_hic_kept"] = (
            sum(hc_u) / len(hc_u) if hc_u else float("nan")
        )
        filtered[f"ge_{thr}"] = block

    primary_thr = filtered["ge_0.3"]
    strengthens = bool(primary_thr["below_fail_threshold_1_1"])

    return {
        "script": "t4_mappability_sensitivity",
        "experiment": "exp_te_loop_assay_discordance_chia_vs_hic",
        "candidate_id": "C-A1",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembly": "GRCh38",
        "primary_te": PRIMARY_TE,
        "mapq": {
            "status": "N/A",
            "note": (
                "Processed ENCODE bedpe ENCFF511QFN (7-col ChIA-PET clusters) and "
                "ENCFF693XIL (HiCCUPS bedpe) lack per-anchor MAPQ fields usable for "
                "MAPQ≥30 filtering. Umap mean ≥0.3 is the preregistered proxy for "
                "'MAPQ≥30 spirit' (claim.md / controls.md)."
            ),
        },
        "umap_track": {
            "source": "Hoffman lab Umap / Karimzadeh et al. NAR 2018",
            "file": "k100.Umap.MultiTrackMappability.bw",
            "url": UMAP_URL,
            "measure": "multi-read mappability, k=100",
            "annotation": "mean over fixed 1 kb midpoint scoring windows",
            "path": str(umap_path),
            "on_disk_md5": _md5_if_sidecar(umap_path),
        },
        "inputs": {
            "pol2_bedpe": str(pol2_path),
            "pol2_accession": "ENCFF511QFN",
            "hic_bedpe": str(hic_path),
            "hic_accession": "ENCFF693XIL",
            "rmsk": str(rmsk_path),
        },
        "anchor_counts_unfiltered": {
            "n_pol2": len(pol2),
            "n_hic": len(hic),
            "mean_umap_pol2": sum(pol2_umap) / len(pol2_umap) if pol2_umap else None,
            "mean_umap_hic": sum(hic_umap) / len(hic_umap) if hic_umap else None,
        },
        "unfiltered_baseline": unfiltered,
        "filters": filtered,
        "verdict": {
            "primary_filter": "mean_umap_ge_0.3",
            "or_ge_0_3": primary_thr["fisher_or"],
            "or_ge_0_5": filtered["ge_0.5"]["fisher_or"],
            "strengthens_fail": strengthens,
            "note": (
                "After umap≥0.3, AluSz OR remains <1.1 → strengthens FAIL_DESK_PRIMARY "
                "(MAPQ-spirit proxy). Full claim REJECT still needs replication arm."
                if strengthens
                else "After umap≥0.3, OR not <1.1 — does not alone meet falsification."
            ),
        },
        "explicit_non_claims": [
            "MAPQ=N/A on processed bedpe; umap is proxy only",
            "No post-hoc primary TE switch",
            "No causal / wet / holdout / C1 claims",
        ],
    }


def _md5_if_sidecar(path: Path) -> str | None:
    side = Path(str(path) + ".md5")
    if side.exists():
        txt = side.read_text(encoding="utf-8").strip().split()[0]
        return txt
    return None


def write_outputs(result: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS / "sensitivity_mappability.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    f03 = result["filters"]["ge_0.3"]
    f05 = result["filters"]["ge_0.5"]
    base = result["unfiltered_baseline"]
    md = f"""# Mappability sensitivity — AluSz OR (T4)

**Computed:** `{result['computed_at_utc']}`  
**Primary TE:** `{PRIMARY_TE}` (frozen)  
**MAPQ:** `{result['mapq']['status']}`  
**Umap track:** `{result['umap_track']['file']}` (k100 multi-read)

## MAPQ status

{result['mapq']['note']}

## Estimand

Same as T3 primary: Fisher OR for AluSz overlap in fixed 1 kb midpoint windows of
merged ≥1 kb anchors, Pol II ChIA-PET (`ENCFF511QFN`) vs Hi-C (`ENCFF693XIL`), K562 /
GRCh38 — restricted to windows with mean Umap ≥ threshold.

## Results

| Filter | n Pol II | n Hi-C | AluSz+ Pol II / Hi-C | Fisher OR | Woolf 95% CI | OR < 1.1 |
|--------|----------|--------|----------------------|-----------|--------------|----------|
| Unfiltered (T3 baseline) | {base['n_pol2']} | {base['n_hic']} | {base['a_pol2_te_pos']} / {base['c_hic_te_pos']} | **{base['fisher_or']:.4f}** | {base['woolf_ci95_lo']:.4f}–{base['woolf_ci95_hi']:.4f} | {base['below_fail_threshold_1_1']} |
| Mean umap ≥ 0.3 (primary) | {f03['n_pol2_kept']} | {f03['n_hic_kept']} | {f03['a_pol2_te_pos']} / {f03['c_hic_te_pos']} | **{f03['fisher_or']:.4f}** | {f03['woolf_ci95_lo']:.4f}–{f03['woolf_ci95_hi']:.4f} | {f03['below_fail_threshold_1_1']} |
| Mean umap ≥ 0.5 (sensitivity) | {f05['n_pol2_kept']} | {f05['n_hic_kept']} | {f05['a_pol2_te_pos']} / {f05['c_hic_te_pos']} | **{f05['fisher_or']:.4f}** | {f05['woolf_ci95_lo']:.4f}–{f05['woolf_ci95_hi']:.4f} | {f05['below_fail_threshold_1_1']} |

**Retention:** umap≥0.3 keeps {f03['frac_pol2_kept']:.1%} Pol II / {f03['frac_hic_kept']:.1%} Hi-C;
umap≥0.5 keeps {f05['frac_pol2_kept']:.1%} / {f05['frac_hic_kept']:.1%}.

## Verdict

- Primary filter umap≥0.3 OR = **{f03['fisher_or']:.4f}**
- Sensitivity umap≥0.5 OR = **{f05['fisher_or']:.4f}**
- Strengthens FAIL: **{result['verdict']['strengthens_fail']}**

{result['verdict']['note']}

## What this does NOT mean

1. NOT a causal TE → loop claim.
2. NOT proof that mappability "explains" the null (OR already <1.1 unfiltered).
3. NOT MAPQ≥30 on raw BAM (unavailable here) — umap proxy only.
4. NOT claim-level REJECT without the replication arm.
"""
    (RESULTS / "sensitivity_mappability.md").write_text(md + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pol2", type=Path, default=DATA / "ENCFF511QFN.bedpe.gz")
    ap.add_argument("--hic", type=Path, default=DATA / "ENCFF693XIL.bedpe.gz")
    ap.add_argument("--rmsk", type=Path, default=DATA / "rmsk.txt.gz")
    ap.add_argument("--umap", type=Path, default=UMAP_DEFAULT)
    args = ap.parse_args()

    for p, label in (
        (args.pol2, "Pol II bedpe"),
        (args.hic, "Hi-C bedpe"),
        (args.rmsk, "rmsk"),
        (args.umap, "umap bigWig"),
    ):
        if not p.exists():
            print(f"Missing {label}: {p}", file=sys.stderr)
            return 1

    result = run(args.pol2, args.hic, args.rmsk, args.umap)
    write_outputs(result)
    print(
        json.dumps(
            {
                "or_unfiltered": result["unfiltered_baseline"]["fisher_or"],
                "or_umap_ge_0.3": result["filters"]["ge_0.3"]["fisher_or"],
                "or_umap_ge_0.5": result["filters"]["ge_0.5"]["fisher_or"],
                "strengthens_fail": result["verdict"]["strengthens_fail"],
                "mapq": result["mapq"]["status"],
            },
            indent=2,
        )
    )
    print(f"Wrote {RESULTS / 'sensitivity_mappability.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
