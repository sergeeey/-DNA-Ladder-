"""Stage-3 architecture anchor freeze — deterministic E/P definition for A754 and A518.

Pre-registers CTCF (E) and TSS-window (P) anchors in GRCh38 and their GRCh37 mapping for
Hi-C analysis.

Rules (from G4a_stage3_architecture_wt_contact_CLAIM_v1.md):
  E: unique HUDEP-2 CTCF BED peak where BED_start < variant_1based_pos <= BED_end.
  T: nearest protein-coding Ensembl gene TSS within ±1 Mb; strand-aware; tie-break by ENSG ID.
  P: TSS ± 2500 (1-based inclusive coordinates).
  Map E and P to GRCh37 via Ensembl REST; require single same-chromosome mapping.
  No eligible TSS → BLOCKED_NO_ELIGIBLE_TSS.
  No CTCF anchor → BLOCKED_NO_CTCF_ANCHOR.
  Mapping failure → BLOCKED_MAP_FAILED.

Safety assertions:
  1. Registry architecture_strong_1 == "chr11:75445532:G:A"  (A754)
  2. Registry architecture_strong_2 == "chr11:518575:C:A"    (A518)
  3. Registry holdout == SEALED
  4. Registry assignment_locked == true
  5. No path traversal into data/holdout
  6. No GRCh38 anchor window overlapping chr11:64,000,000–68,000,000 (sealed locus)

Usage:
  python freeze_stage3_architecture_anchors.py          # online (calls Ensembl REST)
  python freeze_stage3_architecture_anchors.py --offline # use existing cache only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml  # PyYAML

ROOT = Path(__file__).resolve().parents[2]
PROSPECTIVE = ROOT / "09_outputs" / "prospective"
CACHE_DIR = PROSPECTIVE / "stage3_architecture_anchor_cache"
REGISTRY = PROSPECTIVE / "prospective_panel_registry_v1.yaml"
CTCF_BED = ROOT / "pilot_scaffold" / "data" / "ctcf_HUDEP2_peaks.bed"
FREEZE_JSON = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json"
FREEZE_HASH = PROSPECTIVE / "stage3_architecture_anchor_freeze_v1.json.sha256"

ENSEMBL_BASE = "https://rest.ensembl.org"
USED_CACHE_FILES: set[Path] = set()

# Sealed region (GRCh38 and approximate GRCh37) — any anchor overlap → FORBIDDEN
SEALED_CHR = "chr11"
SEALED_START_38 = 64_000_000
SEALED_END_38 = 68_000_000

# Locked slot definitions
LOCKED_SLOTS: list[dict] = [
    {
        "slot_id": "ARCH_01",
        "candidate_id": "A754",
        "registry_key": "architecture_strong_1",
        "variant": "chr11:75445532:G:A",
        "chrom": "chr11",
        "chrom_num": "11",
        "pos_1based": 75_445_532,
    },
    {
        "slot_id": "ARCH_02",
        "candidate_id": "A518",
        "registry_key": "architecture_strong_2",
        "variant": "chr11:518575:C:A",
        "chrom": "chr11",
        "chrom_num": "11",
        "pos_1based": 518_575,
    },
]


# ---------------------------------------------------------------------------
# Safety assertions
# ---------------------------------------------------------------------------


def assert_registry_and_holdout(registry_path: Path) -> None:
    """Verify registry assignments exactly match CLAIM and holdout is SEALED."""
    reg = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    assignments = reg.get("stage3_slot_assignments", {})
    expected = {
        "architecture_strong_1": "chr11:75445532:G:A",
        "architecture_strong_2": "chr11:518575:C:A",
    }
    for key, val in expected.items():
        if assignments.get(key) != val:
            raise AssertionError(
                f"Registry mismatch: {key} expected {val!r}, got {assignments.get(key)!r}"
            )
    if not assignments.get("assignment_locked"):
        raise AssertionError("Registry stage3_slot_assignments.assignment_locked is not true")

    if reg.get("holdout") != "SEALED":
        raise AssertionError(f"Holdout is not SEALED: {reg.get('holdout')!r}")
    if reg.get("oligo_order") != "FORBIDDEN":
        raise AssertionError(
            f"Oligo order is not FORBIDDEN: {reg.get('oligo_order')!r}"
        )

    print("[OK] Registry assertions passed")


def assert_no_holdout_path(path: Path) -> None:
    """Raise if path string contains 'holdout'."""
    if "holdout" in str(path).lower():
        raise ForbiddenAccessError(f"FORBIDDEN: path contains 'holdout': {path}")


def assert_not_sealed_region_grch38(chrom: str, start: int, end: int) -> None:
    """Raise if the window overlaps chr11:64–68 Mb (sealed region, GRCh38)."""
    if chrom == SEALED_CHR and start < SEALED_END_38 and end > SEALED_START_38:
        raise ForbiddenAccessError(
            f"FORBIDDEN: GRCh38 window {chrom}:{start}-{end} overlaps sealed "
            f"{SEALED_CHR}:{SEALED_START_38}-{SEALED_END_38}"
        )


class ForbiddenAccessError(RuntimeError):
    """Raised when a forbidden path or region is accessed."""


# ---------------------------------------------------------------------------
# CTCF BED parsing
# ---------------------------------------------------------------------------


def find_ctcf_anchor(bed_path: Path, chrom: str, pos_1based: int) -> dict | None:
    """Return the first CTCF BED peak containing pos_1based (BED_start < pos <= BED_end).

    If multiple peaks match, return the one with the highest score (col 5 if present).
    Returns None if no peak matches.
    """
    assert_no_holdout_path(bed_path)
    hits: list[dict] = []
    with bed_path.open(encoding="utf-8") as fh:
        for raw in fh:
            if raw.startswith("#") or not raw.strip():
                continue
            parts = raw.strip().split()
            if len(parts) < 3 or parts[0] != chrom:
                continue
            start, end = int(parts[1]), int(parts[2])
            if start < pos_1based <= end:
                score = float(parts[4]) if len(parts) > 4 else 0.0
                peak_id = parts[3] if len(parts) > 3 else f"{chrom}:{start}-{end}"
                hits.append({"chrom": chrom, "start": start, "end": end, "score": score, "id": peak_id})

    if not hits:
        return None
    # WHY: highest score first; if tied, lexicographic peak ID is the tie-break.
    hits.sort(key=lambda h: (-h["score"], h["id"]))
    return hits[0]


# ---------------------------------------------------------------------------
# Ensembl REST helpers
# ---------------------------------------------------------------------------


def _fetch_json(url: str, retries: int = 3, delay: float = 2.0, timeout: int = 120) -> object:
    """Fetch a JSON endpoint, retrying on HTTP 429 or transient errors."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "DNA-Ladder-freeze/1.0 (research; contact: sboi)",
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = float(exc.headers.get("Retry-After", delay * (attempt + 1)))
                print(f"  Rate-limited; sleeping {wait:.1f}s")
                time.sleep(wait)
                continue
            raise
        except TimeoutError:
            print(f"  Timeout on attempt {attempt + 1}/{retries}: {url[:80]}...")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            continue
    raise RuntimeError(f"All retries exhausted for {url}")


