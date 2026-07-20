#!/usr/bin/env python3
"""C-H1 pipeline: TE-derived pELS vs matched non-TE pELS Gnocchi Δ.

Phases:
  A) Universe + covariates (GC/length/TSS) — NO Gnocchi
  B) TE vs non-TE; 1:1 match; write matching_lock.json
  C) Attach Gnocchi Z; mean Δ + CI + Cliff's δ; primary |Δ|
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
SE_ROOT = ROOT.parent.parent  # tracks/se_llps
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
    paired_permutation_p,
    quantile_bins,
    tss_dist_bin,
    verdict_from_abs_delta,
)
from gnocchi_constraint_se_vs_typical_analysis import (  # noqa: E402
    load_gnocchi_windows,
    weighted_mean_z,
)
from twobit import TwoBitFile  # noqa: E402

N_PERM = 10_000
N_BOOT = 5_000


def load_registry_pels(path: Path) -> dict[str, tuple[str, int, int]]:
    out: dict[str, tuple[str, int, int]] = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 6:
                continue
            chrom, start, end, eid, klass = p[0], int(p[1]), int(p[2]), p[4], p[5]
            if chrom not in KEEP_CHROMS:
                continue
            if not is_registry_pels(klass):
                continue
            out[eid] = (chrom, start, end)
    return out


def load_tss(path: Path) -> dict[str, np.ndarray]:
    by: dict[str, list[int]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 9 or cols[2] != "gene":
                continue
            if 'gene_type "protein_coding"' not in cols[8]:
                continue
            chrom = cols[0]
            if chrom not in KEEP_CHROMS:
                continue
            start, end = int(cols[3]), int(cols[4])
            strand = cols[6]
            tss = start if strand == "+" else end
            by[chrom].append(tss)
    return {c: np.array(sorted(v), dtype=np.int64) for c, v in by.items()}


def nearest_tss_dist(tss: np.ndarray, mid: int) -> int:
    if tss.size == 0:
        return 10**9
    i = int(np.searchsorted(tss, mid))
    best = 10**9
    if i < tss.size:
        best = min(best, abs(int(tss[i]) - mid))
    if i > 0:
        best = min(best, abs(int(tss[i - 1]) - mid))
    return best


def load_rmsk_te(path: Path) -> dict[str, list[tuple[int, int]]]:
    te: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 12:
                continue
            chrom = p[5]
            if chrom not in KEEP_CHROMS:
                continue
            start, end = int(p[6]), int(p[7])
            rep_class = p[11]
            if rep_class in TE_CLASSES:
                te[chrom].append((start, end))
    for c in te:
        te[c].sort()
    return te


def annotate_overlaps(
    regions: dict[str, tuple[str, int, int]],
    intervals: dict[str, list[tuple[int, int]]],
) -> set[str]:
    by_chrom: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for eid, (chrom, s, e) in regions.items():
        by_chrom[chrom].append((s, e, eid))
    hits: set[str] = set()
    for chrom, rows in by_chrom.items():
        rows.sort()
        iv = intervals.get(chrom, [])
        j0 = 0
        for s, e, eid in rows:
            while j0 < len(iv) and iv[j0][1] <= s:
                j0 += 1
            j = j0
            while j < len(iv) and iv[j][0] < e:
                if iv[j][1] > s:
                    hits.add(eid)
                    break
                j += 1
    return hits


def gc_for_regions(
    regions: dict[str, tuple[str, int, int]], twobit_path: Path
) -> dict[str, float]:
    by_chrom: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    for eid, (chrom, s, e) in regions.items():
        by_chrom[chrom].append((eid, s, e))
    out: dict[str, float] = {}
    with TwoBitFile(twobit_path) as tb:
        for chrom, rows in by_chrom.items():
            tb._load_meta(chrom)
            dna_size, n_regions, _m, packed_off = tb._seq_meta[chrom]
            byte_len = (dna_size + 3) // 4
            tb.fh.seek(packed_off)
            blob = np.frombuffer(tb.fh.read(byte_len), dtype=np.uint8)
            shifts = np.array([6, 4, 2, 0], dtype=np.uint8)
            codes = np.empty(byte_len * 4, dtype=np.uint8)
            for i, sh in enumerate(shifts):
                codes[i::4] = (blob >> sh) & np.uint8(3)
            codes = codes[:dna_size]
            is_gc = ((codes == 1) | (codes == 3)).astype(np.int32)
            is_atgc = np.ones(dna_size, dtype=np.int32)
            for ns, nsz in n_regions:
                is_gc[ns : ns + nsz] = 0
                is_atgc[ns : ns + nsz] = 0
            ps_gc = np.zeros(dna_size + 1, dtype=np.int64)
            ps_at = np.zeros(dna_size + 1, dtype=np.int64)
            np.cumsum(is_gc, out=ps_gc[1:])
            np.cumsum(is_atgc, out=ps_at[1:])
            for eid, s, e in rows:
                e2 = min(e, dna_size)
                s2 = max(s, 0)
                if e2 <= s2:
                    out[eid] = float("nan")
                    continue
                gc = int(ps_gc[e2] - ps_gc[s2])
                atgc = int(ps_at[e2] - ps_at[s2])
                out[eid] = (gc / atgc) if atgc else float("nan")
            print(f"  GC done {chrom} n={len(rows)}", flush=True)
            del codes, is_gc, is_atgc, ps_gc, ps_at, blob
    return out


def main() -> None:
    t0 = time.time()
    RES.mkdir(parents=True, exist_ok=True)
    reg_path = INP / "GRCh38-cCREs.Registry-V3.bed"
    rmsk_path = INP / "rmsk.txt.gz"
    twobit_path = INP / "hg38.2bit"
    gencode_path = INP / "gencode.v47.basic.annotation.gtf.gz"
    gnocchi_path = INP / "gnocchi_constraint_z_genome_1kb_qc.txt.gz"
    for p in (reg_path, rmsk_path, twobit_path, gencode_path, gnocchi_path):
        if not p.exists():
            raise SystemExit(f"BLOCKED_DATA missing input: {p}")

    print("=== Phase A: pELS universe + covariates (no Gnocchi) ===", flush=True)
    pels = load_registry_pels(reg_path)
    print(f"registry pELS (chr1-22,X): {len(pels)}", flush=True)

    print("loading rmsk TE…", flush=True)
    te_iv = load_rmsk_te(rmsk_path)
    te_ids = annotate_overlaps(pels, te_iv)
    non_te_ids = [eid for eid in pels if eid not in te_ids]
    te_list = sorted(eid for eid in te_ids if eid in pels)
    print(f"TE∩pELS={len(te_list)}  non-TE pELS pool={len(non_te_ids)}", flush=True)

    print("loading TSS…", flush=True)
    tss = load_tss(gencode_path)

    print("computing GC…", flush=True)
    gc = gc_for_regions(pels, twobit_path)

    ids = list(pels.keys())
    lengths = np.array([pels[i][2] - pels[i][1] for i in ids], dtype=float)
    gcv = np.array([gc.get(i, np.nan) for i in ids], dtype=float)
    # drop NaN GC from universe for matching
    ok = np.isfinite(gcv)
    ids = [ids[i] for i in range(len(ids)) if ok[i]]
    lengths = lengths[ok]
    gcv = gcv[ok]
    print(f"universe with finite GC: {len(ids)}", flush=True)

    length_bins = quantile_bins(lengths, 4)
    gc_bins = quantile_bins(gcv, 10)
    id_to_lenbin = {ids[i]: int(length_bins[i]) for i in range(len(ids))}
    id_to_gcbin = {ids[i]: int(gc_bins[i]) for i in range(len(ids))}

    keys: dict[str, tuple] = {}
    for eid in ids:
        chrom, s, e = pels[eid]
        mid = (s + e) // 2
        d = nearest_tss_dist(tss.get(chrom, np.array([], dtype=np.int64)), mid)
        keys[eid] = (chrom, id_to_lenbin[eid], id_to_gcbin[eid], tss_dist_bin(d))

    te_exposed = [eid for eid in te_list if eid in keys]
    non_te_pool = [eid for eid in non_te_ids if eid in keys]
    pool_by_key = group_by_key(non_te_pool, keys)
    exposed_keys = [(eid, keys[eid]) for eid in te_exposed]

    print("=== Phase B: 1:1 match lock (no Gnocchi) ===", flush=True)
    matched = match_1to1(exposed_keys, pool_by_key, seed=RNG_SEED)
    n_matched = sum(1 for v in matched.values() if v is not None)
    n_undermatched = sum(1 for v in matched.values() if v is None)
    lock = {
        "experiment": "exp_te_derived_pels_gnocchi",
        "candidate_id": "C-H1",
        "seed": RNG_SEED,
        "n_pels_universe": len(pels),
        "n_finite_gc": len(ids),
        "n_te_exposed": len(te_exposed),
        "n_non_te_pool": len(non_te_pool),
        "n_matched_pairs": n_matched,
        "n_undermatched": n_undermatched,
        "match_covariates": ["chrom", "length_bin_q4", "gc_bin_d10", "tss_dist_bin"],
        "te_classes": sorted(TE_CLASSES),
        "pairs_sample": [
            {"te": k, "non_te": v}
            for k, v in list(matched.items())[:5]
            if v is not None
        ],
    }
    (RES / "matching_lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    print(f"matched={n_matched} undermatched={n_undermatched}", flush=True)

    print("=== Phase C: attach Gnocchi ===", flush=True)
    # Point shared loader at our file via monkeypatch of module constant path
    import gnocchi_constraint_se_vs_typical_analysis as gmod

    gmod.GNOCCHI_FILE = gnocchi_path.resolve()
    gnocchi = load_gnocchi_windows()
    n_win = sum(len(v[0]) for v in gnocchi.values())
    print(f"Gnocchi windows: {n_win}", flush=True)

    pairs_z: list[tuple[float, float]] = []
    n_missing = 0
    for te_id, ctrl_id in matched.items():
        if ctrl_id is None:
            continue
        c1, s1, e1 = pels[te_id]
        c2, s2, e2 = pels[ctrl_id]
        z1 = weighted_mean_z(c1, s1, e1, gnocchi)
        z2 = weighted_mean_z(c2, s2, e2, gnocchi)
        if z1 is None or z2 is None:
            n_missing += 1
            continue
        pairs_z.append((z1, z2))

    diffs = [a - b for a, b in pairs_z]
    mean_delta, ci_lo, ci_hi = bootstrap_mean_ci(diffs, N_BOOT, RNG_SEED)
    abs_delta = abs(mean_delta) if diffs else float("nan")
    obs, p_perm = paired_permutation_p(diffs, N_PERM, RNG_SEED)
    z_te = [a for a, _ in pairs_z]
    z_ctrl = [b for _, b in pairs_z]
    delta_cliff = cliffs_delta(z_te, z_ctrl)
    verdict = verdict_from_abs_delta(abs_delta) if diffs else "BLOCKED_DATA"

    primary = {
        "experiment": "exp_te_derived_pels_gnocchi",
        "candidate_id": "C-H1",
        "n_matched_pairs_lock": n_matched,
        "n_pairs_with_gnocchi": len(pairs_z),
        "n_pairs_dropped_no_coverage": n_missing,
        "mean_z_te": float(np.mean(z_te)) if z_te else None,
        "mean_z_non_te": float(np.mean(z_ctrl)) if z_ctrl else None,
        "median_z_te": float(np.median(z_te)) if z_te else None,
        "median_z_non_te": float(np.median(z_ctrl)) if z_ctrl else None,
        "mean_delta_te_minus_nonte": mean_delta,
        "abs_mean_delta": abs_delta,
        "bootstrap_ci95_mean_delta": [ci_lo, ci_hi],
        "n_bootstrap": N_BOOT,
        "cliffs_delta": delta_cliff,
        "paired_permutation_observed_mean_diff": obs,
        "p_value_permutation": p_perm,
        "n_permutations": N_PERM,
        "support_threshold_abs_delta": SUPPORT_ABS_DELTA,
        "kill_threshold_abs_delta": KILL_ABS_DELTA,
        "verdict": verdict,
        "data_source_gnocchi": (
            "Chen/Francioli/Karczewski 2023 Gnocchi QC 1kb "
            "(gs://gnomad-nc-constraint-v31-paper/download_files/"
            "constraint_z_genome_1kb.qc.download.txt.gz)"
        ),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (RES / "primary_result.json").write_text(json.dumps(primary, indent=2) + "\n")
    print(json.dumps(primary, indent=2))
    print(f"Saved {RES / 'primary_result.json'}", flush=True)


if __name__ == "__main__":
    main()
