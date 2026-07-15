"""QC filters for chr11 pilot — gates 1–4 + TE family filter.

Kill-first: every excluded variant is logged with gate ID and reason.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent


@dataclass
class VariantRecord:
    chrom: str
    pos: int
    ref: str
    alt: str
    variant_id: str = ""
    source: str = ""  # clinvar | gnomad
    clinical_significance: str = ""
    af: float | None = None
    te_family: str = ""
    te_overlap: bool = False
    qc_flags: list[str] = field(default_factory=list)
    qc_pass: bool = True
    track: str = ""  # confirmatory | exploratory

    @property
    def length(self) -> int:
        if len(self.ref) == 1 and len(self.alt) == 1:
            return 1
        return max(len(self.ref), len(self.alt))

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant_id": self.variant_id or f"{self.chrom}:{self.pos}:{self.ref}:{self.alt}",
            "chrom": self.chrom,
            "pos": self.pos,
            "ref": self.ref,
            "alt": self.alt,
            "source": self.source,
            "clinical_significance": self.clinical_significance,
            "af": self.af,
            "te_family": self.te_family,
            "te_overlap": self.te_overlap,
            "qc_flags": self.qc_flags,
            "qc_pass": self.qc_pass,
            "track": self.track,
        }


def load_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or ROOT / "config.yaml"
    with cfg_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_bed_intervals(path: Path) -> list[tuple[str, int, int]]:
    intervals: list[tuple[str, int, int]] = []
    if not path.exists():
        return intervals
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip().split("\t")
            if len(parts) < 3:
                continue
            chrom = parts[0] if parts[0].startswith("chr") else f"chr{parts[0]}"
            intervals.append((chrom, int(parts[1]), int(parts[2])))
    return intervals


def _index_intervals(
    intervals: list[tuple[str, int, int]],
) -> dict[str, list[tuple[int, int]]]:
    by_chrom: dict[str, list[tuple[int, int]]] = {}
    for c, start, end in intervals:
        by_chrom.setdefault(c, []).append((start, end))
    for c in by_chrom:
        by_chrom[c].sort()
    return by_chrom


def _overlaps_indexed(chrom: str, pos: int, index: dict[str, list[tuple[int, int]]]) -> bool:
    import bisect

    ivals = index.get(chrom)
    if not ivals:
        return False
    # find rightmost start <= pos
    starts = [s for s, _ in ivals]
    i = bisect.bisect_right(starts, pos) - 1
    # check a small window of candidates (intervals may nest)
    for j in range(max(0, i - 5), min(len(ivals), i + 2)):
        start, end = ivals[j]
        if start <= pos < end:
            return True
    # fallback scan near pos for nested intervals
    for start, end in ivals:
        if start > pos:
            break
        if start <= pos < end:
            return True
    return False


def _load_te_index(
    te_bed: Path, families: set[str]
) -> dict[str, list[tuple[int, int, str]]]:
    """chrom -> sorted (start, end, label) for Alu/SVA."""
    by_chrom: dict[str, list[tuple[int, int, str]]] = {}
    if not te_bed.exists():
        return by_chrom
    with te_bed.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip().split("\t")
            if len(parts) < 3:
                continue
            c = parts[0] if parts[0].startswith("chr") else f"chr{parts[0]}"
            start, end = int(parts[1]), int(parts[2])
            name = parts[3] if len(parts) > 3 else ""
            fam = parts[6] if len(parts) > 6 else name
            label = f"{name}|{fam}" if name else (fam or "")
            if families and not any(f.lower() in label.lower() for f in families):
                if not any(f.lower() in name.lower() for f in families):
                    continue
            by_chrom.setdefault(c, []).append((start, end, label))
    for c in by_chrom:
        by_chrom[c].sort()
    return by_chrom


def _te_overlap_indexed(
    chrom: str, pos: int, te_index: dict[str, list[tuple[int, int, str]]]
) -> tuple[bool, str]:
    import bisect

    ivals = te_index.get(chrom)
    if not ivals:
        return False, ""
    starts = [s for s, _, _ in ivals]
    i = bisect.bisect_right(starts, pos) - 1
    for j in range(max(0, i - 3), min(len(ivals), i + 2)):
        start, end, label = ivals[j]
        if start <= pos < end:
            return True, label
    for start, end, label in ivals:
        if start > pos:
            break
        if start <= pos < end:
            return True, label
    return False, ""


def _overlaps(chrom: str, pos: int, intervals: list[tuple[str, int, int]]) -> bool:
    return _overlaps_indexed(chrom, pos, _index_intervals(intervals))


def _te_overlap(chrom: str, pos: int, te_bed: Path, families: set[str]) -> tuple[bool, str]:
    return _te_overlap_indexed(chrom, pos, _load_te_index(te_bed, families))


def _mappability_at(path: Path, chrom: str, pos: int) -> float | None:
    try:
        import pyBigWig  # type: ignore
    except ImportError:
        return None
    if not path.exists():
        return None
    bw = pyBigWig.open(str(path))
    try:
        chrom_name = chrom if chrom in bw.chroms() else chrom.replace("chr", "")
        vals = bw.values(chrom_name, pos - 1, pos)
        if vals and vals[0] is not None:
            return float(vals[0])
    finally:
        bw.close()
    return None


def _discordance_flag(
    variant_id: str, discordance_tsv: Path, p_threshold: float
) -> bool:
    if not discordance_tsv.exists():
        return False
    with discordance_tsv.open(encoding="utf-8") as fh:
        header = fh.readline()
        for line in fh:
            parts = line.rstrip().split("\t")
            if len(parts) < 2:
                continue
            if parts[0] == variant_id:
                try:
                    pval = float(parts[1])
                except ValueError:
                    return parts[-1].lower() in {"true", "1", "yes"}
                return pval < p_threshold
    return False


def apply_qc(
    variants: list[VariantRecord],
    cfg: dict[str, Any],
    data_dir: Path,
    role: str = "test",
) -> tuple[list[VariantRecord], dict[str, Any]]:
    """Apply gates 1–4 + TE Alu/SVA filter. Returns passed variants + dropout audit."""
    qc = cfg["qc_gates"]
    te_families = set(cfg["te_focus"]["families"])

    blacklist = _index_intervals(_load_bed_intervals(data_dir / "encode_blacklist_hg38.bed"))
    segdup = _index_intervals(_load_bed_intervals(data_dir / "genomicSuperDups_chr11.bed"))
    te_bed = data_dir / "repeatmasker_chr11_alu_sva.bed"
    if not te_bed.exists():
        te_bed = data_dir / "repeatmasker_chr11.bed"
    te_index = _load_te_index(te_bed, te_families)
    map_path = data_dir / "wgEncodeCrgMapabilityAlign100mer.bigWig"
    disc_path = data_dir / "gnomad_af_discordance_chr11.tsv"
    min_map = qc["gate_2_mappability"]["min_score"]
    p_disc = qc["gate_4_gnomad_discordance"]["exome_genome_p_threshold"]

    audit: dict[str, int] = {
        "input": len(variants),
        "gate_1_blacklist": 0,
        "gate_2_mappability": 0,
        "gate_3_segdup": 0,
        "gate_4_discordance": 0,
        "te_not_alu_sva": 0,
        "passed": 0,
    }

    passed: list[VariantRecord] = []
    for v in variants:
        v.qc_flags = []
        v.qc_pass = True

        if qc["gate_1_blacklist"]["enabled"] and _overlaps_indexed(v.chrom, v.pos, blacklist):
            v.qc_flags.append("G1_BLACKLIST")
            v.qc_pass = False
            audit["gate_1_blacklist"] += 1

        if v.qc_pass and qc["gate_3_segmental_duplications"]["enabled"]:
            if _overlaps_indexed(v.chrom, v.pos, segdup):
                v.qc_flags.append("G3_SEGDUP")
                v.qc_pass = False
                audit["gate_3_segdup"] += 1

        if v.qc_pass and qc["gate_2_mappability"]["enabled"]:
            score = _mappability_at(map_path, v.chrom, v.pos)
            if score is not None and score < min_map:
                v.qc_flags.append(f"G2_MAPLT{min_map}")
                v.qc_pass = False
                audit["gate_2_mappability"] += 1

        if v.qc_pass and qc["gate_4_gnomad_discordance"]["enabled"]:
            vid = v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}"
            if _discordance_flag(vid, disc_path, p_disc):
                v.qc_flags.append("G4_AF_DISCORDANT")
                v.qc_pass = False
                audit["gate_4_discordance"] += 1

        overlap, fam = _te_overlap_indexed(v.chrom, v.pos, te_index)
        v.te_overlap = overlap
        v.te_family = fam
        if role == "test" and not overlap:
            v.qc_flags.append("TE_NOT_ALU_SVA")
            audit["te_not_alu_sva"] += 1
            v.qc_pass = False
        elif role == "pool" and overlap:
            v.qc_flags.append("TE_IN_CONTROL_POOL")
            v.qc_pass = False

        if v.qc_pass:
            audit["passed"] += 1
            passed.append(v)

    return passed, audit


def assign_track(variants: list[VariantRecord], cfg: dict[str, Any]) -> None:
    """Gate 7: split confirmatory vs exploratory (KC3 ascertainment)."""
    max_af = cfg["variant_sets"]["test_gnomad_rare"]["max_af"]
    for v in variants:
        if v.source == "gnomad" and v.af is not None and v.af <= max_af:
            v.track = "confirmatory"
        elif v.source == "clinvar":
            v.track = "exploratory"  # until dual-track confirmed
        else:
            v.track = "exploratory"


def dry_run_variants() -> list[VariantRecord]:
    """Synthetic chr11 set for pipeline mechanics without downloads."""
    return [
        VariantRecord("chr11", 5227000, "A", "G", source="clinvar", clinical_significance="Pathogenic"),
        VariantRecord("chr11", 5227100, "C", "T", source="clinvar", clinical_significance="Likely_pathogenic"),
        VariantRecord("chr11", 10800000, "G", "A", source="gnomad", af=0.0002),
        VariantRecord("chr11", 10800100, "T", "C", source="gnomad", af=0.0008),
        VariantRecord("chr11", 17400000, "A", "T", source="clinvar", clinical_significance="Pathogenic"),
    ]


def write_dry_run_fixtures(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "repeatmasker_chr11_alu_sva.bed").write_text(
        "chr11\t5226990\t5227050\tAluJb\t0\t+\tSINE/Alu\n"
        "chr11\t10800050\t10800200\tSVA_E\t0\t+\tSVA\n"
        "chr11\t17399900\t17400100\tAluSx1\t0\t+\tSINE/Alu\n",
        encoding="utf-8",
    )
    (data_dir / "encode_blacklist_hg38.bed").write_text(
        "chr11\t9999999\t10000050\tblacklist_test\n", encoding="utf-8"
    )
    (data_dir / "genomicSuperDups_chr11.bed").write_text(
        "chr11\t10800080\t10800120\tsegdup_test\n", encoding="utf-8"
    )


def main() -> int:
    dry = "--dry-run" in sys.argv
    cfg = load_config()
    data_dir = ROOT / cfg["paths"]["data_dir"]
    if dry:
        dry_dir = data_dir / "dry_run"
        write_dry_run_fixtures(dry_dir)
        variants = dry_run_variants()
        passed, audit = apply_qc(variants, cfg, dry_dir, role="test")
        assign_track(passed, cfg)
        out_dir = ROOT / cfg["outputs"]["base_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        report = {"dry_run": True, "audit": audit, "passed": [v.to_dict() for v in passed]}
        (out_dir / "qc_dropout_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
        return 0

    print("Use --dry-run or load real VCFs per inputs_manifest.md", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
