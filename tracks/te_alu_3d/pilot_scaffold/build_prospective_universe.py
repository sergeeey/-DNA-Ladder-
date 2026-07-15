"""Build a leakage-free prospective variant universe (no ClinVar ranking, no holdout).

Usage:
  python build_prospective_universe.py --input data/prospective_fixtures/universe_seed.tsv
  python build_prospective_universe.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from holdout_guard import assert_not_scoring_holdout, holdout_is_sealed
from qc_filters import VariantRecord, _load_te_index, _te_overlap_indexed

ROOT = Path(__file__).resolve().parent
DEFAULT_CFG = ROOT / "prospective_config.yaml"


def load_prospective_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_CFG
    with cfg_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _resolve_data_dir(cfg: dict[str, Any], *, dry: bool) -> Path:
    paths = (cfg.get("prospective") or {}).get("paths") or {}
    base = ROOT / paths.get("data_dir", "data")
    return base / "prospective_fixtures" if dry else base


def _resolve_out_dir(cfg: dict[str, Any]) -> Path:
    paths = (cfg.get("prospective") or {}).get("paths") or {}
    out = ROOT / paths.get("out_dir", "../09_outputs/prospective")
    out.mkdir(parents=True, exist_ok=True)
    return out.resolve()


FORBIDDEN_HEADER_HINTS = {
    "clinical_significance",
    "clnsig",
    "clinvar",
    "consequence",
    "vep",
    "vep_severity",
    "effect_strength",
    "pearl_status",
    "pearl",
    "pathogenicity",
    "label",
    "pathogenic",
    "benign",
}


def validate_input_path(path: Path, cfg: dict[str, Any]) -> None:
    assert_not_scoring_holdout(path)
    tokens = set((cfg.get("prospective") or {}).get("forbid_path_tokens") or ["holdout"])
    if any(tok in path.parts for tok in tokens):
        raise RuntimeError(f"Forbidden path token in input: {path}")


def validate_headers(headers: list[str], cfg: dict[str, Any]) -> list[str]:
    forbid = {
        f.lower()
        for f in ((cfg.get("prospective") or {}).get("forbid_header_fields") or list(FORBIDDEN_HEADER_HINTS))
    }
    hits: list[str] = []
    for h in headers:
        hl = h.strip().lower()
        if hl in forbid or any(tok in hl for tok in forbid if len(tok) > 3):
            # avoid matching bare "af" etc.; token-in-name for clinvar/vep/pearl
            if hl in forbid or any(tok in hl for tok in ("clinvar", "clnsig", "consequence", "vep", "pearl", "pathogen")):
                hits.append(h)
    return hits


def _in_excluded_window(chrom: str, pos: int, cfg: dict[str, Any]) -> str | None:
    for w in (cfg.get("prospective") or {}).get("exclude_windows") or []:
        if chrom == w.get("chrom") and int(w["start"]) <= pos < int(w["end"]):
            return str(w.get("reason") or "excluded_window")
    return None


def load_allowed_tsv(path: Path, cfg: dict[str, Any]) -> list[VariantRecord]:
    validate_input_path(path, cfg)
    with path.open(encoding="utf-8") as fh:
        header = fh.readline()
        if not header.strip():
            raise ValueError(f"empty header: {path}")
        cols = [c.strip() for c in header.split("\t")]
        bad = validate_headers(cols, cfg)
        if bad:
            raise RuntimeError(
                "G1 leakage: forbidden header fields in input TSV: " + ", ".join(bad)
            )
        cols_l = [c.lower() for c in cols]
        rows: list[VariantRecord] = []
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            row = {cols_l[i]: parts[i] for i in range(min(len(cols_l), len(parts)))}
            chrom = row.get("chrom") or row.get("chr") or parts[0]
            if not chrom.startswith("chr"):
                chrom = f"chr{chrom}"
            pos = int(row.get("pos") or parts[1])
            ref = row.get("ref") or parts[2]
            alt = row.get("alt") or parts[3]
            af_s = row.get("af", "")
            af = float(af_s) if af_s not in ("", None) else None
            vid = row.get("variant_id") or f"{chrom}:{pos}:{ref}:{alt}"
            # Hard reject if a forbidden label sneaks into a free-text column
            for k, v in row.items():
                if k in FORBIDDEN_HEADER_HINTS and v not in ("", None, ".", "NA"):
                    raise RuntimeError(f"G1 leakage: non-empty forbidden field {k}={v!r}")
            rows.append(
                VariantRecord(
                    chrom=chrom,
                    pos=pos,
                    ref=ref,
                    alt=alt,
                    variant_id=vid,
                    source="prospective_tsv",
                    clinical_significance="",
                    af=af,
                )
            )
    return rows


def write_fixture_seed(path: Path) -> None:
    """Synthetic non-HBB seed (around 10.8 Mb) for dry-run mechanics."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "chrom\tpos\tref\talt\taf\tvariant_id\n"
        "chr11\t10800060\tG\tA\t0.0002\tchr11:10800060:G:A\n"
        "chr11\t10800090\tT\tC\t0.0005\tchr11:10800090:T:C\n"
        "chr11\t10800150\tA\tG\t0.0001\tchr11:10800150:A:G\n"
        "chr11\t5227000\tA\tG\t0.0001\tchr11:5227000:A:G\n"  # HBB — must be excluded
        "chr11\t17400050\tC\tT\t0.0003\tchr11:17400050:C:T\n"
        ,
        encoding="utf-8",
    )


