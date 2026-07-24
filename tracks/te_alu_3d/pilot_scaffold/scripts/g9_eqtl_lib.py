"""G9 helpers: panel geography, AF matching, Fisher exact, eQTL hit rule.

Pure functions + thin HTTP wrappers. No analysis side effects.
"""

from __future__ import annotations

import json
import math
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

HOLDOUT_EXCLUDE = [
    (5_200_000, 5_300_000, "HBB_development"),
    (64_000_000, 68_000_000, "holdout_HO_A_B_C_geography"),
]

AF_MIN = 0.05
AF_MAX = 0.50
PANEL_CAP = 200
CTCF_CTRL_PAD_BP = 250
EQTL_P_THRESHOLD = 5e-8
EQTL_NLOG10P_THRESHOLD = -math.log10(EQTL_P_THRESHOLD)
PRIMARY_DATASET = "QTD000356"
REPLIC_DATASET = "QTD000373"
EQTL_API = "https://www.ebi.ac.uk/eqtl/api/v2/datasets"
SEED = 20260722
SEED_G9B = 20260723
SEED_G9C = "20260723c"
AF_MIN_G9B = 0.01
G9C_CHROMS = ("chr1", "chr2", "chr6", "chr11")


def excluded_pos(pos: int, chrom: str = "chr11") -> bool:
    if chrom not in ("chr11", "11"):
        return False
    return any(a <= pos < b for a, b, _ in HOLDOUT_EXCLUDE)


def in_half_open(pos: int, start: int, end: int) -> bool:
    """BED half-open with 1-based variant pos: start < pos <= end."""
    return start < pos <= end


