#!/usr/bin/env python3
"""exp_heritability_vus_se_vs_typical_enhancer: reclassifies the already-
fetched genome-wide ClinVar VUS set (from exp_heritability_vus_se_frequency)
by H3K27ac/super-enhancer membership per cell line, and compares gnomAD AF
between VUS-in-SE and VUS-in-matched-typical-enhancer (H3K27ac-marked,
not super) -- correcting the original experiment's weak "vs everywhere
else" comparator, same lesson as the LLPS matched-control follow-up.
Reuses the gnomAD cache from the original experiment; only queries new
variants (the typical-enhancer subsample) that weren't already looked up.
"""

import bisect
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

VUS_FILE = ROOT / "data/input/clinvar_vus_grch38_se_classified.json"
H3K27AC_FILES = {
    "K562": ROOT / "data/input/h3k27ac_k562_grch38.json",
    "HepG2": ROOT / "data/input/h3k27ac_hepg2_grch38.json",
}
GNOMAD_CACHE_FILE = ROOT / "data/input/gnomad_af_cache_vus.json"
RESULTS_FILE = ROOT / "experiments/exp_heritability_vus_se_vs_typical_enhancer/results.json"

GNOMAD_API = "https://gnomad.broadinstitute.org/api"
SAMPLE_CAP = 3000
SAMPLE_SEED = 42


def load_h3k27ac_intervals(path):
    with open(path) as f:
        data = json.load(f)
    by_chrom = defaultdict(list)
    for p in data["peaks"]:
        by_chrom[p["chrom"]].append((p["start"], p["end"]))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return dict(by_chrom)


def in_any_interval(chrom, pos, by_chrom):
    intervals = by_chrom.get(chrom)
    if not intervals:
        return False
    starts = [s for s, _ in intervals]
    i = bisect.bisect_right(starts, pos) - 1
    if i < 0:
        return False
    s, e = intervals[i]
    return s <= pos < e


