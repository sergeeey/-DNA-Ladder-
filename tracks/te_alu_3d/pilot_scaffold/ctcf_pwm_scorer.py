"""Exploratory CTCF disruption scorer (ARCHCODE stand-in).

Uses local fasta + CTCF peaks + JASPAR-like CTCF PWM Δ.
NEVER confirmatory — see score_freeze.yaml.
"""

from __future__ import annotations

import hashlib
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

# JASPAR MA0139.1-like CTCF core (simplified 19bp log-odds, A/C/G/T)
# Higher = better CTCF match. Source: approximate consensus from MA0139.1.
_CTCF_PWM: list[dict[str, float]] = [
    {"A": 0.1, "C": 0.4, "G": 0.4, "T": 0.1},
    {"A": 0.05, "C": 0.7, "G": 0.15, "T": 0.1},
    {"A": 0.05, "C": 0.8, "G": 0.1, "T": 0.05},
    {"A": 0.7, "C": 0.1, "G": 0.1, "T": 0.1},
    {"A": 0.1, "C": 0.1, "G": 0.7, "T": 0.1},
    {"A": 0.05, "C": 0.05, "G": 0.85, "T": 0.05},
    {"A": 0.05, "C": 0.05, "G": 0.05, "T": 0.85},
    {"A": 0.1, "C": 0.1, "G": 0.7, "T": 0.1},
    {"A": 0.05, "C": 0.8, "G": 0.1, "T": 0.05},
    {"A": 0.1, "C": 0.7, "G": 0.1, "T": 0.1},
    {"A": 0.1, "C": 0.1, "G": 0.1, "T": 0.7},
    {"A": 0.7, "C": 0.1, "G": 0.1, "T": 0.1},
    {"A": 0.1, "C": 0.7, "G": 0.1, "T": 0.1},
    {"A": 0.1, "C": 0.1, "G": 0.7, "T": 0.1},
    {"A": 0.05, "C": 0.85, "G": 0.05, "T": 0.05},
    {"A": 0.1, "C": 0.1, "G": 0.1, "T": 0.7},
    {"A": 0.7, "C": 0.1, "G": 0.1, "T": 0.1},
    {"A": 0.1, "C": 0.7, "G": 0.1, "T": 0.1},
    {"A": 0.1, "C": 0.4, "G": 0.4, "T": 0.1},
]

PWM_LEN = len(_CTCF_PWM)
SCORER_VERSION = "ctcf_pwm_delta_v1.1"



def scorer_fingerprint() -> str:
    blob = SCORER_VERSION + "|" + str(_CTCF_PWM)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _log_odds(seq: str) -> float:
    s = 0.0
    for i, base in enumerate(seq.upper()):
        if i >= PWM_LEN:
            break
        p = _CTCF_PWM[i].get(base, 0.01)
        s += math.log2(max(p, 1e-6) / 0.25)
    return s


def _revcomp(seq: str) -> str:
    table = str.maketrans("ACGTN", "TGCAN")
    return seq.upper().translate(table)[::-1]


@lru_cache(maxsize=4)
def _load_fasta_window(path_str: str) -> tuple[str, int, int, str]:
    """Return (chrom, start0, end0, sequence)."""
    path = Path(path_str)
    text = path.read_text(encoding="utf-8")
    lines = text.strip().splitlines()
    header = lines[0][1:] if lines[0].startswith(">") else "chr11:0-0"
    seq = "".join(lines[1:]).upper().replace("N", "A")
    # header like chr11:5200000-5300000
    chrom, rest = header.split(":", 1)
    start_s, end_s = rest.replace("..", "-").split("-")
    return chrom, int(start_s), int(end_s), seq


def _load_peaks(path: Path) -> list[tuple[int, int]]:
    peaks: list[tuple[int, int]] = []
    if not path.exists():
        return peaks
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            p = line.split("\t")
            if len(p) < 3:
                continue
            if not p[0].endswith("11") and p[0] != "chr11":
                continue
            peaks.append((int(p[1]), int(p[2])))
    return peaks


