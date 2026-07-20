#!/usr/bin/env python3
"""C-A2 primary pipeline: match-before-outcomes → switcher Fisher OR → odd/even kill.

Phases (enforced):
  A) Build registry dELS universe + covariates (GC/length/TSS/baseline) — NO switching labels
  B) Define SVA_F vs non-TE; 1:k match; write matched ids
  C) ONLY THEN attach switching-panel activity; switcher; Fisher OR; sub-panels

Writes:
  results/matching_lock.json          (phase B artifact — no outcomes)
  results/primary_result_OR_CI.json
  results/primary_result_OR_CI.md
  results/panel_split_OR.json
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from c_a2_lib import (  # noqa: E402
    K_MATCH,
    RNG_SEED,
    TE_CLASSES,
    fisher_or_woolf,
    is_active_classification,
    is_registry_dels,
    match_1k,
    quantile_bins,
    switcher_flag,
    tss_dist_bin,
)
from t0_probe_screen_matrix import BASELINE, SWITCHING  # noqa: E402
from twobit import TwoBitFile  # noqa: E402

KEEP_CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX"}


def load_registry_dels(path: Path) -> dict[str, tuple[str, int, int]]:
    """id -> (chrom, start, end) for registry dELS."""
    out: dict[str, tuple[str, int, int]] = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 6:
                continue
            chrom, start, end, _d, eid, klass = p[0], int(p[1]), int(p[2]), p[3], p[4], p[5]
            if chrom not in KEEP_CHROMS:
                continue
            if not is_registry_dels(klass):
                continue
            out[eid] = (chrom, start, end)
    return out


def load_tss(path: Path) -> dict[str, np.ndarray]:
    """chrom -> sorted TSS positions (protein-coding genes)."""
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


def load_rmsk_te(path: Path) -> tuple[dict[str, list[tuple[int, int]]], dict[str, list[tuple[int, int]]]]:
    """Return (sva_f_intervals, any_te_intervals) keyed by chrom."""
    sva: dict[str, list[tuple[int, int]]] = defaultdict(list)
    te: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            # UCSC rmsk: bin, swScore, milliDiv, milliDel, milliIns, genoName, genoStart, genoEnd,
            # ... repName, repClass, repFamily ...
            if len(p) < 12:
                continue
            chrom = p[5]
            if chrom not in KEEP_CHROMS:
                continue
            start, end = int(p[6]), int(p[7])
            rep_name, rep_class = p[10], p[11]
            if rep_class in TE_CLASSES:
                te[chrom].append((start, end))
            if rep_name == "SVA_F":
                sva[chrom].append((start, end))
    for d in (sva, te):
        for c in d:
            d[c].sort()
    return sva, te


def annotate_overlaps(
    dels: dict[str, tuple[str, int, int]],
    intervals: dict[str, list[tuple[int, int]]],
) -> set[str]:
    """Return cCRE ids that overlap any interval."""
    by_chrom: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for eid, (chrom, s, e) in dels.items():
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


def load_active_ids(bed_gz: Path) -> set[str]:
    """cCRE ids active under pre-registered rule."""
    active: set[str] = set()
    with gzip.open(bed_gz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 11:
                continue
            eid, klass, complete = p[3], p[9], p[10]
            if is_active_classification(klass, complete):
                active.add(eid)
    return active


def gc_for_dels(dels: dict[str, tuple[str, int, int]], twobit_path: Path) -> dict[str, float]:
    """Compute GC% per cCRE; load each chrom packed DNA once."""
    # group ids by chrom
    by_chrom: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    for eid, (chrom, s, e) in dels.items():
        by_chrom[chrom].append((eid, s, e))

    out: dict[str, float] = {}
    with TwoBitFile(twobit_path) as tb:
        for chrom, rows in by_chrom.items():
            tb._load_meta(chrom)
            dna_size, n_regions, _m, packed_off = tb._seq_meta[chrom]
            byte_len = (dna_size + 3) // 4
            tb.fh.seek(packed_off)
            blob = tb.fh.read(byte_len)
            # build N mask bitset via bytearray
            is_n = bytearray(dna_size)
            for ns, nsz in n_regions:
                is_n[ns : ns + nsz] = b"\x01" * nsz
            decode_gc = (0, 1, 0, 1)  # T=0 C=1 A=0 G=1
            decode_atgc = (1, 1, 1, 1)
            for eid, s, e in rows:
                gc = 0
                atgc = 0
                for pos in range(s, e):
                    if pos >= dna_size or is_n[pos]:
                        continue
                    bi = pos // 4
                    shift = 6 - 2 * (pos % 4)
                    base = (blob[bi] >> shift) & 0x3
                    atgc += decode_atgc[base]
                    gc += decode_gc[base]
                out[eid] = (gc / atgc) if atgc else float("nan")
            print(f"  GC done {chrom} n={len(rows)}", flush=True)
    return out


def contingency_from_labels(
    exposed: list[str],
    matched: dict[str, list[str]],
    switcher: dict[str, bool],
) -> tuple[int, int, int, int, int]:
    """Return a,b,c,d,n_undermatched for Fisher table."""
    a = b = c = d = 0
    undermatched = 0
    ctrl_ids: list[str] = []
    for eid in exposed:
        m = matched.get(eid, [])
        if len(m) < K_MATCH:
            undermatched += 1
        if not m:
            continue
        if switcher.get(eid, False):
            a += 1
        else:
            b += 1
        ctrl_ids.extend(m)
    for cid in ctrl_ids:
        if switcher.get(cid, False):
            c += 1
        else:
            d += 1
    return a, b, c, d, undermatched


def main() -> None:
    t0 = time.time()
    RES.mkdir(parents=True, exist_ok=True)
    reg_path = INP / "GRCh38-cCREs.Registry-V3.bed"
    rmsk_path = INP / "rmsk.txt.gz"
    twobit_path = INP / "hg38.2bit"
    gencode_path = INP / "gencode.v47.basic.annotation.gtf.gz"
    for p in (reg_path, rmsk_path, twobit_path, gencode_path):
        if not p.exists():
            raise SystemExit(f"missing input: {p}")

    print("=== Phase A: universe + covariates (no switching outcomes) ===", flush=True)
    dels = load_registry_dels(reg_path)
    print(f"registry dELS (chr1-22,X): {len(dels)}", flush=True)

    print("loading rmsk…", flush=True)
    sva_iv, te_iv = load_rmsk_te(rmsk_path)
    sva_ids = annotate_overlaps(dels, sva_iv)
    te_ids = annotate_overlaps(dels, te_iv)
    non_te_ids = [eid for eid in dels if eid not in te_ids]
    sva_list = sorted(eid for eid in sva_ids if eid in dels)
    print(f"SVA_F∩dELS={len(sva_list)}  non-TE dELS pool={len(non_te_ids)}", flush=True)

    print("loading TSS…", flush=True)
    tss = load_tss(gencode_path)

    print("computing GC (per chrom)…", flush=True)
    gc = gc_for_dels(dels, twobit_path)

    # baseline biosample active (matching covariate only)
    base_path = INP / f"{BASELINE['accession']}_{BASELINE['biosample']}.bed.gz"
    print(f"baseline active: {base_path.name}", flush=True)
    baseline_active = load_active_ids(base_path)

    # covariate arrays on universe
    ids = list(dels.keys())
    lengths = np.array([dels[i][2] - dels[i][1] for i in ids], dtype=float)
    gcv = np.array([gc.get(i, np.nan) for i in ids], dtype=float)
    # impute nan GC with median
    med_gc = float(np.nanmedian(gcv))
    gcv = np.where(np.isnan(gcv), med_gc, gcv)
    tss_bins = []
    for i in ids:
        chrom, s, e = dels[i]
        mid = (s + e) // 2
        tss_bins.append(tss_dist_bin(nearest_tss_dist(tss.get(chrom, np.array([], dtype=np.int64)), mid)))
    tss_bins_a = np.array(tss_bins, dtype=int)
    len_bins = quantile_bins(lengths, 4)
    gc_bins = quantile_bins(gcv, 10)
    base_bin = np.array([1 if i in baseline_active else 0 for i in ids], dtype=int)

    cov: dict[str, tuple] = {}
    for idx, eid in enumerate(ids):
        chrom = dels[eid][0]
        cov[eid] = (
            chrom,
            int(len_bins[idx]),
            int(gc_bins[idx]),
            int(tss_bins_a[idx]),
            int(base_bin[idx]),
        )

    print("=== Phase B: 1:k match (LOCK — no outcomes yet) ===", flush=True)
    pool_by_key: dict[tuple, list[str]] = defaultdict(list)
    for eid in non_te_ids:
        pool_by_key[cov[eid]].append(eid)
    exposed_keys = [(eid, cov[eid]) for eid in sva_list]
    matched = match_1k(exposed_keys, pool_by_key, k=K_MATCH, seed=RNG_SEED)
    n_full = sum(1 for v in matched.values() if len(v) >= K_MATCH)
    n_under = sum(1 for v in matched.values() if 0 < len(v) < K_MATCH)
    n_none = sum(1 for v in matched.values() if len(v) == 0)

    matching_lock = {
        "phase": "B_MATCH_LOCK",
        "seed": RNG_SEED,
        "k": K_MATCH,
        "n_registry_dels": len(dels),
        "n_sva_f": len(sva_list),
        "n_non_te_pool": len(non_te_ids),
        "n_matched_full_k": n_full,
        "n_undermatched": n_under,
        "n_unmatched": n_none,
        "covariates": ["chrom", "length_quartile", "gc_decile", "tss_dist_bin", "baseline_SK-N-SH_active"],
        "baseline_biosample": BASELINE,
        "switching_panel_not_used": True,
        "matched_preview_first_5": {k: matched[k] for k in sva_list[:5]},
    }
    (RES / "matching_lock.json").write_text(json.dumps(matching_lock, indent=2) + "\n")
    # full match map (ids only — still no outcomes)
    (RES / "matched_ids.json").write_text(
        json.dumps({"sva_to_controls": matched, "outcomes_attached": False}, indent=2) + "\n"
    )
    print(f"match lock written: full_k={n_full} under={n_under} none={n_none}", flush=True)

    print("=== Phase C: attach switching outcomes → OR ===", flush=True)
    panel_active: dict[str, set[str]] = {}
    for row in SWITCHING:
        p = INP / f"{row['accession']}_{row['biosample']}.bed.gz"
        print(f"  load {row['biosample']}…", flush=True)
        panel_active[row["biosample"]] = load_active_ids(p)

    panel_order = [r["biosample"] for r in SWITCHING]
    n_panel = len(panel_order)

    def activity_vec(eid: str, biosamples: list[str]) -> list[bool]:
        return [eid in panel_active[b] for b in biosamples]

    switcher_all: dict[str, bool] = {}
    # only need labels for SVA_F + matched controls
    need: set[str] = set(sva_list)
    for v in matched.values():
        need.update(v)
    for eid in need:
        switcher_all[eid] = switcher_flag(activity_vec(eid, panel_order))

    a, b, c, d, und = contingency_from_labels(sva_list, matched, switcher_all)
    or_, lo, hi, p = fisher_or_woolf(a, b, c, d)
    print(f"primary OR={or_:.4f} CI=({lo:.4f},{hi:.4f}) table=[{a},{b},{c},{d}]", flush=True)

    # odd / even sub-panels
    odd = [panel_order[i] for i in range(n_panel) if i % 2 == 0]
    even = [panel_order[i] for i in range(n_panel) if i % 2 == 1]
    panel_split = {}
    kill_hits = 0
    for name, bios in (("odd", odd), ("even", even)):
        if len(bios) < 4:
            panel_split[name] = {"status": "SKIP_N_LT_4", "N": len(bios)}
            continue
        sw = {eid: switcher_flag(activity_vec(eid, bios)) for eid in need}
        aa, bb, cc, dd, _ = contingency_from_labels(sva_list, matched, sw)
        oor, olo, ohi, op = fisher_or_woolf(aa, bb, cc, dd)
        kill = oor < 1.1
        kill_hits += int(kill)
        panel_split[name] = {
            "biosamples": bios,
            "N": len(bios),
            "table": {"a": aa, "b": bb, "c": cc, "d": dd},
            "OR": oor,
            "CI95": [olo, ohi],
            "p_fisher": op,
            "kill_OR_lt_1_1": kill,
        }
        print(f"  {name} OR={oor:.4f} kill={kill}", flush=True)

    # verdict
    if kill_hits >= 2:
        verdict = "REJECT"
        gate = "FAIL_KILL"
    elif or_ >= 1.4 and kill_hits == 0:
        verdict = "SUPPORT"
        gate = "PASS_MCID"
    elif or_ < 1.1:
        verdict = "REJECT"
        gate = "FAIL_PRIMARY_OR"
    else:
        verdict = "INCONCLUSIVE"
        gate = "MID_ZONE"

    primary = {
        "candidate_id": "C-A2",
        "experiment": "exp_sva_f_ccre_state_switching",
        "not_chia_pet": True,
        "N_switching": n_panel,
        "panel_order": panel_order,
        "baseline_held_out": BASELINE,
        "k": K_MATCH,
        "seed": RNG_SEED,
        "table": {"a_sva_switch": a, "b_sva_nonswitch": b, "c_ctrl_switch": c, "d_ctrl_nonswitch": d},
        "n_undermatched_indices": und,
        "OR": or_,
        "CI95": [lo, hi],
        "p_fisher": p,
        "switcher_rate_sva": a / (a + b) if (a + b) else None,
        "switcher_rate_ctrl": c / (c + d) if (c + d) else None,
        "MCID": 1.4,
        "kill_rule": "OR<1.1 in ≥2 independent panels",
        "panel_split_kill_hits": kill_hits,
        "verdict": verdict,
        "decision_gate": gate,
        "matching_lock_path": "results/matching_lock.json",
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (RES / "primary_result_OR_CI.json").write_text(json.dumps(primary, indent=2) + "\n")
    (RES / "panel_split_OR.json").write_text(json.dumps(panel_split, indent=2) + "\n")

    md = [
        "# C-A2 primary result — SVA_F dELS switching OR",
        "",
        f"**Verdict:** `{verdict}` (`{gate}`)",
        "",
        f"- Fisher OR = **{or_:.4f}** (Woolf 95% CI {lo:.4f}–{hi:.4f}; p={p:.4g})",
        f"- Table [a,b,c,d] = [{a}, {b}, {c}, {d}] (SVA switch / SVA non / ctrl switch / ctrl non)",
        f"- Switcher rate SVA_F = {primary['switcher_rate_sva']:.4f}; matched non-TE = {primary['switcher_rate_ctrl']:.4f}",
        f"- N switching biosamples = {n_panel}; k={K_MATCH}; undermatched indices = {und}",
        f"- Panel-split kill hits (OR<1.1) = {kill_hits} / 2",
        "",
        "## Panel split",
        "",
    ]
    for name, block in panel_split.items():
        if "OR" in block:
            md.append(
                f"- **{name}** ({', '.join(block['biosamples'])}): OR={block['OR']:.4f} "
                f"CI={block['CI95'][0]:.4f}–{block['CI95'][1]:.4f} kill={block['kill_OR_lt_1_1']}"
            )
        else:
            md.append(f"- **{name}**: {block}")
    md += [
        "",
        "## Leakage control",
        "",
        "Matching locked in `matching_lock.json` with `switching_panel_not_used: true` before outcomes.",
        "",
        "Not ChIA-PET. True C-A2 SVA_F dELS switching desk.",
        "",
    ]
    (RES / "primary_result_OR_CI.md").write_text("\n".join(md) + "\n")
    print(json.dumps({"verdict": verdict, "OR": or_, "kill_hits": kill_hits}, indent=2))


if __name__ == "__main__":
    main()
