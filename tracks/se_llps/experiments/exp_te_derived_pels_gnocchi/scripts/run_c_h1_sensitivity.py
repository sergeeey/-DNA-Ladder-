#!/usr/bin/env python3
"""C-H1 robustness / sensitivity (post-SUPPORT).

Non-primary checks (do not change primary claim.md gates):
  1) Alternate matching: seed swap; drop TSS; coarser GC bins (q5)
  2) TE class split: SINE / LINE / LTR exposures (re-match each)
  3) Exclude ENCODE blacklist-overlapping cCREs
  4) Chromosome holdout: leave-one-chrom-out mean |Δ|; odd vs even chroms

Second Gnocchi build: not available on public gnomAD-nc-constraint v31 paper
bucket at probe time → documented SKIP (QC 1kb only).

Robustness rule (desk):
  - ROBUST_SUPPORT if every pre-registered sensitivity keeps |Δ| ≥ 0.15
    (TE class splits report-only if n too small; still tabulated)
  - SUPPORT_WITH_CAVEATS if primary holds but ≥1 sensitivity drops to
    [0.05, 0.15) or TE-class direction flips
  - FRAGILE if any core sensitivity (alt-match / blacklist / chr-holdout)
    falls into kill |Δ| < 0.05

Forbidden language: wet / pathogenicity / causal TE→constraint.
"""

from __future__ import annotations

import gzip
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
INP = ROOT / "data" / "input"
RES = ROOT / "results"
SE_ROOT = ROOT.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(SE_ROOT / "scripts"))

from c_h1_lib import (  # noqa: E402
    KEEP_CHROMS,
    KILL_ABS_DELTA,
    RNG_SEED,
    SUPPORT_ABS_DELTA,
    TE_CLASSES,
    bootstrap_mean_ci,
    cliffs_delta,
    group_by_key,
    is_registry_pels,
    match_1to1,
    quantile_bins,
    tss_dist_bin,
    verdict_from_abs_delta,
)
from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    load_gnocchi_windows,
    weighted_mean_z,
)
from run_c_h1_analysis import (  # noqa: E402
    annotate_overlaps,
    gc_for_regions,
    load_registry_pels,
    load_tss,
    nearest_tss_dist,
)
N_BOOT = 2000  # lighter than primary for sensitivity battery
ALT_SEED = 20260721
CLASS_SPLIT = ("SINE", "LINE", "LTR")