def load_bed_intervals(
    path: Path | str, chroms: set[str] | None = None
) -> list[tuple[str, int, int, str]]:
    p = Path(path)
    rows: list[tuple[str, int, int, str]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        chrom = parts[0] if parts[0].startswith("chr") else f"chr{parts[0]}"
        if chroms is not None and chrom not in chroms:
            continue
        name = parts[3] if len(parts) > 3 else "."
        rows.append((chrom, int(parts[1]), int(parts[2]), name))
    return rows


def interval_contains(
    intervals: list[tuple[str, int, int, str]] | list[tuple[int, int, str]],
    pos: int,
    chrom: str | None = None,
) -> tuple[str, int, int, str] | tuple[int, int, str] | None:
    for row in intervals:
        if len(row) == 4:
            ch, s, e, name = row
            if chrom is not None and ch != chrom:
                continue
            if in_half_open(pos, s, e):
                return ch, s, e, name
        else:
            s, e, name = row
            if in_half_open(pos, s, e):
                return s, e, name
    return None


def in_expanded_peaks(
    peaks: list[tuple[str, int, int, str]] | list[tuple[int, int, str]],
    pos: int,
    pad: int,
    chrom: str | None = None,
) -> bool:
    for row in peaks:
        if len(row) == 4:
            ch, s, e, _ = row
            if chrom is not None and ch != chrom:
                continue
            if (s - pad) < pos <= (e + pad):
                return True
        else:
            s, e, _ = row
            if (s - pad) < pos <= (e + pad):
                return True
    return False


def af_decile(af: float, af_min: float = AF_MIN, af_max: float = AF_MAX) -> int:
    """Deciles over [af_min, af_max]; 0..9."""
    if af < af_min:
        return -1
    if af > af_max:
        return 10
    span = af_max - af_min
    if span <= 0:
        return 0
    d = int((af - af_min) / span * 10)
    return min(9, max(0, d))


def variant_id(chrom: str, pos: int, ref: str, alt: str) -> str:
    return f"{chrom}:{pos}:{ref}:{alt}"


def eqtl_variant_key(pos: int, ref: str, alt: str, chrom: str = "chr11") -> str:
    c = chrom if chrom.startswith("chr") else f"chr{chrom}"
    return f"{c}_{pos}_{ref}_{alt}"


def is_eqtl_hit(
    associations: list[dict[str, Any]], p_thr: float = EQTL_P_THRESHOLD
) -> bool:
    nlog_thr = -math.log10(p_thr) if p_thr > 0 else EQTL_NLOG10P_THRESHOLD
    for a in associations:
        pv = a.get("pvalue")
        if pv is not None:
            try:
                if float(pv) <= p_thr:
                    return True
            except (TypeError, ValueError):
                pass
        nlog = a.get("nlog10p")
        if nlog is None:
            nlog = a.get("neg_log10_pvalue")
        if nlog is not None:
            try:
                if float(nlog) >= nlog_thr:
                    return True
            except (TypeError, ValueError):
                pass
    return False


def fisher_exact_2x2(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher's exact p-value (hypergeometric), pure Python.

    Table: [[a, b], [c, d]] with a=case_hit, b=case_miss, c=ctrl_hit, d=ctrl_miss.
    """
    if min(a, b, c, d) < 0:
        raise ValueError("negative counts")
    n = a + b + c + d
    if n == 0:
        return 1.0
    row1 = a + b
    col1 = a + c

    def _choose(n_: int, k: int) -> float:
        if k < 0 or k > n_:
            return 0.0
        return float(math.comb(n_, k))

    def _prob(x: int) -> float:
        return _choose(col1, x) * _choose(n - col1, row1 - x) / _choose(n, row1)

    lo = max(0, row1 - (n - col1))
    hi = min(row1, col1)
    p_obs = _prob(a)
    p = 0.0
    for x in range(lo, hi + 1):
        px = _prob(x)
        if px <= p_obs + 1e-15:
            p += px
    return min(1.0, max(0.0, p))


def decide_enrichment(
    n_hit_case: int,
    n_miss_case: int,
    n_hit_ctrl: int,
    n_miss_ctrl: int,
    *,
    p_alpha: float = 0.01,
    min_n: int = 30,
    min_abs_diff: float = 0.05,
) -> dict[str, Any]:
    n_case = n_hit_case + n_miss_case
    n_ctrl = n_hit_ctrl + n_miss_ctrl
    p_case = (n_hit_case / n_case) if n_case else float("nan")
    p_ctrl = (n_hit_ctrl / n_ctrl) if n_ctrl else float("nan")
    diff = p_case - p_ctrl if n_case and n_ctrl else float("nan")
    fisher_p = fisher_exact_2x2(n_hit_case, n_miss_case, n_hit_ctrl, n_miss_ctrl)
    out: dict[str, Any] = {
        "n_hit_case": n_hit_case,
        "n_miss_case": n_miss_case,
        "n_hit_ctrl": n_hit_ctrl,
        "n_miss_ctrl": n_miss_ctrl,
        "p_case": p_case,
        "p_ctrl": p_ctrl,
        "risk_diff": diff,
        "fisher_p": fisher_p,
        "verdict": "INCONCLUSIVE",
    }
    if n_case < min_n or n_ctrl < min_n:
        out["verdict"] = "INCONCLUSIVE"
        out["reason"] = "underpowered"
        return out
    if fisher_p <= p_alpha and p_case > p_ctrl:
        out["verdict"] = "PASS"
        out["reason"] = "enrichment_case_gt_ctrl"
        return out
    if fisher_p <= p_alpha and p_case <= p_ctrl:
        out["verdict"] = "REJECT"
        out["reason"] = "wrong_direction"
        return out
    if abs(diff) < min_abs_diff:
        out["verdict"] = "REJECT"
        out["reason"] = "negligible_diff"
        return out
    out["verdict"] = "INCONCLUSIVE"
    out["reason"] = "effect_uncertain"
    return out


def match_controls_by_af_decile(
    cases: list[dict[str, Any]],
    control_pool: list[dict[str, Any]],
    *,
    seed: int = SEED,
    cap: int | None = None,
    af_min: float = AF_MIN,
    af_max: float = AF_MAX,
) -> list[dict[str, Any]]:
    """Deterministic AF-decile matching without replacement."""
    rng = random.Random(seed)
    target_n = len(cases) if cap is None else min(len(cases), cap)
    by_dec: dict[int, list[dict[str, Any]]] = {i: [] for i in range(10)}
    for v in control_pool:
        d = af_decile(float(v["af"]), af_min=af_min, af_max=af_max)
        if 0 <= d <= 9:
            by_dec[d].append(v)
    for d in by_dec:
        by_dec[d].sort(key=lambda x: (x["pos"], x["ref"], x["alt"]))
        rng.shuffle(by_dec[d])

    need = {i: 0 for i in range(10)}
    for v in cases:
        d = af_decile(float(v["af"]), af_min=af_min, af_max=af_max)
        if 0 <= d <= 9:
            need[d] += 1
    total_need = sum(need.values()) or 1
    scaled = {i: int(round(need[i] * target_n / total_need)) for i in range(10)}
    while sum(scaled.values()) > target_n:
        k = max(scaled, key=lambda i: scaled[i])
        scaled[k] -= 1
    while sum(scaled.values()) < target_n:
        k = max(need, key=lambda i: need[i] - scaled[i])
        scaled[k] += 1

    picked: list[dict[str, Any]] = []
    used: set[str] = set()
    for d in range(10):
        take = scaled[d]
        for v in by_dec[d]:
            if take <= 0:
                break
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in used:
                continue
            used.add(vid)
            picked.append(v)
            take -= 1
    if len(picked) < target_n:
        rest = sorted(control_pool, key=lambda x: (x["pos"], x["ref"], x["alt"]))
        for v in rest:
            if len(picked) >= target_n:
                break
            vid = variant_id(v["chrom"], v["pos"], v["ref"], v["alt"])
            if vid in used:
                continue
            used.add(vid)
            picked.append(v)
    return picked[:target_n]


def classify_eqtl_query_result(
    associations: list[dict[str, Any]] | None,
    *,
    http_status: int | None = None,
    p_thr: float = EQTL_P_THRESHOLD,
) -> str:
    """Return HIT / MISS / ERROR per G9b rules.

    G9b: HTTP 400 → MISS (variant absent / not queryable in map).
    Empty 200 → MISS. Significant assoc → HIT.
    """
    if http_status == 400:
        return "MISS"
    if http_status is not None and http_status >= 500:
        return "ERROR"
    if associations is None:
        return "ERROR"
    if is_eqtl_hit(associations, p_thr=p_thr):
        return "HIT"
    return "MISS"


def fetch_eqtl_status(
    dataset_id: str,
    pos: int,
    ref: str,
    alt: str,
    *,
    chrom: str = "chr11",
    timeout: int = 60,
    retries: int = 4,
    miss_on_http_400: bool = False,
) -> str:
    """Fetch and classify association status for one variant."""
    variant = eqtl_variant_key(pos, ref, alt, chrom=chrom)
    q = urllib.parse.urlencode({"variant": variant, "size": 1000, "start": 0})
    url = f"{EQTL_API}/{dataset_id}/associations?{q}"
    last_status: int | None = None
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "DNK-TE3D-G9/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            if isinstance(data, list):
                assoc: list[dict[str, Any]] = data
            elif isinstance(data, dict) and "associations" in data:
                assoc = list(data["associations"])
            else:
                assoc = []
            return classify_eqtl_query_result(assoc, http_status=200)
        except urllib.error.HTTPError as exc:
            last_status = int(exc.code)
            last_err = exc
            if miss_on_http_400 and exc.code == 400:
                return "MISS"
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    if miss_on_http_400:
        return classify_eqtl_query_result(None, http_status=last_status)
    raise RuntimeError(f"eQTL fetch failed for {variant}: {last_err}")


def fetch_eqtl_associations(
    dataset_id: str,
    pos: int,
    ref: str,
    alt: str,
    *,
    timeout: int = 60,
    retries: int = 4,
) -> list[dict[str, Any]]:
    variant = eqtl_variant_key(pos, ref, alt)
    q = urllib.parse.urlencode({"variant": variant, "size": 1000, "start": 0})
    url = f"{EQTL_API}/{dataset_id}/associations?{q}"
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "DNK-TE3D-G9/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "associations" in data:
                return list(data["associations"])
            return []
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"eQTL fetch failed for {variant}: {last_err}")


def cap_sorted(
    variants: Iterable[dict[str, Any]], cap: int = PANEL_CAP
) -> list[dict[str, Any]]:
    rows = sorted(variants, key=lambda v: (v["pos"], v["ref"], v["alt"]))
    return rows[:cap]
