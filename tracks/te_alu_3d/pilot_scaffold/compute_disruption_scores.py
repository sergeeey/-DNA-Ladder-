"""Disruption scores — ARCHCODE primary; CTCF-PWM exploratory fallback.

Does NOT interpret enrichment. LSSIM/PWM never confirmatory.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ctcf_pwm_scorer import SCORER_VERSION, ctcf_pwm_disruption, scorer_fingerprint
from qc_filters import VariantRecord, dry_run_variants, load_config

ROOT = Path(__file__).resolve().parent


def lssim_motif_disruption(ref: str, alt: str, window: str = "") -> float:
    """Legacy stub — kept for dry-run regress; prefer CTCF-PWM."""
    _ = window
    ref_u, alt_u = ref.upper(), alt.upper()
    if ref_u == alt_u:
        return 0.0
    gc_ref = sum(1 for b in ref_u if b in "GC") / max(len(ref_u), 1)
    gc_alt = sum(1 for b in alt_u if b in "GC") / max(len(alt_u), 1)
    base = 0.15 + abs(gc_alt - gc_ref) * 0.5
    if ref_u in "CG" and alt_u in "AT":
        base += 0.1
    return min(1.0, base)


def archcode_score(
    chrom: str,
    pos: int,
    ref: str,
    alt: str,
    cfg: dict[str, Any],
) -> float | None:
    binary = cfg["scoring"]["archcode"].get("binary_path")
    if not binary:
        return None
    cmd = [binary, "--chrom", chrom, "--pos", str(pos), "--ref", ref, "--alt", alt]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return float(proc.stdout.strip().split()[-1])
    except ValueError:
        return None


def _resolve_fasta(cfg: dict[str, Any], data_dir: Path) -> Path:
    p = cfg.get("scoring", {}).get("fasta_window")
    if p:
        path = Path(p)
        return path if path.is_absolute() else (ROOT / path)
    return data_dir / "chr11_hbb_window.fa"


def _resolve_ctcf(cfg: dict[str, Any], data_dir: Path) -> Path:
    from build_matched_controls import resolve_ctcf_bed

    return resolve_ctcf_bed(cfg, data_dir)


def score_variant(
    v: VariantRecord,
    cfg: dict[str, Any],
    *,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    data_dir = data_dir or (ROOT / cfg["paths"]["data_dir"])
    arch = archcode_score(v.chrom, v.pos, v.ref, v.alt, cfg)
    legacy = lssim_motif_disruption(v.ref, v.alt)

    pwm_meta: dict[str, Any] = {}
    fasta = _resolve_fasta(cfg, data_dir)
    ctcf = _resolve_ctcf(cfg, data_dir)
    if fasta.exists():
        pwm_meta = ctcf_pwm_disruption(
            v.chrom, v.pos, v.ref, v.alt, fasta_path=fasta, peaks_path=ctcf
        )
        pwm_score = float(pwm_meta.get("score", 0.0))
    else:
        pwm_score = legacy
        pwm_meta = {"method": "legacy_lssim_stub", "score": pwm_score}

    if arch is not None:
        score = arch
        method = "archcode"
        exploratory_only = False
    else:
        score = pwm_score
        method = pwm_meta.get("method", SCORER_VERSION)
        exploratory_only = True

    return {
        "variant_id": v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}",
        "score": score,
        "method": method,
        "archcode": arch,
        "lssim": legacy,
        "pwm_score": pwm_score,
        "pwm_delta_logodds": pwm_meta.get("delta_logodds"),
        "in_ctcf_peak": pwm_meta.get("in_peak"),
        "scorer_fingerprint": scorer_fingerprint(),
        "exploratory_only": exploratory_only,
        "te_family": v.te_family,
        "track": v.track,
    }


def write_scores(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    split: dict[str, list] = {"confirmatory": [], "exploratory": []}
    for r in rows:
        track = r.get("track") or "exploratory"
        if r.get("exploratory_only"):
            track = "exploratory"
        split.setdefault(track, []).append(r)

    for track, items in split.items():
        sub = path.parent / track / path.name
        sub.parent.mkdir(parents=True, exist_ok=True)
        with sub.open("w", newline="", encoding="utf-8") as fh:
            if not items:
                fh.write("variant_id,score,method\n")
                continue
            w = csv.DictWriter(fh, fieldnames=list(items[0].keys()))
            w.writeheader()
            w.writerows(items)

    with path.open("w", newline="", encoding="utf-8") as fh:
        if not rows:
            fh.write("variant_id,score,method\n")
            return
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    dry = "--dry-run" in sys.argv
    cfg = load_config()
    out_dir = ROOT / cfg["outputs"]["base_dir"]
    if dry:
        variants = dry_run_variants()
        for v in variants:
            v.te_family = "Alu" if v.pos < 10000000 else "SVA"
            v.track = "exploratory"
        rows = [score_variant(v, cfg) for v in variants]
        write_scores(rows, out_dir / "disruption_scores.csv")
        print(
            json.dumps(
                {
                    "scored": len(rows),
                    "archcode_available": bool(cfg["scoring"]["archcode"].get("binary_path")),
                    "scorer_fingerprint": scorer_fingerprint(),
                },
                indent=2,
            )
        )
        return 0
    print("Use --dry-run or run_pilot.py", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
