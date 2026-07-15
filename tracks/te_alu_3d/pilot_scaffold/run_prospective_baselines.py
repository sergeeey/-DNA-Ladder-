"""Run motif-only and distance-only baselines on a leakage-free universe.

Usage:
  python run_prospective_baselines.py --dry-run
  python run_prospective_baselines.py --universe ../09_outputs/prospective/universe.tsv
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any

from baseline_scorers import score_variant_baselines
from build_prospective_universe import (
    DEFAULT_CFG,
    build_universe,
    ensure_dry_fixtures,
    load_allowed_tsv,
    load_prospective_config,
    write_universe,
    _resolve_data_dir,
    _resolve_out_dir,
)
from holdout_guard import assert_not_scoring_holdout
from leakage_audit import run_audit
from qc_filters import VariantRecord

ROOT = Path(__file__).resolve().parent


def _load_universe_tsv(path: Path) -> list[VariantRecord]:
    assert_not_scoring_holdout(path)
    rows: list[VariantRecord] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            af_s = row.get("af") or ""
            af = float(af_s) if af_s not in ("", None) else None
            rows.append(
                VariantRecord(
                    chrom=row["chrom"],
                    pos=int(row["pos"]),
                    ref=row["ref"],
                    alt=row["alt"],
                    variant_id=row.get("variant_id") or "",
                    source=row.get("source") or "universe",
                    af=af,
                    te_family=row.get("te_family") or "",
                    te_overlap=str(row.get("te_overlap", "0")) in {"1", "true", "True"},
                )
            )
    return rows


def _resolve_peaks(cfg: dict[str, Any], data_dir: Path) -> Path:
    paths = (cfg.get("prospective") or {}).get("paths") or {}
    for name in (
        paths.get("ctcf_bed", "ctcf_HUDEP2_peaks.bed"),
        paths.get("ctcf_bed_fallback", "ctcf_GM12878_peaks.bed"),
    ):
        p = data_dir / name
        if p.exists():
            return p
        alt = ROOT / "data" / name
        if alt.exists():
            return alt
    return data_dir / paths.get("ctcf_bed", "ctcf_HUDEP2_peaks.bed")


def _resolve_fasta(cfg: dict[str, Any], data_dir: Path, dry: bool) -> Path | None:
    paths = (cfg.get("prospective") or {}).get("paths") or {}
    if dry:
        fa = data_dir / "chr11_prospective_fixture.fa"
        return fa if fa.exists() else None
    configured = paths.get("fasta")
    if configured:
        p = Path(configured)
        if not p.is_absolute():
            p = data_dir / configured
        return p if p.exists() else None
    return None


def run_baselines(
    variants: list[VariantRecord],
    *,
    fasta_path: Path | None,
    peaks_path: Path,
) -> list[dict[str, Any]]:
    return [
        score_variant_baselines(v, fasta_path=fasta_path, peaks_path=peaks_path)
        for v in variants
    ]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    motif = [float(r["motif_only"]) for r in rows if r.get("motif_only") is not None]
    dist = [float(r["distance_only"]) for r in rows if r.get("distance_only") is not None]
    return {
        "n_variants": len(rows),
        "n_motif_scored": len(motif),
        "n_distance_scored": len(dist),
        "motif_only_median": statistics.median(motif) if motif else None,
        "distance_only_median": statistics.median(dist) if dist else None,
        "spearman_motif_vs_distance": _spearman(motif_aligned(rows)),
        "role": "G2_preparation_only",
        "primary_scorer": None,
        "claim": None,
        "note": (
            "Baselines are comparators. A future leakage-free primary must beat "
            "both on an independent shortlist before G2 can PASS."
        ),
    }


def motif_aligned(rows: list[dict[str, Any]]) -> list[tuple[float, float]]:
    pairs: list[tuple[float, float]] = []
    for r in rows:
        if r.get("motif_only") is None or r.get("distance_only") is None:
            continue
        pairs.append((float(r["motif_only"]), float(r["distance_only"])))
    return pairs


def _spearman(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]

    def ranks(vals: list[float]) -> list[float]:
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    n = len(pairs)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any], out_dir: Path) -> None:
    tsv = out_dir / "baseline_scores.tsv"
    with tsv.open("w", encoding="utf-8") as fh:
        fh.write(
            "variant_id\tmotif_only\tmotif_only_ok\tmotif_delta_logodds\t"
            "motif_error\tdistance_only\tdist_ctcf\trole\n"
        )
        for r in rows:
            fh.write(
                f"{r['variant_id']}\t{r.get('motif_only')}\t{r.get('motif_only_ok')}\t"
                f"{r.get('motif_delta_logodds')}\t{r.get('motif_error')}\t"
                f"{r.get('distance_only')}\t{r.get('dist_ctcf')}\t{r.get('role')}\n"
            )
    payload = {
        "summary": summary,
        "rows_head": rows[:20],
        "gate": "G2_PREP",
        "verdict": "PREP_COMPLETE",
        "wet_lab_go": False,
    }
    (out_dir / "baseline_comparison.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=DEFAULT_CFG)
    ap.add_argument("--universe", type=Path, default=None)
    ap.add_argument("--input", type=Path, default=None, help="raw allowed TSV (builds universe)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_prospective_config(args.config)
    out_dir = _resolve_out_dir(cfg)
    data_dir = _resolve_data_dir(cfg, dry=args.dry_run)

    if args.dry_run:
        seed = ensure_dry_fixtures(data_dir)
        audit = run_audit(cfg, input_tsv=seed, out_dir=out_dir)
        if audit["verdict"] != "PASS":
            print(json.dumps(audit, indent=2))
            return 1
        variants = load_allowed_tsv(seed, cfg)
        kept, uaudit = build_universe(variants, cfg, data_dir)
        write_universe(
            kept,
            out_dir,
            {
                "input": str(seed),
                "dry_run": True,
                "audit": uaudit,
                "leakage_audit_verdict": audit["verdict"],
            },
        )
        universe_vars = kept
    elif args.universe:
        assert_not_scoring_holdout(args.universe)
        run_audit(cfg, input_tsv=None, out_dir=out_dir)
        universe_vars = _load_universe_tsv(args.universe)
    elif args.input:
        audit = run_audit(cfg, input_tsv=args.input, out_dir=out_dir)
        if audit["verdict"] != "PASS":
            print(json.dumps(audit, indent=2))
            return 1
        variants = load_allowed_tsv(args.input, cfg)
        kept, uaudit = build_universe(variants, cfg, data_dir)
        write_universe(
            kept,
            out_dir,
            {"input": str(args.input), "audit": uaudit, "leakage_audit_verdict": audit["verdict"]},
        )
        universe_vars = kept
    else:
        raise SystemExit("Provide --dry-run, --universe, or --input")

    peaks = _resolve_peaks(cfg, data_dir)
    fasta = _resolve_fasta(cfg, data_dir, dry=args.dry_run)
    rows = run_baselines(universe_vars, fasta_path=fasta, peaks_path=peaks)
    summary = summarize(rows)
    summary["peaks"] = str(peaks)
    summary["fasta"] = str(fasta) if fasta else None
    write_outputs(rows, summary, out_dir)
    print(json.dumps({"out_dir": str(out_dir), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
