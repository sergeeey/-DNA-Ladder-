"""Matched controls — gate 5 (redesign v2).

Estimand T: technical match only (no distance-to-CTCF).
Estimand C: T + CTCF-distance bins.
Control hierarchy A (non-TE primary); B (same TE family) diagnostic.
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from qc_filters import VariantRecord, dry_run_variants, load_config, write_dry_run_fixtures

ROOT = Path(__file__).resolve().parent

EstimandId = Literal["T", "C"]


@dataclass
class AnnotatedVariant:
    variant: VariantRecord
    gc: float
    mappability: float
    dist_ctcf: int
    dist_tss: int
    map_decile: int
    gc_decile: int
    ctcf_bin: int
    tss_bin: int
    te_family_norm: str = ""
    te_subfamily: str = ""


def _vid(v: VariantRecord) -> str:
    return v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}"


def _gc_content(ref: str, alt: str) -> float:
    seq = (ref + alt).upper()
    if not seq:
        return 0.5
    return sum(1 for b in seq if b in "GC") / len(seq)


def _dist_to_nearest(chrom: str, pos: int, bed_path: Path) -> int:
    if not bed_path.exists():
        return 10**9
    best = 10**9
    with bed_path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip().split("\t")
            c = p[0] if p[0].startswith("chr") else f"chr{p[0]}"
            if c != chrom:
                continue
            start, end = int(p[1]), int(p[2])
            mid = (start + end) // 2
            best = min(best, abs(pos - mid))
    return best


def _decile(value: float, n: int = 10) -> int:
    v = max(0.0, min(1.0, value))
    return min(n - 1, int(v * n))


def _log_dist_bin(dist: int) -> int:
    if dist >= 10**8:
        return 9
    return min(9, int(math.log10(max(dist, 1))))


def _norm_te_family(label: str) -> str:
    u = (label or "").upper()
    if "SVA" in u:
        return "SVA"
    if "ALU" in u:
        return "Alu"
    return label or ""


def _te_subfamily(label: str) -> str:
    """RepeatMasker repName-like token (AluSx1, SVA_E, ...)."""
    if not label:
        return ""
    # preferred: 'AluSx1|SINE/Alu'
    if "|" in label:
        return label.split("|", 1)[0].strip()
    tok = label.split("/")[-1].strip()
    return tok


def annotate(
    v: VariantRecord,
    data_dir: Path,
    ctcf_bed: Path,
    tss_bed: Path,
    default_map: float = 0.95,
) -> AnnotatedVariant:
    gc = _gc_content(v.ref, v.alt)
    d_ctcf = _dist_to_nearest(v.chrom, v.pos, ctcf_bed)
    d_tss = _dist_to_nearest(v.chrom, v.pos, tss_bed)
    return AnnotatedVariant(
        variant=v,
        gc=gc,
        mappability=default_map,
        dist_ctcf=d_ctcf,
        dist_tss=d_tss,
        map_decile=_decile(default_map),
        gc_decile=_decile(gc),
        ctcf_bin=_log_dist_bin(d_ctcf),
        tss_bin=_log_dist_bin(d_tss),
        te_family_norm=_norm_te_family(v.te_family),
        te_subfamily=_te_subfamily(v.te_family),
    )


def _match_key(a: AnnotatedVariant, length_exact: bool, estimand: EstimandId) -> tuple:
    v = a.variant
    length = v.length if length_exact else 1
    base = (v.chrom, length, a.map_decile, a.gc_decile, a.tss_bin)
    if estimand == "C":
        return base + (a.ctcf_bin,)
    return base


def build_control_pool(
    pool_variants: list[VariantRecord],
    data_dir: Path,
    *,
    require_non_te: bool = True,
    ctcf_bed: Path | None = None,
    tss_bed: Path | None = None,
) -> list[AnnotatedVariant]:
    ctcf = ctcf_bed or (data_dir / "ctcf_GM12878_peaks.bed")
    tss = tss_bed or (data_dir / "gencode_v46_protein_coding_TSS_chr11.bed")
    # Prefer HUDEP-2 if present and requested via filename already passed
    out: list[AnnotatedVariant] = []
    for v in pool_variants:
        if require_non_te and v.te_overlap:
            continue
        if not require_non_te and not v.te_overlap:
            continue
        out.append(annotate(v, data_dir, ctcf, tss))
    return out


def resolve_ctcf_bed(cfg: dict[str, Any], data_dir: Path) -> Path:
    """KC0-aware CTCF track selection."""
    ctx = cfg.get("three_d_context", {})
    preferred = ctx.get("preferred_cell_line", "GM12878")
    hud = data_dir / "ctcf_HUDEP2_peaks.bed"
    gm = data_dir / "ctcf_GM12878_peaks.bed"
    if preferred in {"HUDEP-2", "HUDEP2", "erythroid"} and hud.exists():
        return hud
    # Auto-upgrade HBB locus prior to HUDEP-2 when file present
    priors = (cfg.get("scoring") or {}).get("archcode", {}).get("locus_priors") or []
    if "HBB" in priors and hud.exists() and ctx.get("auto_huddep2_for_hbb", True):
        return hud
    if gm.exists():
        return gm
    if hud.exists():
        return hud
    return gm


def match_controls_for_estimand(
    test: AnnotatedVariant,
    pool: list[AnnotatedVariant],
    cfg: dict[str, Any],
    rng: random.Random,
    estimand: EstimandId,
) -> tuple[list[AnnotatedVariant], str]:
    """Return chosen AnnotatedVariant controls + match tier."""
    n = cfg["qc_gates"]["gate_5_matched_controls"]["n_per_variant"]
    length_exact = cfg["qc_gates"]["gate_5_matched_controls"]["calipers"]["length_exact"]
    tid = _vid(test.variant)
    key = _match_key(test, length_exact, estimand)

    tier = "strict"
    candidates = [
        p
        for p in pool
        if _vid(p.variant) != tid and _match_key(p, length_exact, estimand) == key
    ]

    if len(candidates) < n:
        tier = "relaxed_gc"
        candidates = [
            p
            for p in pool
            if _vid(p.variant) != tid
            and p.variant.chrom == test.variant.chrom
            and p.variant.length == test.variant.length
            and p.map_decile == test.map_decile
            and p.tss_bin == test.tss_bin
            and abs(p.gc - test.gc) <= 0.05
            and (estimand == "T" or p.ctcf_bin == test.ctcf_bin)
        ]

    if len(candidates) < n:
        tier = "relaxed_map"
        candidates = [
            p
            for p in pool
            if _vid(p.variant) != tid
            and p.variant.chrom == test.variant.chrom
            and p.variant.length == test.variant.length
            and p.map_decile == test.map_decile
            and (estimand == "T" or p.ctcf_bin == test.ctcf_bin)
        ]

    if len(candidates) < n and estimand == "C":
        # last resort for C: drop CTCF to fill n but flag tier
        tier = "relaxed_drop_ctcf"
        candidates = [
            p
            for p in pool
            if _vid(p.variant) != tid
            and p.variant.chrom == test.variant.chrom
            and p.variant.length == test.variant.length
            and p.map_decile == test.map_decile
        ]

    rng.shuffle(candidates)
    return candidates[:n], tier


def match_controls_same_family(
    test: AnnotatedVariant,
    te_pool: list[AnnotatedVariant],
    cfg: dict[str, Any],
    rng: random.Random,
    estimand: EstimandId,
) -> tuple[list[AnnotatedVariant], str]:
    """Control B — diagnostic: same TE family, non-identical site."""
    fam = test.te_family_norm
    subset = [p for p in te_pool if p.te_family_norm == fam]
    chosen, tier = match_controls_for_estimand(test, subset, cfg, rng, estimand)
    return chosen, f"B_{tier}"


def match_controls_same_subfamily(
    test: AnnotatedVariant,
    te_pool: list[AnnotatedVariant],
    cfg: dict[str, Any],
    rng: random.Random,
    estimand: EstimandId,
) -> tuple[list[AnnotatedVariant], str]:
    """Control C — diagnostic: same subfamily (repName proxy)."""
    sub = test.te_subfamily
    if not sub:
        return [], "C_no_subfamily"
    subset = [p for p in te_pool if p.te_subfamily == sub]
    chosen, tier = match_controls_for_estimand(test, subset, cfg, rng, estimand)
    return chosen, f"C_{tier}"


def match_controls(
    test: AnnotatedVariant,
    pool: list[AnnotatedVariant],
    cfg: dict[str, Any],
    rng: random.Random,
    estimand: EstimandId = "C",
) -> tuple[list[str], str]:
    """Backward-compatible wrapper returning ids."""
    chosen, tier = match_controls_for_estimand(test, pool, cfg, rng, estimand)
    return [_vid(c.variant) for c in chosen], tier


def standardized_mean_diff(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return float("nan")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a) / max(len(a) - 1, 1)
    vb = sum((x - mb) ** 2 for x in b) / max(len(b) - 1, 1)
    pooled = math.sqrt((va + vb) / 2) if (va + vb) > 0 else 1.0
    return abs(ma - mb) / pooled


def write_manifest(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text(
            "estimand,test_variant_id,control_ids,match_tier,n_controls,control_level\n",
            encoding="utf-8",
        )
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def balance_for_pairs(
    tests: list[AnnotatedVariant],
    pairs: list[tuple[AnnotatedVariant, list[AnnotatedVariant]]],
) -> dict[str, Any]:
    def col(ann_list: list[AnnotatedVariant], attr: str) -> list[float]:
        return [float(getattr(a, attr)) for a in ann_list]

    all_ctrl = [c for _, cs in pairs for c in cs]
    return {
        "n_test": len(tests),
        "n_controls_used": len(all_ctrl),
        "smd_gc": standardized_mean_diff(col(tests, "gc"), col(all_ctrl, "gc")) if all_ctrl else None,
        "smd_mappability": standardized_mean_diff(
            col(tests, "mappability"), col(all_ctrl, "mappability")
        )
        if all_ctrl
        else None,
        "smd_dist_ctcf": standardized_mean_diff(
            col(tests, "dist_ctcf"), col(all_ctrl, "dist_ctcf")
        )
        if all_ctrl
        else None,
        "smd_dist_tss": standardized_mean_diff(
            col(tests, "dist_tss"), col(all_ctrl, "dist_tss")
        )
        if all_ctrl
        else None,
    }


def main() -> int:
    dry = "--dry-run" in sys.argv
    cfg = load_config()
    rng = random.Random(cfg["pilot"]["random_seed"])
    data_dir = ROOT / cfg["paths"]["data_dir"]
    out_dir = ROOT / cfg["outputs"]["base_dir"]

    if not dry:
        print("Use --dry-run or run_pilot.py", file=sys.stderr)
        return 1

    dry_dir = data_dir / "dry_run"
    write_dry_run_fixtures(dry_dir)
    (dry_dir / "ctcf_GM12878_peaks.bed").write_text(
        "chr11\t5226900\t5226950\tCTCF_peak\n",
        encoding="utf-8",
    )
    (dry_dir / "gencode_v46_protein_coding_TSS_chr11.bed").write_text(
        "chr11\t5226000\t5226010\tHBB\t-\n",
        encoding="utf-8",
    )
    ctcf = dry_dir / "ctcf_GM12878_peaks.bed"
    tss = dry_dir / "gencode_v46_protein_coding_TSS_chr11.bed"
    tests = [
        annotate(v, dry_dir, ctcf, tss)
        for v in dry_run_variants()
        if v.pos in {5227000, 17400000}
    ]
    for t in tests:
        t.variant.te_overlap = True
        t.te_family_norm = "Alu"
    pool_raw = dry_run_variants() + [
        VariantRecord("chr11", 5227200, "A", "G", source="gnomad", af=0.001),
        VariantRecord("chr11", 5227300, "G", "C", source="gnomad", af=0.002),
    ]
    pool = build_control_pool(pool_raw, dry_dir)

    summary: dict[str, Any] = {}
    for est in ("T", "C"):
        rows: list[dict[str, Any]] = []
        for t in tests:
            chosen, tier = match_controls_for_estimand(t, pool, cfg, rng, est)  # type: ignore[arg-type]
            rows.append(
                {
                    "estimand": est,
                    "test_variant_id": _vid(t.variant),
                    "control_ids": ";".join(_vid(c.variant) for c in chosen),
                    "match_tier": tier,
                    "n_controls": len(chosen),
                    "control_level": "A",
                }
            )
        write_manifest(rows, out_dir / f"control_manifest_{est}.csv")
        summary[est] = len(rows)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