def ensure_dry_fixtures(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    te = data_dir / "repeatmasker_chr11_alu_sva.bed"
    if not te.exists():
        te.write_text(
            "chr11\t10800050\t10800200\tSVA_E\t0\t+\tSVA\n"
            "chr11\t17399900\t17400100\tAluSx1\t0\t+\tSINE/Alu\n"
            "chr11\t5226990\t5227050\tAluJb\t0\t+\tSINE/Alu\n",
            encoding="utf-8",
        )
    ctcf = data_dir / "ctcf_HUDEP2_peaks.bed"
    if not ctcf.exists():
        ctcf.write_text(
            "chr11\t10800000\t10800080\tCTCF_peak\n"
            "chr11\t17399950\t17400020\tCTCF_peak\n",
            encoding="utf-8",
        )
    (data_dir / "encode_blacklist_hg38.bed").write_text(
        "chr11\t9999999\t10000050\tblacklist_test\n", encoding="utf-8"
    )
    (data_dir / "genomicSuperDups_chr11.bed").write_text(
        "chr11\t20000000\t20000100\tsegdup_far\n", encoding="utf-8"
    )
    (data_dir / "gencode_v46_protein_coding_TSS_chr11.bed").write_text(
        "chr11\t10801000\t10801010\tGENE_X\t-\n", encoding="utf-8"
    )
    # tiny fasta covering 10800000-10800300 for motif baseline dry-run
    fa = data_dir / "chr11_prospective_fixture.fa"
    if not fa.exists():
        # synthetic sequence; length 300
        seq = ("ACGT" * 75)
        fa.write_text(f">chr11:10800000-10800300\n{seq}\n", encoding="utf-8")
    seed = data_dir / "universe_seed.tsv"
    write_fixture_seed(seed)
    return seed


def annotate_te(
    variants: list[VariantRecord],
    te_bed: Path,
    families: set[str],
) -> list[VariantRecord]:
    index = _load_te_index(te_bed, families)
    out: list[VariantRecord] = []
    for v in variants:
        overlap, fam = _te_overlap_indexed(v.chrom, v.pos, index)
        v.te_overlap = bool(overlap)
        v.te_family = fam or ""
        out.append(v)
    return out


def build_universe(
    variants: list[VariantRecord],
    cfg: dict[str, Any],
    data_dir: Path,
) -> tuple[list[VariantRecord], dict[str, Any]]:
    prosp = cfg.get("prospective") or {}
    rarity = prosp.get("rarity") or {}
    max_af = float(rarity.get("max_af", 0.001))
    require_af = bool(rarity.get("require_af", False))
    te_cfg = prosp.get("te_focus") or {}
    families = set(te_cfg.get("families") or ["Alu", "SVA"])
    require_te = bool(te_cfg.get("require_te_overlap", True))
    paths = prosp.get("paths") or {}

    te_bed = data_dir / paths.get("te_bed", "repeatmasker_chr11_alu_sva.bed")
    if not te_bed.exists():
        # fall back to parent data dir
        alt = ROOT / "data" / paths.get("te_bed", "repeatmasker_chr11_alu_sva.bed")
        if alt.exists():
            te_bed = alt

    variants = annotate_te(variants, te_bed, families)

    kept: list[VariantRecord] = []
    drop: dict[str, int] = {
        "excluded_window": 0,
        "af_fail": 0,
        "te_fail": 0,
        "missing_af": 0,
    }
    for v in variants:
        reason = _in_excluded_window(v.chrom, v.pos, cfg)
        if reason:
            drop["excluded_window"] += 1
            continue
        if v.af is None:
            if require_af:
                drop["missing_af"] += 1
                continue
        elif v.af > max_af:
            drop["af_fail"] += 1
            continue
        if require_te and not v.te_overlap:
            drop["te_fail"] += 1
            continue
        kept.append(v)

    audit = {
        "n_input": len(variants),
        "n_kept": len(kept),
        "drop": drop,
        "te_bed": str(te_bed),
        "holdout_sealed": holdout_is_sealed(),
        "status": "FRAMEWORK_ONLY",
        "claim": None,
    }
    return kept, audit


def write_universe(
    variants: list[VariantRecord],
    out_dir: Path,
    provenance: dict[str, Any],
) -> Path:
    out_tsv = out_dir / "universe.tsv"
    with out_tsv.open("w", encoding="utf-8") as fh:
        fh.write("variant_id\tchrom\tpos\tref\talt\taf\tte_family\tte_overlap\tsource\n")
        for v in variants:
            vid = v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}"
            af = "" if v.af is None else str(v.af)
            fh.write(
                f"{vid}\t{v.chrom}\t{v.pos}\t{v.ref}\t{v.alt}\t{af}\t"
                f"{v.te_family}\t{int(v.te_overlap)}\t{v.source}\n"
            )
    (out_dir / "universe_provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )
    return out_tsv


def main() -> int:
    ap = argparse.ArgumentParser(description="Build leakage-free prospective universe")
    ap.add_argument("--config", type=Path, default=DEFAULT_CFG)
    ap.add_argument("--input", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_prospective_config(args.config)
    out_dir = _resolve_out_dir(cfg)
    data_dir = _resolve_data_dir(cfg, dry=args.dry_run)

    if args.dry_run:
        inp = ensure_dry_fixtures(data_dir)
    else:
        if args.input is None:
            raise SystemExit("--input required unless --dry-run")
        inp = args.input

    variants = load_allowed_tsv(inp, cfg)
    kept, audit = build_universe(variants, cfg, data_dir)
    provenance = {
        "input": str(inp.resolve()),
        "config": str(args.config.resolve()),
        "dry_run": bool(args.dry_run),
        "audit": audit,
        "forbidden_windows": (cfg.get("prospective") or {}).get("exclude_windows"),
        "note": "No ranking, no claim, no holdout scoring",
    }
    out_tsv = write_universe(kept, out_dir, provenance)
    print(json.dumps({"universe": str(out_tsv), "n": len(kept), "audit": audit}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