def gnomad_af(chrom, pos, ref, alt, retries=3):
    variant_id = f"{chrom.replace('chr', '')}-{pos}-{ref}-{alt}"
    query = """
    query($variantId: String!) {
      variant(variantId: $variantId, dataset: gnomad_r4) {
        genome { af }
        exome { af }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"variantId": variant_id}}).encode()
    req = urllib.request.Request(
        GNOMAD_API, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
            v = data.get("data", {}).get("variant")
            if v is None:
                return 0.0
            genome_af = (v.get("genome") or {}).get("af")
            exome_af = (v.get("exome") or {}).get("af")
            afs = [a for a in (genome_af, exome_af) if a is not None]
            return max(afs) if afs else 0.0
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2**attempt)
                continue
            return None
        except Exception:
            time.sleep(1)
    return None


def _vkey(v):
    # v is a slim tuple: (chrom, position_vcf, ref_vcf, alt_vcf, in_se_k562, in_se_hepg2)
    return f"{v[0]}:{v[1]}:{v[2]}:{v[3]}"


def annotate_af(variants, cache):
    remaining = [v for v in variants if _vkey(v) not in cache]
    print(
        f"  Querying gnomAD for {len(remaining)} NEW variants (of {len(variants)} total; "
        f"{len(variants) - len(remaining)} already cached)..."
    )
    for i, v in enumerate(remaining):
        key = _vkey(v)
        af = gnomad_af(v[0], v[1], v[2], v[3])
        cache[key] = af
        if (i + 1) % 100 == 0:
            with open(GNOMAD_CACHE_FILE, "w") as f:
                json.dump(cache, f)
            print(
                f"    ...{i + 1}/{len(remaining)} new variants annotated (cache saved)",
                file=sys.stderr,
            )
        time.sleep(0.05)
    with open(GNOMAD_CACHE_FILE, "w") as f:
        json.dump(cache, f)
    return cache


def mann_whitney_u(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return float("nan"), float("nan"), float("nan")
    combined = [(d, 0) for d in group1] + [(d, 1) for d in group2]
    combined.sort(key=lambda x: x[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    cliffs_delta = (2 * u1 / (n1 * n2)) - 1
    if sigma == 0:
        return u1, float("nan"), cliffs_delta
    z = (u1 - mu) / sigma
    p = math.erfc(abs(z) / math.sqrt(2))
    return u1, p, cliffs_delta


def benjamini_hochberg(p_values):
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * n
    prev = 1.0
    for rank, (idx, p) in enumerate(reversed(indexed), start=1):
        bh_rank = n - rank + 1
        val = min(prev, p * n / bh_rank)
        adjusted[idx] = val
        prev = val
    return adjusted


def log10_af(af):
    floor = -7.0
    if af is None or af == 0.0:
        return floor
    return math.log10(af)


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def main():
    # Memory-lean loading: this file is 372MB / 2.25M records. json.load() must
    # materialize it fully regardless (stdlib has no streaming parser), but we
    # immediately slim each record down to a 6-field tuple (not a dict with a
    # nested dict) and drop the original structure -- cuts peak RSS well below
    # keeping both the raw parse and a second filtered list alive at once
    # (the previous version's `valid = [...]` did exactly that and likely
    # caused the OOM-style crash on the first run attempt, given ~1.9GB free
    # RAM observed on this machine at run time).
    print("Loading genome-wide VUS set (this is a ~370MB file, may take a moment)...")
    with open(VUS_FILE) as f:
        vus_data = json.load(f)
    raw_variants = vus_data["variants"]
    n_total = len(raw_variants)
    print(f"  Parsed {n_total} VUS records, slimming...")

    valid = []
    for v in raw_variants:
        pos, ref, alt = v.get("position_vcf"), v.get("ref_vcf"), v.get("alt_vcf")
        if not pos or not ref or not alt or len(ref) != 1 or len(alt) != 1:
            continue
        valid.append((v["chrom"], int(pos), ref, alt, v["in_se"]["K562"], v["in_se"]["HepG2"]))
    del raw_variants, vus_data
    print(f"  {len(valid)} valid simple SNVs (slimmed; raw parse freed)")

    h3k27ac_by_cell = {name: load_h3k27ac_intervals(path) for name, path in H3K27AC_FILES.items()}
    print(f"  Loaded H3K27ac interval sets: {list(h3k27ac_by_cell.keys())}")

    cache = {}
    if GNOMAD_CACHE_FILE.exists():
        with open(GNOMAD_CACHE_FILE) as f:
            cache = json.load(f)
        print(f"  Resuming from existing gnomAD cache: {len(cache)} variants already annotated")

    all_results = {}
    for cell in ("K562", "HepG2"):
        print(f"\n=== {cell} ===")
        se_idx = 4 if cell == "K562" else 5
        in_se = [v for v in valid if v[se_idx]]
        in_typical = [
            v for v in valid if not v[se_idx] and in_any_interval(v[0], v[1], h3k27ac_by_cell[cell])
        ]
        print(
            f"  In SE: {len(in_se)} total, in typical enhancer (H3K27ac, not SE): {len(in_typical)} total"
        )

        se_sample = (
            random.Random(SAMPLE_SEED).sample(in_se, SAMPLE_CAP)
            if len(in_se) > SAMPLE_CAP
            else in_se
        )
        typical_sample = (
            random.Random(SAMPLE_SEED).sample(in_typical, SAMPLE_CAP)
            if len(in_typical) > SAMPLE_CAP
            else in_typical
        )
        print(
            f"  Sampled: SE={len(se_sample)}, typical-enhancer={len(typical_sample)} (seed={SAMPLE_SEED})"
        )

        cache = annotate_af(se_sample + typical_sample, cache)

        def afs_for(vlist, cache_ref):
            out = []
            for v in vlist:
                af = cache_ref.get(_vkey(v))
                if af is not None:
                    out.append(log10_af(af))
            return out

        log_af_se = afs_for(se_sample, cache)
        log_af_typical = afs_for(typical_sample, cache)

        u, p, delta = mann_whitney_u(log_af_se, log_af_typical)

        print(f"  n_SE={len(log_af_se)}, n_typical={len(log_af_typical)}")
        print(
            f"  median_log10af_SE={median(log_af_se)}, median_log10af_typical={median(log_af_typical)}"
        )
        print(f"  Mann-Whitney U={u}, p={p}, Cliff's delta={delta}")

        all_results[cell] = {
            "n_se_total": len(in_se),
            "n_typical_total": len(in_typical),
            "n_se_sampled": len(se_sample),
            "n_typical_sampled": len(typical_sample),
            "n_se_with_af": len(log_af_se),
            "n_typical_with_af": len(log_af_typical),
            "median_log10af_se": median(log_af_se),
            "median_log10af_typical": median(log_af_typical),
            "mann_whitney_U": u,
            "p_value": p,
            "cliffs_delta": delta,
        }

    p_values = [all_results["K562"]["p_value"], all_results["HepG2"]["p_value"]]
    p_adj = benjamini_hochberg(p_values)
    all_results["K562"]["p_value_bh"] = p_adj[0]
    all_results["HepG2"]["p_value_bh"] = p_adj[1]
    all_results["mcid"] = "abs(cliffs_delta) >= 0.2 AND p_value_bh < 0.05"
    all_results["sample_seed"] = SAMPLE_SEED

    print("\n" + json.dumps(all_results, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
