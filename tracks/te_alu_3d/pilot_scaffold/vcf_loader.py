"""Lightweight VCF/BED loaders for chr11 pilot — no bulk genome download."""

from __future__ import annotations

import gzip
import re
from pathlib import Path
from typing import Iterable, Iterator

from qc_filters import VariantRecord

CLINVAR_P_LP = {"Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic"}


def _open_text(path: Path):
    if str(path).endswith(".gz") or str(path).endswith(".bgz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open(encoding="utf-8", errors="replace")


def _norm_chrom(chrom: str) -> str:
    return chrom if chrom.startswith("chr") else f"chr{chrom}"


def _parse_info(info: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in info.split(";"):
        if not tok:
            continue
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
        else:
            out[tok] = "1"
    return out


def _clin_sig_ok(clnsig: str, allowed: Iterable[str]) -> bool:
    allowed_set = set(allowed)
    # ClinVar may use Pathogenic/Likely_pathogenic or pipe-separated
    parts = re.split(r"[|,/]", clnsig.replace(" ", "_"))
    for p in parts:
        p = p.strip()
        if p in allowed_set:
            return True
        if p.replace("/", "_") in allowed_set:
            return True
    # also accept substring Pathogenic / Likely_pathogenic
    norm = clnsig.replace(" ", "_")
    return any(a in norm for a in allowed_set if a)


def iter_vcf_variants(
    path: Path,
    chrom_filter: str = "chr11",
    source: str = "clinvar",
) -> Iterator[VariantRecord]:
    """Stream VCF records on one chromosome (uncompressed or .gz)."""
    want = _norm_chrom(chrom_filter)
    with _open_text(path) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 8:
                continue
            chrom = _norm_chrom(parts[0])
            if chrom != want:
                continue
            pos = int(parts[1])
            ref = parts[3]
            alt_field = parts[4]
            info = _parse_info(parts[7])
            filt = parts[6]
            for alt in alt_field.split(","):
                vid = f"{chrom}:{pos}:{ref}:{alt}"
                af: float | None = None
                for key in ("AF", "AF_joint", "AF_popmax", "gnomad_af"):
                    if key in info:
                        try:
                            af = float(info[key].split(",")[0])
                        except ValueError:
                            af = None
                        break
                clnsig = info.get("CLNSIG", "")
                yield VariantRecord(
                    chrom=chrom,
                    pos=pos,
                    ref=ref,
                    alt=alt,
                    variant_id=vid,
                    source=source,
                    clinical_significance=clnsig,
                    af=af,
                    qc_flags=[] if filt in {"PASS", ".", "None"} else [f"FILTER_{filt}"],
                )


def load_clinvar_plp(
    path: Path,
    chrom: str = "chr11",
    allowed_sig: Iterable[str] | None = None,
) -> list[VariantRecord]:
    allowed = list(allowed_sig or CLINVAR_P_LP)
    out: list[VariantRecord] = []
    for v in iter_vcf_variants(path, chrom_filter=chrom, source="clinvar"):
        if _clin_sig_ok(v.clinical_significance, allowed):
            out.append(v)
    return out


def load_gnomad_rare(
    path: Path,
    chrom: str = "chr11",
    max_af: float = 0.001,
    pass_only: bool = True,
) -> list[VariantRecord]:
    out: list[VariantRecord] = []
    for v in iter_vcf_variants(path, chrom_filter=chrom, source="gnomad"):
        if pass_only and any(f.startswith("FILTER_") and f != "FILTER_PASS" for f in v.qc_flags):
            # FILTER_. is ok; FILTER_PASS not used — empty flags means PASS/.
            if v.qc_flags and not all(f in {"FILTER_PASS", "FILTER_."} for f in v.qc_flags):
                continue
        if v.af is not None and v.af <= max_af:
            out.append(v)
        elif v.af is None:
            # keep if no AF annotated (caller may filter later)
            out.append(v)
    return out


def load_variant_tsv(path: Path, source: str = "tsv") -> list[VariantRecord]:
    """Fallback TSV: chrom pos ref alt [af] [clnsig] [variant_id]."""
    out: list[VariantRecord] = []
    with path.open(encoding="utf-8") as fh:
        header = fh.readline()
        cols = [c.strip().lower() for c in header.split("\t")]
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            row = {cols[i]: parts[i] for i in range(min(len(cols), len(parts)))}
            chrom = _norm_chrom(row.get("chrom", row.get("chr", parts[0])))
            pos = int(row.get("pos", parts[1]))
            ref = row.get("ref", parts[2])
            alt = row.get("alt", parts[3])
            af = float(row["af"]) if row.get("af") not in (None, "") else None
            clnsig = row.get("clnsig", row.get("clinical_significance", ""))
            vid = row.get("variant_id", f"{chrom}:{pos}:{ref}:{alt}")
            out.append(
                VariantRecord(
                    chrom=chrom,
                    pos=pos,
                    ref=ref,
                    alt=alt,
                    variant_id=vid,
                    source=source,
                    clinical_significance=clnsig,
                    af=af,
                )
            )
    return out


def slice_vcf_to_chr(
    in_path: Path,
    out_path: Path,
    chrom: str = "chr11",
) -> int:
    """Filter full VCF to one chromosome (streaming). Returns n records written."""
    want = {_norm_chrom(chrom), chrom.replace("chr", "")}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    opener_out = gzip.open if str(out_path).endswith(".gz") else open
    with _open_text(in_path) as fin, opener_out(out_path, "wt", encoding="utf-8") as fout:  # type: ignore
        for line in fin:
            if line.startswith("#"):
                fout.write(line)
                continue
            chrom_field = line.split("\t", 1)[0]
            if chrom_field in want or _norm_chrom(chrom_field) == _norm_chrom(chrom):
                # normalize to chr prefix
                if not chrom_field.startswith("chr"):
                    line = f"chr{line}"
                fout.write(line)
                n += 1
    return n
