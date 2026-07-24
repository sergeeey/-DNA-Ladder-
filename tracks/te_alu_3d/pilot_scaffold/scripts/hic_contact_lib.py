"""Pure-function library for Hi-C contact qualification.

All functions are stateless and take explicit Path / primitive arguments.
No global state, no I/O side effects beyond reading the files passed in.

Pre-registered thresholds (Stage-3, G4a_stage3_architecture_wt_contact_CLAIM_v1.md):
  PASS: obs present, focal_row_nonzero > 0, bg_n >= 20,
        enrich_mean >= 1.5, obs_percentile >= 0.75, OE >= 1.2
  INSUFFICIENT_BG: bg_n < 20
  FAIL: otherwise

sample_verdict maps two resolution scores to a slot verdict.
"""
from __future__ import annotations

import statistics
from pathlib import Path


# ---------------------------------------------------------------------------
# Low-level loaders
# ---------------------------------------------------------------------------


def load_triples(path: Path) -> list[tuple[int, int, float]]:
    """Parse a juicer_tools dump text file into (bin_a, bin_b, value) triples.

    Skips lines that do not have exactly three whitespace-separated tokens or
    whose first two tokens are not integers.  Returns an empty list for a
    missing or empty file.
    """
    if not path.exists() or path.stat().st_size < 5:
        return []
    rows: list[tuple[int, int, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        try:
            rows.append((int(parts[0]), int(parts[1]), float(parts[2])))
        except ValueError:
            continue
    return rows


def bin_of(coord: int, binsize: int) -> int:
    """Return the bin-start coordinate for a 1-based genomic position."""
    # WHY: integer floor division maps any position into its bin's left edge,
    #      matching juicer_tools' own coordinate convention.
    return (coord // binsize) * binsize


# ---------------------------------------------------------------------------
# Contact analysis
# ---------------------------------------------------------------------------


def analyze_contact(
    obs_path: Path,
    oe_path: Path,
    binsize: int,
    e_anchor: tuple[int, int],
    p_anchor: tuple[int, int],
    focal_row_coord: int,
    bg_tol_bins: int = 1,
) -> dict:
    """Compute contact metrics for an E–P anchor pair at a given resolution.

    Args:
        obs_path: Path to juicer_tools dump ``observed`` text file.
        oe_path: Path to juicer_tools dump ``oe`` text file.
        binsize: Resolution in base-pairs (e.g. 10_000 or 25_000).
        e_anchor: (start, end) of the E (CTCF) anchor in hg19 coordinates,
                  half-open BED convention (0-based start, exclusive end).
        p_anchor: (start, end) of the P (TSS window) anchor, same convention.
        focal_row_coord: 1-based coordinate of the primary anchor to check for
                         row coverage (typically the mid-point of E).
        bg_tol_bins: Tolerance (in bins) for same-distance background.

    Returns:
        Dictionary with keys:
          binsize, bg_tol_bins, e_bins, p_bins,
          primary_pair, primary_obs, primary_oe,
          same_distance_bg_n, bg_mean_obs, bg_median_obs,
          enrich_mean, obs_percentile, oe_percentile,
          focal_row_nonzero, n_obs_pixels.
    """
    obs_triples = load_triples(obs_path)
    oe_triples = load_triples(oe_path)

    # WHY: symmetric expansion ensures lookup works regardless of which
    #      triangle juicer emitted; done for both obs and OE to be consistent.
    obs_map: dict[tuple[int, int], float] = {}
    for a, b, v in obs_triples:
        obs_map[(a, b)] = v
        obs_map[(b, a)] = v

    oe_map: dict[tuple[int, int], float] = {}
    for a, b, v in oe_triples:
        oe_map[(a, b)] = v
        oe_map[(b, a)] = v

    # Bins covered by each anchor window
    e_start, e_end = e_anchor
    p_start, p_end = p_anchor
    e_bins = sorted({bin_of(e_start, binsize), bin_of(e_end - 1, binsize)})
    p_bins = sorted({bin_of(p_start, binsize), bin_of(p_end - 1, binsize)})

    # Primary pair: midpoint of each anchor
    e_mid_coord = (e_start + e_end) // 2
    p_mid_coord = (p_start + p_end) // 2
    e_mid = bin_of(e_mid_coord, binsize)
    p_mid = bin_of(p_mid_coord, binsize)
    primary = (e_mid, p_mid)

    primary_obs = obs_map.get(primary)
    primary_oe = oe_map.get(primary)

    # Same-distance background (exclude the focal E–P bins themselves)
    target_dist = abs(p_mid - e_mid)
    tol = binsize * bg_tol_bins
    e_bins_set = set(e_bins)
    p_bins_set = set(p_bins)
    bg_obs: list[float] = []
    bg_oe: list[float] = []
    for a, b, v in obs_triples:
        d = abs(b - a)
        if abs(d - target_dist) <= tol:
            # Exclude the focal E–P bin pair regardless of which anchor is upstream.
            # WHY: E may be downstream of P (e.g. A754 hg19); must check both orientations.
            lo, hi = min(a, b), max(a, b)
            is_focal = (lo in e_bins_set and hi in p_bins_set) or (
                lo in p_bins_set and hi in e_bins_set
            )
            if is_focal:
                continue
            bg_obs.append(v)
            ov = oe_map.get((a, b))
            if ov is not None:
                bg_oe.append(ov)

    bg_n = len(bg_obs)
    bg_mean = statistics.mean(bg_obs) if bg_obs else None
    bg_median = statistics.median(bg_obs) if bg_obs else None

    enrich_mean: float | None = None
    if primary_obs is not None and bg_mean and bg_mean > 0:
        enrich_mean = primary_obs / bg_mean

    def pct_rank(x: float | None, arr: list[float]) -> float | None:
        if x is None or not arr:
            return None
        return sum(1 for t in arr if t <= x) / len(arr)

    obs_pct = pct_rank(primary_obs, bg_obs)
    oe_pct = pct_rank(primary_oe, bg_oe)

    # Focal-row coverage: count each symmetric pixel once.
    focal_bin = bin_of(focal_row_coord, binsize)
    focal_row_nonzero = sum(
        1 for (a, b), v in obs_map.items() if a == focal_bin and v > 0
    )

    return {
        "binsize": binsize,
        "bg_tol_bins": bg_tol_bins,
        "e_bins": e_bins,
        "p_bins": p_bins,
        "primary_pair": list(primary),
        "primary_obs": primary_obs,
        "primary_oe": primary_oe,
        "same_distance_bg_n": bg_n,
        "bg_mean_obs": bg_mean,
        "bg_median_obs": bg_median,
        "enrich_mean": enrich_mean,
        "obs_percentile": obs_pct,
        "oe_percentile": oe_pct,
        "focal_row_nonzero": focal_row_nonzero,
        "n_obs_pixels": len(obs_triples),
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

# Pre-registered thresholds (Stage-3 claim v1)
_ENRICH_THRESHOLD = 1.5
_PCT_THRESHOLD = 0.75
_OE_THRESHOLD = 1.2
_BG_MIN = 20


def score_resolution(m: dict) -> str:
    """Score a single resolution dict from analyze_contact.

    Returns one of: "PASS", "INSUFFICIENT_BG",
    "UNRESOLVED_SAME_BIN", "FAIL".
    """
    primary_pair = m.get("primary_pair")
    if (
        isinstance(primary_pair, list)
        and len(primary_pair) == 2
        and primary_pair[0] == primary_pair[1]
    ):
        # A diagonal self-bin is dominated by local polymer/diagonal signal.
        # It cannot discriminate contact between two distinct anchors.
        return "UNRESOLVED_SAME_BIN"

    bg_n: int = m.get("same_distance_bg_n", 0)
    if bg_n < _BG_MIN:
        # WHY: fail-closed on inadequate background; inconclusive verdict
        #      propagates through sample_verdict.
        return "INSUFFICIENT_BG"

    obs = m.get("primary_obs")
    focal = m.get("focal_row_nonzero", 0)
    enrich = m.get("enrich_mean")
    pct = m.get("obs_percentile")
    oe = m.get("primary_oe")

    if (
        obs is not None
        and focal > 0
        and enrich is not None
        and enrich >= _ENRICH_THRESHOLD
        and pct is not None
        and pct >= _PCT_THRESHOLD
        and oe is not None
        and oe >= _OE_THRESHOLD
    ):
        return "PASS"
    return "FAIL"


def sample_verdict(res10: str, res25: str) -> str:
    """Combine two resolution scores into a slot verdict.

    Pre-registered mapping (Stage-3 claim v1):
      PASS + PASS             → PASS
      either unresolved score → INCONCLUSIVE
      FAIL + FAIL             → UNSUPPORTED
      ≥1 PASS (other ≠ PASS)  → PARTIAL
      otherwise               → INCONCLUSIVE
    """
    scores = (res10, res25)

    if res10 == "PASS" and res25 == "PASS":
        return "PASS"

    if "INSUFFICIENT_BG" in scores or "UNRESOLVED_SAME_BIN" in scores:
        # WHY: inadequate background means we cannot distinguish signal from
        # noise; a diagonal self-bin is likewise non-discriminating.
        return "INCONCLUSIVE"

    if res10 == "FAIL" and res25 == "FAIL":
        return "UNSUPPORTED"

    if "PASS" in scores:
        return "PARTIAL"

    return "INCONCLUSIVE"