def load_rmsk_by_class(
    path: Path, classes: frozenset[str] | set[str]
) -> dict[str, dict[str, list[tuple[int, int]]]]:
    """chrom -> repClass -> intervals."""
    out: dict[str, dict[str, list[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 12:
                continue
            chrom = p[5]
            if chrom not in KEEP_CHROMS:
                continue
            rep_class = p[11]
            if rep_class not in classes:
                continue
            start, end = int(p[6]), int(p[7])
            out[chrom][rep_class].append((start, end))
    for chrom in out:
        for rc in out[chrom]:
            out[chrom][rc].sort()
    return out


def merge_classes(
    by_class: dict[str, dict[str, list[tuple[int, int]]]],
    keep: set[str] | frozenset[str],
) -> dict[str, list[tuple[int, int]]]:
    te: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for chrom, cmap in by_class.items():
        for rc, ivs in cmap.items():
            if rc in keep:
                te[chrom].extend(ivs)
        te[chrom].sort()
    return te


def load_blacklist(path: Path) -> dict[str, list[tuple[int, int]]]:
    bl: dict[str, list[tuple[int, int]]] = defaultdict(list)
    opener = gzip.open if str(path).endswith(".gz") else open
    mode = "rt" if str(path).endswith(".gz") else "r"
    with opener(path, mode, encoding="utf-8", errors="replace") as fh:  # type: ignore[arg-type]
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            chrom = p[0]
            if chrom not in KEEP_CHROMS:
                continue
            bl[chrom].append((int(p[1]), int(p[2])))
    for c in bl:
        bl[c].sort()
    return bl


def build_keys(
    ids: list[str],
    pels: dict[str, tuple[str, int, int]],
    gc: dict[str, float],
    tss: dict[str, np.ndarray],
    *,
    n_gc_bins: int,
    include_tss: bool,
) -> dict[str, tuple]:
    lengths = np.array([pels[i][2] - pels[i][1] for i in ids], dtype=float)
    gcv = np.array([gc[i] for i in ids], dtype=float)
    length_bins = quantile_bins(lengths, 4)
    gc_bins = quantile_bins(gcv, n_gc_bins)
    keys: dict[str, tuple] = {}
    for i, eid in enumerate(ids):
        chrom, s, e = pels[eid]
        if include_tss:
            mid = (s + e) // 2
            d = nearest_tss_dist(tss.get(chrom, np.array([], dtype=np.int64)), mid)
            keys[eid] = (chrom, int(length_bins[i]), int(gc_bins[i]), tss_dist_bin(d))
        else:
            keys[eid] = (chrom, int(length_bins[i]), int(gc_bins[i]))
    return keys


def score_matched(
    matched: dict[str, str | None],
    pels: dict[str, tuple[str, int, int]],
    gnocchi: dict,
    *,
    chrom_filter: set[str] | None = None,
) -> dict:
    pairs_z: list[tuple[float, float]] = []
    n_missing = 0
    n_matched = 0
    for te_id, ctrl_id in matched.items():
        if ctrl_id is None:
            continue
        c1, s1, e1 = pels[te_id]
        if chrom_filter is not None and c1 not in chrom_filter:
            continue
        n_matched += 1
        c2, s2, e2 = pels[ctrl_id]
        z1 = weighted_mean_z(c1, s1, e1, gnocchi)
        z2 = weighted_mean_z(c2, s2, e2, gnocchi)
        if z1 is None or z2 is None:
            n_missing += 1
            continue
        pairs_z.append((z1, z2))
    diffs = [a - b for a, b in pairs_z]
    if not diffs:
        return {
            "n_matched_pairs_scored": n_matched,
            "n_pairs_with_gnocchi": 0,
            "n_pairs_dropped_no_coverage": n_missing,
            "mean_delta_te_minus_nonte": None,
            "abs_mean_delta": None,
            "bootstrap_ci95_mean_delta": [None, None],
            "cliffs_delta": None,
            "verdict": "BLOCKED_DATA",
        }
    mean_delta, ci_lo, ci_hi = bootstrap_mean_ci(diffs, N_BOOT, RNG_SEED)
    abs_delta = abs(mean_delta)
    z_te = [a for a, _ in pairs_z]
    z_ctrl = [b for _, b in pairs_z]
    return {
        "n_matched_pairs_scored": n_matched,
        "n_pairs_with_gnocchi": len(pairs_z),
        "n_pairs_dropped_no_coverage": n_missing,
        "mean_z_te": float(np.mean(z_te)),
        "mean_z_non_te": float(np.mean(z_ctrl)),
        "mean_delta_te_minus_nonte": mean_delta,
        "abs_mean_delta": abs_delta,
        "bootstrap_ci95_mean_delta": [ci_lo, ci_hi],
        "cliffs_delta": cliffs_delta(z_te, z_ctrl),
        "verdict": verdict_from_abs_delta(abs_delta),
    }


def run_scenario(
    name: str,
    te_ids: list[str],
    non_te_ids: list[str],
    keys: dict[str, tuple],
    pels: dict[str, tuple[str, int, int]],
    gnocchi: dict,
    *,
    seed: int,
    chrom_filter: set[str] | None = None,
) -> dict:
    te_exposed = [eid for eid in te_ids if eid in keys]
    non_te_pool = [eid for eid in non_te_ids if eid in keys]
    pool_by_key = group_by_key(non_te_pool, keys)
    exposed_keys = [(eid, keys[eid]) for eid in te_exposed]
    matched = match_1to1(exposed_keys, pool_by_key, seed=seed)
    n_lock = sum(1 for v in matched.values() if v is not None)
    scored = score_matched(matched, pels, gnocchi, chrom_filter=chrom_filter)
    return {
        "scenario": name,
        "seed": seed,
        "n_te_exposed": len(te_exposed),
        "n_non_te_pool": len(non_te_pool),
        "n_matched_pairs_lock": n_lock,
        **scored,
    }


def chrom_parity(chrom: str) -> str:
    if chrom == "chrX":
        return "even"  # park X with even for binary split
    try:
        n = int(chrom.replace("chr", ""))
    except ValueError:
        return "other"
    return "odd" if n % 2 else "even"


def main() -> None:
    t0 = time.time()
    RES.mkdir(parents=True, exist_ok=True)
    reg_path = INP / "GRCh38-cCREs.Registry-V3.bed"
    rmsk_path = INP / "rmsk.txt.gz"
    twobit_path = INP / "hg38.2bit"
    gencode_path = INP / "gencode.v47.basic.annotation.gtf.gz"
    gnocchi_path = INP / "gnocchi_constraint_z_genome_1kb_qc.txt.gz"
    bl_path = INP / "encode_blacklist_hg38.bed"
    if not bl_path.exists():
        bl_path = INP / "encode_blacklist_hg38.bed.gz"
    for p in (reg_path, rmsk_path, twobit_path, gencode_path, gnocchi_path, bl_path):
        if not p.exists():
            raise SystemExit(f"BLOCKED_DATA missing input: {p}")

    print("=== Load universe ===", flush=True)
    pels = load_registry_pels(reg_path)
    print(f"pELS={len(pels)}", flush=True)
    by_class = load_rmsk_by_class(rmsk_path, TE_CLASSES)
    te_all = merge_classes(by_class, TE_CLASSES)
    te_ids_all = sorted(annotate_overlaps(pels, te_all))
    non_te_ids = [eid for eid in pels if eid not in set(te_ids_all)]
    print(f"TE∩pELS={len(te_ids_all)} non-TE={len(non_te_ids)}", flush=True)

    tss = load_tss(gencode_path)
    print("GC…", flush=True)
    gc = gc_for_regions(pels, twobit_path)
    ids = [i for i in pels if np.isfinite(gc.get(i, np.nan))]
    print(f"finite GC={len(ids)}", flush=True)

    print("Gnocchi…", flush=True)
    import gnocchi_constraint_se_vs_typical_analysis as gmod

    gmod.GNOCCHI_FILE = gnocchi_path.resolve()
    gnocchi = load_gnocchi_windows()

    bl = load_blacklist(bl_path)
    bl_hits = annotate_overlaps(pels, bl)
    print(f"blacklist∩pELS={len(bl_hits)}", flush=True)

    scenarios: list[dict] = []

    # --- Primary-like baseline recompute (sanity) ---
    keys_primary = build_keys(ids, pels, gc, tss, n_gc_bins=10, include_tss=True)
    scenarios.append(
        run_scenario(
            "primary_recompute_seed_20260720",
            te_ids_all,
            non_te_ids,
            keys_primary,
            pels,
            gnocchi,
            seed=RNG_SEED,
        )
    )

    # --- Alternate matching ---
    scenarios.append(
        run_scenario(
            "alt_match_seed_20260721",
            te_ids_all,
            non_te_ids,
            keys_primary,
            pels,
            gnocchi,
            seed=ALT_SEED,
        )
    )
    keys_no_tss = build_keys(ids, pels, gc, tss, n_gc_bins=10, include_tss=False)
    scenarios.append(
        run_scenario(
            "alt_match_no_tss",
            te_ids_all,
            non_te_ids,
            keys_no_tss,
            pels,
            gnocchi,
            seed=RNG_SEED,
        )
    )
    keys_gc5 = build_keys(ids, pels, gc, tss, n_gc_bins=5, include_tss=True)
    scenarios.append(
        run_scenario(
            "alt_match_gc_bins_q5",
            te_ids_all,
            non_te_ids,
            keys_gc5,
            pels,
            gnocchi,
            seed=RNG_SEED,
        )
    )

    # --- Blacklist exclude ---
    te_no_bl = [e for e in te_ids_all if e not in bl_hits]
    non_te_no_bl = [e for e in non_te_ids if e not in bl_hits]
    scenarios.append(
        run_scenario(
            "exclude_encode_blacklist",
            te_no_bl,
            non_te_no_bl,
            keys_primary,
            pels,
            gnocchi,
            seed=RNG_SEED,
        )
    )

    # --- TE class splits ---
    for rc in CLASS_SPLIT:
        te_rc = merge_classes(by_class, {rc})
        te_ids_rc = sorted(annotate_overlaps(pels, te_rc))
        # comparator remains non-TE (zero any TE class), not "non-this-class"
        scenarios.append(
            run_scenario(
                f"te_class_{rc}",
                te_ids_rc,
                non_te_ids,
                keys_primary,
                pels,
                gnocchi,
                seed=RNG_SEED,
            )
        )

    # --- Chromosome holdouts ---
    chroms = sorted({pels[i][0] for i in ids})
    loco_abs: list[float] = []
    loco_rows: list[dict] = []
    for held in chroms:
        keep = set(chroms) - {held}
        row = run_scenario(
            f"loco_holdout_{held}",
            te_ids_all,
            non_te_ids,
            keys_primary,
            pels,
            gnocchi,
            seed=RNG_SEED,
            chrom_filter=keep,
        )
        loco_rows.append(row)
        if row.get("abs_mean_delta") is not None:
            loco_abs.append(float(row["abs_mean_delta"]))
    loco_summary = {
        "scenario": "chromosome_loco_summary",
        "n_chroms": len(chroms),
        "abs_delta_mean_across_loco": float(np.mean(loco_abs)) if loco_abs else None,
        "abs_delta_min_across_loco": float(np.min(loco_abs)) if loco_abs else None,
        "abs_delta_max_across_loco": float(np.max(loco_abs)) if loco_abs else None,
        "n_loco_below_support_0_15": sum(1 for x in loco_abs if x < SUPPORT_ABS_DELTA),
        "n_loco_below_kill_0_05": sum(1 for x in loco_abs if x < KILL_ABS_DELTA),
        "verdict_min_abs": (
            verdict_from_abs_delta(float(np.min(loco_abs))) if loco_abs else "BLOCKED_DATA"
        ),
    }

    odd_chroms = {c for c in chroms if chrom_parity(c) == "odd"}
    even_chroms = {c for c in chroms if chrom_parity(c) == "even"}
    scenarios.append(
        run_scenario(
            "chrom_parity_odd",
            te_ids_all,
            non_te_ids,
            keys_primary,
            pels,
            gnocchi,
            seed=RNG_SEED,
            chrom_filter=odd_chroms,
        )
    )
    scenarios.append(
        run_scenario(
            "chrom_parity_even",
            te_ids_all,
            non_te_ids,
            keys_primary,
            pels,
            gnocchi,
            seed=RNG_SEED,
            chrom_filter=even_chroms,
        )
    )

    # Core scenarios for robust verdict (exclude per-chrom LOCO rows; use summary)
    core_names = {
        "primary_recompute_seed_20260720",
        "alt_match_seed_20260721",
        "alt_match_no_tss",
        "alt_match_gc_bins_q5",
        "exclude_encode_blacklist",
        "chrom_parity_odd",
        "chrom_parity_even",
    }
    class_names = {f"te_class_{rc}" for rc in CLASS_SPLIT}

    core = [s for s in scenarios if s["scenario"] in core_names]
    class_rows = [s for s in scenarios if s["scenario"] in class_names]

    def abs_ok(row: dict, thr: float) -> bool:
        v = row.get("abs_mean_delta")
        return v is not None and float(v) >= thr

    core_all_support = all(abs_ok(s, SUPPORT_ABS_DELTA) for s in core) and abs_ok(
        {"abs_mean_delta": loco_summary["abs_delta_min_across_loco"]}, SUPPORT_ABS_DELTA
    )
    core_any_kill = any(
        s.get("abs_mean_delta") is not None
        and float(s["abs_mean_delta"]) < KILL_ABS_DELTA
        for s in core
    ) or (
        loco_summary["abs_delta_min_across_loco"] is not None
        and float(loco_summary["abs_delta_min_across_loco"]) < KILL_ABS_DELTA
    )
    class_all_support = all(abs_ok(s, SUPPORT_ABS_DELTA) for s in class_rows)
    class_any_kill = any(
        s.get("abs_mean_delta") is not None
        and float(s["abs_mean_delta"]) < KILL_ABS_DELTA
        for s in class_rows
    )
    class_dir = [
        float(s["mean_delta_te_minus_nonte"])
        for s in class_rows
        if s.get("mean_delta_te_minus_nonte") is not None
    ]
    primary_dir = next(
        float(s["mean_delta_te_minus_nonte"])
        for s in scenarios
        if s["scenario"] == "primary_recompute_seed_20260720"
    )
    class_flip = any((d > 0) != (primary_dir > 0) for d in class_dir)

    if core_any_kill:
        robust_verdict = "FRAGILE"
    elif core_all_support and class_all_support and not class_flip:
        robust_verdict = "ROBUST_SUPPORT"
    elif core_all_support and (not class_all_support or class_flip):
        # primary + core match/blacklist/chr hold; class split caveats
        robust_verdict = "SUPPORT_WITH_CAVEATS"
    else:
        robust_verdict = "SUPPORT_WITH_CAVEATS"

    out = {
        "experiment": "exp_te_derived_pels_gnocchi",
        "candidate_id": "C-H1",
        "analysis": "sensitivity_robustness",
        "date": "2026-07-21",
        "support_threshold_abs_delta": SUPPORT_ABS_DELTA,
        "kill_threshold_abs_delta": KILL_ABS_DELTA,
        "second_gnocchi_build": {
            "status": "UNAVAILABLE",
            "note": (
                "Public gnomAD-nc-constraint-v31-paper bucket returns 404 for "
                "non-QC alternate 1kb builds at probe; only QC download used "
                "(constraint_z_genome_1kb.qc.download.txt.gz)."
            ),
        },
        "blacklist": {
            "path": str(bl_path.name),
            "n_pels_overlapping": len(bl_hits),
        },
        "scenarios": scenarios,
        "chromosome_loco_rows": loco_rows,
        "chromosome_loco_summary": loco_summary,
        "robust_verdict": robust_verdict,
        "robust_rule": {
            "core_scenarios": sorted(core_names),
            "class_split_report": sorted(class_names),
            "ROBUST_SUPPORT": "all core + LOCO-min + class splits |Δ|≥0.15; no class direction flip",
            "SUPPORT_WITH_CAVEATS": "primary/core hold ≥0.15 but class split or LOCO gray/caveat",
            "FRAGILE": "any core/LOCO-min |Δ|<0.05",
        },
        "core_all_support": core_all_support,
        "class_all_support": class_all_support,
        "class_direction_flip_vs_primary": class_flip,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    path = RES / "sensitivity_result.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in (
        "robust_verdict",
        "core_all_support",
        "class_all_support",
        "class_direction_flip_vs_primary",
        "chromosome_loco_summary",
        "elapsed_sec",
    )}, indent=2))
    print("Scenarios |Δ|:")
    for s in scenarios:
        print(
            f"  {s['scenario']}: abs={s.get('abs_mean_delta')} "
            f"n={s.get('n_pairs_with_gnocchi')} verdict={s.get('verdict')}"
        )
    print(
        f"LOCO min|Δ|={loco_summary['abs_delta_min_across_loco']} "
        f"mean={loco_summary['abs_delta_mean_across_loco']}"
    )
    print(f"Saved {path}", flush=True)


if __name__ == "__main__":
    main()