def _cache_key(slug: str) -> str:
    return slug.replace("/", "_").replace(":", "_").replace("?", "_").replace(";", "_")


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for an immutable freeze input."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cached_fetch(url: str, cache_dir: Path, offline: bool) -> object:
    """Fetch URL with disk caching.  In offline mode, load from cache or raise."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(url)
    cache_file = cache_dir / f"{key}.json"
    if cache_file.exists():
        USED_CACHE_FILES.add(cache_file)
        return json.loads(cache_file.read_text(encoding="utf-8"))
    if offline:
        raise RuntimeError(f"Offline mode: cache missing for {url}")
    data = _fetch_json(url)
    cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    USED_CACHE_FILES.add(cache_file)
    return data


def get_ensembl_release(cache_dir: Path, offline: bool) -> str:
    """Return the current Ensembl release string from /info/data."""
    url = f"{ENSEMBL_BASE}/info/data?content-type=application/json"
    data = _cached_fetch(url, cache_dir, offline)
    releases: list = data.get("releases", []) if isinstance(data, dict) else []  # type: ignore[union-attr]
    return str(releases[0]) if releases else "unknown"


def get_genes_in_region(chrom_num: str, start: int, end: int, cache_dir: Path, offline: bool) -> list[dict]:
    """Return Ensembl protein-coding genes in the given GRCh38 region (1-based)."""
    region = f"{chrom_num}:{start}-{end}"
    url = (
        f"{ENSEMBL_BASE}/overlap/region/human/{region}"
        f"?feature=gene;biotype=protein_coding;content-type=application/json"
    )
    data = _cached_fetch(url, cache_dir, offline)
    return data if isinstance(data, list) else []  # type: ignore[return-value]


def pick_tss(genes: list[dict], variant_pos: int) -> dict | None:
    """Return the gene dict for the nearest TSS (strand-aware, tie-break ENSG ID).

    TSS is gene['start'] for + strand (strand==1) and gene['end'] for - strand.
    """
    candidates: list[tuple[int, str, int, dict]] = []
    for g in genes:
        if g.get("biotype") != "protein_coding":
            continue
        strand = g.get("strand", 0)
        if strand == 1:
            tss = g["start"]
        elif strand == -1:
            tss = g["end"]
        else:
            continue
        dist = abs(tss - variant_pos)
        ensg = g.get("id", "ENSG_unknown")
        candidates.append((dist, ensg, tss, g))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1]))
    _, _, tss, gene = candidates[0]
    gene = dict(gene)
    gene["_tss_1based"] = tss
    return gene


def map_grch38_to_grch37(chrom_num: str, start: int, end: int, cache_dir: Path, offline: bool) -> tuple[int, int]:
    """Map a GRCh38 region to GRCh37 via Ensembl REST.

    Returns (mapped_start, mapped_end) as 1-based coordinates.
    Raises if mapping produces zero or multiple same-chr mappings.
    """
    region = f"{chrom_num}:{start}..{end}"
    url = (
        f"{ENSEMBL_BASE}/map/human/GRCh38/{region}/GRCh37"
        f"?content-type=application/json"
    )
    data = _cached_fetch(url, cache_dir, offline)
    mappings: list = data.get("mappings", []) if isinstance(data, dict) else []  # type: ignore[union-attr]
    same_chr = [
        m for m in mappings
        if m.get("mapped", {}).get("seq_region_name") == chrom_num
    ]
    if len(same_chr) != 1:
        raise RuntimeError(
            f"Expected 1 same-chrom mapping for {chrom_num}:{start}..{end}, "
            f"got {len(same_chr)}: {same_chr}"
        )
    mapped = same_chr[0]["mapped"]
    return int(mapped["start"]), int(mapped["end"])


# ---------------------------------------------------------------------------
# Per-slot freeze logic
# ---------------------------------------------------------------------------


def freeze_slot(slot: dict, cache_dir: Path, offline: bool) -> dict:
    """Compute frozen anchor definitions for one slot."""
    chrom = slot["chrom"]
    chrom_num = slot["chrom_num"]
    pos = slot["pos_1based"]

    result: dict = {
        "slot_id": slot["slot_id"],
        "candidate_id": slot["candidate_id"],
        "variant": slot["variant"],
        "pos_1based_grch38": pos,
        "status": "OK",
        "allele_effect": "NOT_TESTED",
        "g4b": "NOT_TESTED",
        "wet": "NO_GO",
    }

    # --- FORBIDDEN: sealed region check ---
    assert_not_sealed_region_grch38(chrom, pos - 1, pos)

    # --- E anchor ---
    ctcf_hit = find_ctcf_anchor(CTCF_BED, chrom, pos)
    if ctcf_hit is None:
        result["status"] = "BLOCKED_NO_CTCF_ANCHOR"
        return result

    e_start38 = ctcf_hit["start"]
    e_end38 = ctcf_hit["end"]
    assert_not_sealed_region_grch38(chrom, e_start38, e_end38)
    result["E_grch38"] = {"chrom": chrom, "start": e_start38, "end": e_end38, "peak_id": ctcf_hit["id"]}

    # --- TSS / T anchor ---
    search_start = max(1, pos - 1_000_000)
    search_end = pos + 1_000_000
    genes = get_genes_in_region(chrom_num, search_start, search_end, cache_dir, offline)
    best = pick_tss(genes, pos)
    if best is None:
        result["status"] = "BLOCKED_NO_ELIGIBLE_TSS"
        return result

    tss = best["_tss_1based"]
    result["T_gene"] = {
        "ensg_id": best.get("id"),
        "display_name": best.get("display_name") or best.get("external_name"),
        "strand": best.get("strand"),
        "tss_1based_grch38": tss,
        "distance_to_variant_bp": abs(tss - pos),
    }

    # --- P window ---
    p_start38 = tss - 2500
    p_end38 = tss + 2500
    assert_not_sealed_region_grch38(chrom, p_start38, p_end38)
    result["P_grch38"] = {"chrom": chrom, "start": p_start38, "end": p_end38}

    # --- GRCh38 → GRCh37 mapping ---
    try:
        # BED start is 0-based; Ensembl REST map coordinates are 1-based
        # inclusive. The BED end already equals the inclusive 1-based end.
        e_s37, e_e37 = map_grch38_to_grch37(
            chrom_num,
            e_start38 + 1,
            e_end38,
            cache_dir,
            offline,
        )
    except RuntimeError as exc:
        result["status"] = "BLOCKED_MAP_FAILED"
        result["map_error"] = str(exc)
        return result

    try:
        p_s37, p_e37 = map_grch38_to_grch37(chrom_num, p_start38, p_end38, cache_dir, offline)
    except RuntimeError as exc:
        result["status"] = "BLOCKED_MAP_FAILED"
        result["map_error"] = str(exc)
        return result

    result["E_grch37"] = {"chrom": chrom_num, "start": e_s37, "end": e_e37}
    result["P_grch37"] = {"chrom": chrom_num, "start": p_s37, "end": p_e37}
    result["tss_1based_grch37"] = (p_s37 + p_e37) // 2  # approx midpoint

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(offline: bool = False) -> None:
    USED_CACHE_FILES.clear()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Safety gate
    assert_registry_and_holdout(REGISTRY)
    assert_no_holdout_path(CTCF_BED)

    ensembl_release = get_ensembl_release(CACHE_DIR, offline)
    print(f"[INFO] Ensembl release: {ensembl_release}")

    slots_out = []
    for slot in LOCKED_SLOTS:
        print(f"\n[SLOT] {slot['slot_id']} ({slot['candidate_id']}) — {slot['variant']}")
        s = freeze_slot(slot, CACHE_DIR, offline)
        print(f"       status={s['status']}")
        if s.get("T_gene"):
            g = s["T_gene"]
            print(f"       TSS={g['ensg_id']} ({g.get('display_name')}) dist={g['distance_to_variant_bp']} bp")
        if s.get("E_grch37"):
            e = s["E_grch37"]
            print(f"       E hg19 = {e['chrom']}:{e['start']}-{e['end']}")
        if s.get("P_grch37"):
            p = s["P_grch37"]
            print(f"       P hg19 = {p['chrom']}:{p['start']}-{p['end']}")
        slots_out.append(s)

    payload = {
        "freeze_version": "stage3_architecture_anchor_freeze_v1",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "ensembl_release": ensembl_release,
        "claim": "G4a_stage3_architecture_wt_contact_CLAIM_v1.md",
        "ctcf_bed_source": str(CTCF_BED),
        "holdout": "SEALED",
        "B0_status": "UNSIGNED_NO_GO",
        "allele_effect_all_slots": "NOT_TESTED",
        "g4b_all_slots": "NOT_TESTED",
        "wet_all_slots": "NO_GO",
        "source_sha256": {
            "registry": sha256_file(REGISTRY),
            "ctcf_bed": sha256_file(CTCF_BED),
            "claim": sha256_file(
                PROSPECTIVE / "G4a_stage3_architecture_wt_contact_CLAIM_v1.md"
            ),
        },
        "cache_sha256": {
            path.name: sha256_file(path)
            for path in sorted(USED_CACHE_FILES)
        },
        "slots": slots_out,
    }

    FREEZE_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    digest = hashlib.sha256(FREEZE_JSON.read_bytes()).hexdigest()
    FREEZE_HASH.write_text(digest + "\n", encoding="utf-8")

    print(f"\n[OK] Freeze written: {FREEZE_JSON.name}")
    print(f"[OK] SHA256: {digest}")

    # Summary
    for s in slots_out:
        print(f"  {s['slot_id']} {s['candidate_id']:6s}  {s['status']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Freeze Stage-3 architecture anchors")
    parser.add_argument("--offline", action="store_true", help="Use cached Ensembl responses only")
    args = parser.parse_args()
    main(offline=args.offline)
