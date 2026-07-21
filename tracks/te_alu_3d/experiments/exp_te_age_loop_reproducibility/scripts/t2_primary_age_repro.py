#!/usr/bin/env python3
"""C-D1 primary: TE milliDiv tertile vs Pol II↔Hi-C loop-call reproducibility.

Prereg: claim.md — Δ_repro = repro(old) − repro(young) ≥ 0.10 SUPPORT; <0.05 REJECT.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c_d1_lib import (  # noqa: E402
    CANON,
    MCID_KILL,
    MCID_SUPPORT,
    RMSK_CHROM,
    RMSK_CLASS,
    RMSK_END,
    RMSK_FAMILY,
    RMSK_MILLIDIV,
    RMSK_NAME,
    RMSK_START,
    SEED,
    TE_CLASSES,
    WIN_BP,
    assign_tertile,
    build_units,
    chrom_block_bootstrap_delta,
    fisher_or_woolf,
    load_bedpe_anchors,
    min_milli_overlap,
    open_text,
    overlaps_any,
    tertile_cuts,
    verdict_delta,
)

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"


def load_te_intervals(rmsk_path: Path, *, alu_only: bool = False):
    """chrom -> sorted list of (start, end, milliDiv, repName, repClass, repFamily)."""
    by: dict[str, list[tuple[int, int, int, str, str, str]]] = defaultdict(list)
    with open_text(rmsk_path) as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= RMSK_FAMILY:
                continue
            chrom = cols[RMSK_CHROM]
            if chrom not in CANON:
                continue
            rep_class = cols[RMSK_CLASS]
            if rep_class not in TE_CLASSES:
                continue
            fam = cols[RMSK_FAMILY]
            if alu_only and "Alu" not in fam and "Alu" not in cols[RMSK_NAME]:
                continue
            try:
                start = int(cols[RMSK_START])
                end = int(cols[RMSK_END])
                milli = int(cols[RMSK_MILLIDIV])
            except ValueError:
                continue
            if end <= start:
                continue
            by[chrom].append((start, end, milli, cols[RMSK_NAME], rep_class, fam))
    for chrom in by:
        by[chrom].sort(key=lambda x: x[0])
    return by


def annotate_window(
    chrom: str,
    start: int,
    end: int,
    te_by: dict[str, list[tuple[int, int, int, str, str, str]]],
) -> tuple[int | None, str | None, str | None]:
    """Return (min_milliDiv, class_of_min, family_of_min) or (None, None, None)."""
    return min_milli_overlap(start, end, te_by.get(chrom, []))


def index_starts(windows: list[tuple[str, int, int]]) -> dict[str, list[tuple[int, int]]]:
    by: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for c, s, e in windows:
        by[c].append((s, e))
    for c in by:
        by[c].sort()
    return by


def run_analysis(
    pol2_path: Path,
    hic_path: Path,
    rmsk_path: Path,
    *,
    alu_only: bool = False,
    label: str = "primary",
) -> dict:
    print(f"[{label}] loading bedpe…", flush=True)
    pol2 = build_units(load_bedpe_anchors(pol2_path))
    hic = build_units(load_bedpe_anchors(hic_path))
    print(f"[{label}] pol2={len(pol2)} hic={len(hic)}", flush=True)
    pol2_ix = index_starts(pol2)
    hic_ix = index_starts(hic)

    # Union of windows keyed by (chrom, start, end)
    union: dict[tuple[str, int, int], str] = {}
    for w in pol2:
        union[w] = "pol2_only"
    for w in hic:
        if w in union:
            union[w] = "shared"
        else:
            union[w] = "hic_only"
    refined: list[tuple[str, int, int, str]] = []
    for (c, s, e), _tag in union.items():
        in_pol2 = overlaps_any(s, e, pol2_ix.get(c, []))
        in_hic = overlaps_any(s, e, hic_ix.get(c, []))
        if in_pol2 and in_hic:
            status = "shared"
        elif in_pol2:
            status = "pol2_only"
        elif in_hic:
            status = "hic_only"
        else:
            continue
        refined.append((c, s, e, status))
    print(f"[{label}] union windows={len(refined)}; loading rmsk…", flush=True)

    te_by = load_te_intervals(rmsk_path, alu_only=alu_only)
    print(f"[{label}] rmsk chroms={len(te_by)}; annotating…", flush=True)

    rows = []
    for i, (c, s, e, status) in enumerate(refined):
        if i and i % 100000 == 0:
            print(f"[{label}] annotated {i}/{len(refined)}", flush=True)
        milli, cls, fam = annotate_window(c, s, e, te_by)
        if milli is None:
            rows.append(
                {
                    "chrom": c,
                    "start": s,
                    "end": e,
                    "status": status,
                    "te": False,
                    "repro": 1 if status == "shared" else 0,
                }
            )
            continue
        rows.append(
            {
                "chrom": c,
                "start": s,
                "end": e,
                "status": status,
                "te": True,
                "milliDiv": milli,
                "repClass": cls,
                "repFamily": fam,
                "repro": 1 if status == "shared" else 0,
            }
        )

    te_rows = [r for r in rows if r["te"]]
    non_te = [r for r in rows if not r["te"]]
    if len(te_rows) < 30:
        return {
            "label": label,
            "verdict": "BLOCKED_DATA",
            "reason": f"too few TE-hit windows: {len(te_rows)}",
            "n_te": len(te_rows),
        }

    millis = [float(r["milliDiv"]) for r in te_rows]
    q33, q66 = tertile_cuts(millis)
    for r in te_rows:
        r["tertile"] = assign_tertile(float(r["milliDiv"]), q33, q66)

    def bin_stats(t: int) -> dict:
        sub = [r for r in te_rows if r["tertile"] == t]
        n = len(sub)
        n_shared = sum(1 for r in sub if r["repro"] == 1)
        n_excl = n - n_shared
        return {
            "n": n,
            "n_shared": n_shared,
            "n_exclusive": n_excl,
            "repro_rate": (n_shared / n) if n else float("nan"),
            "milliDiv_min": min((r["milliDiv"] for r in sub), default=None),
            "milliDiv_max": max((r["milliDiv"] for r in sub), default=None),
            "milliDiv_mean": (sum(r["milliDiv"] for r in sub) / n) if n else None,
        }

    young = bin_stats(0)
    mid = bin_stats(1)
    old = bin_stats(2)
    delta = old["repro_rate"] - young["repro_rate"]

    young_flags = [(r["chrom"], r["repro"]) for r in te_rows if r["tertile"] == 0]
    old_flags = [(r["chrom"], r["repro"]) for r in te_rows if r["tertile"] == 2]
    boot_lo, boot_hi = chrom_block_bootstrap_delta(young_flags, old_flags, seed=SEED)

    # OR(exclusive | young) vs old — report-only companion
    a = young["n_exclusive"]  # young exclusive
    b = young["n_shared"]
    c = old["n_exclusive"]
    d = old["n_shared"]
    or_, or_lo, or_hi, or_p = fisher_or_woolf(a, b, c, d)

    # class breakdown exploratory
    class_delta = {}
    for cls in sorted(TE_CLASSES):
        sub = [r for r in te_rows if r.get("repClass") == cls]
        if len(sub) < 60:
            class_delta[cls] = {"status": "SKIP", "n": len(sub)}
            continue
        m = [float(r["milliDiv"]) for r in sub]
        qq = tertile_cuts(m)
        for r in sub:
            r["_t"] = assign_tertile(float(r["milliDiv"]), *qq)
        y = [r for r in sub if r["_t"] == 0]
        o = [r for r in sub if r["_t"] == 2]
        if not y or not o:
            class_delta[cls] = {"status": "SKIP", "n": len(sub)}
            continue
        ry = sum(r["repro"] for r in y) / len(y)
        ro = sum(r["repro"] for r in o) / len(o)
        class_delta[cls] = {
            "status": "OK",
            "n": len(sub),
            "repro_young": ry,
            "repro_old": ro,
            "delta": ro - ry,
            "verdict": verdict_delta(ro - ry),
        }

    verdict = verdict_delta(delta)
    non_te_rate = (
        sum(r["repro"] for r in non_te) / len(non_te) if non_te else float("nan")
    )

    return {
        "label": label,
        "alu_only": alu_only,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "n_pol2_windows": len(pol2),
        "n_hic_windows": len(hic),
        "n_union_windows": len(rows),
        "n_te_hit": len(te_rows),
        "n_non_te": len(non_te),
        "non_te_repro_rate": non_te_rate,
        "tertile_cuts_milliDiv": {"q33": q33, "q66": q66},
        "young": young,
        "mid": mid,
        "old": old,
        "delta_repro_old_minus_young": delta,
        "bootstrap_95ci_delta": {"lo": boot_lo, "hi": boot_hi, "n_boot": 500, "seed": SEED},
        "companion_OR_exclusive_young_vs_old": {
            "OR": or_,
            "CI95": [or_lo, or_hi],
            "p": or_p,
            "table": {"young_excl": a, "young_shared": b, "old_excl": c, "old_shared": d},
        },
        "class_stratified_exploratory": class_delta,
        "mcid": {"SUPPORT": MCID_SUPPORT, "KILL": MCID_KILL},
        "verdict": verdict,
        "unit": f"{WIN_BP}bp midpoint windows; merge+pad≥1kb",
        "accessions": {
            "pol2": "ENCFF511QFN",
            "hic": "ENCFF693XIL",
            "rmsk": "UCSC hg38 rmsk.txt.gz",
        },
    }


def write_md(result: dict, path: Path) -> None:
    lines = [
        f"# C-D1 primary result — {result.get('label')}",
        "",
        f"**Verdict:** `{result.get('verdict')}`",
        "",
        f"Δ_repro (old − young) = **{result.get('delta_repro_old_minus_young'):.4f}**"
        if isinstance(result.get("delta_repro_old_minus_young"), float)
        else f"Δ_repro = {result.get('delta_repro_old_minus_young')}",
        "",
        f"- Young repro: {result.get('young', {}).get('repro_rate')}",
        f"- Mid repro: {result.get('mid', {}).get('repro_rate')}",
        f"- Old repro: {result.get('old', {}).get('repro_rate')}",
        f"- TE-hit n: {result.get('n_te_hit')}",
        f"- Tertile cuts milliDiv: {result.get('tertile_cuts_milliDiv')}",
        f"- Bootstrap 95% CI Δ: {result.get('bootstrap_95ci_delta')}",
        f"- Companion OR(excl|young): {result.get('companion_OR_exclusive_young_vs_old')}",
        "",
        "SUPPORT if Δ≥0.10; REJECT if Δ<0.05; else INCONCLUSIVE.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    pol2 = DATA / "ENCFF511QFN.bedpe.gz"
    hic = DATA / "ENCFF693XIL.bedpe.gz"
    rmsk = DATA / "rmsk.txt.gz"
    for p, lab in ((pol2, "Pol II"), (hic, "Hi-C"), (rmsk, "rmsk")):
        if not p.exists():
            print(f"Missing {lab}: {p}", file=sys.stderr)
            return 2

    RESULTS.mkdir(parents=True, exist_ok=True)
    primary = run_analysis(pol2, hic, rmsk, alu_only=False, label="primary_SINE_LINE_LTR")
    (RESULTS / "primary_delta_repro.json").write_text(
        json.dumps(primary, indent=2) + "\n", encoding="utf-8"
    )
    write_md(primary, RESULTS / "primary_delta_repro.md")
    print(json.dumps({"primary_verdict": primary["verdict"], "delta": primary.get("delta_repro_old_minus_young")}, indent=2))

    alu = run_analysis(pol2, hic, rmsk, alu_only=True, label="sensitivity_Alu_only")
    (RESULTS / "sensitivity_alu_only.json").write_text(
        json.dumps(alu, indent=2) + "\n", encoding="utf-8"
    )
    write_md(alu, RESULTS / "sensitivity_alu_only.md")
    print(json.dumps({"alu_verdict": alu["verdict"], "delta": alu.get("delta_repro_old_minus_young")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