def _best_motif_score(window: str) -> float:
    if len(window) < PWM_LEN:
        return float("-inf")
    best = float("-inf")
    for i in range(0, len(window) - PWM_LEN + 1):
        sub = window[i : i + PWM_LEN]
        best = max(best, _log_odds(sub), _log_odds(_revcomp(sub)))
    return best


def _apply_variant(seq: str, rel_pos: int, ref: str, alt: str) -> str | None:
    ref_u, alt_u = ref.upper(), alt.upper()
    if rel_pos < 0 or rel_pos >= len(seq):
        return None
    if seq[rel_pos : rel_pos + len(ref_u)] != ref_u:
        # indel / allele mismatch — still try single-base replace if lengths match
        if len(ref_u) == 1 and len(alt_u) == 1:
            return seq[:rel_pos] + alt_u + seq[rel_pos + 1 :]
        return None
    return seq[:rel_pos] + alt_u + seq[rel_pos + len(ref_u) :]


def ctcf_pwm_disruption(
    chrom: str,
    pos: int,
    ref: str,
    alt: str,
    *,
    fasta_path: Path,
    peaks_path: Path,
    flank: int = 25,
) -> dict[str, Any]:
    """Δ motif score (ref − alt) at motif placements overlapping the variant.

    Higher disruption = more loss of CTCF motif match in [0, 1].
    """
    meta: dict[str, Any] = {
        "method": SCORER_VERSION,
        "fingerprint": scorer_fingerprint(),
        "in_peak": False,
        "dist_peak": None,
        "delta_logodds": 0.0,
        "score": 0.0,
    }
    if not fasta_path.exists():
        meta["error"] = "missing_fasta"
        return meta

    _fa_chrom, fa_start, fa_end, seq = _load_fasta_window(str(fasta_path))
    if pos < fa_start or pos > fa_end:
        meta["error"] = "pos_outside_fasta_window"
        return meta

    # Ensembl region start is 1-based inclusive; VCF POS is 1-based
    rel = pos - fa_start
    if rel < 0 or rel >= len(seq):
        meta["error"] = "rel_oob"
        return meta

    peaks = _load_peaks(peaks_path)
    dist = min((min(abs(pos - a), abs(pos - b), abs(pos - (a + b) // 2)) for a, b in peaks), default=10**9)
    in_peak = any(a <= pos < b for a, b in peaks)
    meta["in_peak"] = in_peak
    meta["dist_peak"] = int(dist) if dist < 10**9 else None

    alt_seq = _apply_variant(seq, rel, ref, alt)
    allele_mismatch = alt_seq is None
    if allele_mismatch:
        alt_seq = seq[:rel] + (alt.upper()[:1] or "N") + seq[rel + 1 :]
        meta["allele_mismatch"] = True

    # Evaluate every PWM placement that covers the variant base
    best_delta = 0.0
    for offset in range(PWM_LEN):
        start = rel - offset
        if start < 0 or start + PWM_LEN > len(seq):
            continue
        ref_motif = seq[start : start + PWM_LEN]
        alt_motif = alt_seq[start : start + PWM_LEN]
        for motif_r, motif_a in (
            (ref_motif, alt_motif),
            (_revcomp(ref_motif), _revcomp(alt_motif)),
        ):
            delta = _log_odds(motif_r) - _log_odds(motif_a)
            if abs(delta) > abs(best_delta):
                best_delta = delta

    # Prefer disruption direction (loss of motif)
    delta = best_delta
    meta["delta_logodds"] = delta

    # Motif-centric score: map positive Δ to [0,1]; ignore peak boost for ranking core
    # (peak proximity kept as mild multiplier only — benchmark must pass on Δ)
    if delta >= 0:
        disruption = 1.0 - math.exp(-0.5 * delta)
    else:
        # gain of motif → low disruption
        disruption = 0.5 * math.exp(0.5 * delta)

    if in_peak:
        disruption = min(1.0, disruption * 1.05 + 0.02)
    elif meta["dist_peak"] is not None and meta["dist_peak"] > 5000:
        disruption *= 0.85

    meta["score"] = float(max(0.0, min(1.0, disruption)))
    return meta
