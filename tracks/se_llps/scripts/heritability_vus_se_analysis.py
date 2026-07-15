#!/usr/bin/env python3
"""exp_heritability_vus_se_frequency: for ClinVar VUS classified by
super-enhancer membership (fetch_clinvar_vus_grch38.py output), look up
gnomAD v4 (GRCh38-native) population allele frequency per variant and test
whether VUS-in-SE show a different (expected: lower/rarer) frequency
distribution than VUS-outside-SE. Mann-Whitney U + Cliff's delta on
log10(AF), absent-from-gnomAD treated as AF=0 (a real ICE category, not
missing data -- see claim.md).

Pre-registered in claim.md BEFORE this script ran: MCID |Cliff's delta|
>= 0.2 AND BH-corrected p < 0.05, tested separately for K562-SE and
HepG2-SE stratification (2 tests, BH-corrected).
"""

import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

VUS_FILE = ROOT / "data/input/clinvar_vus_grch38_se_classified.json"
GNOMAD_CACHE_FILE = ROOT / "data/input/gnomad_af_cache_vus.json"
RESULTS_FILE = ROOT / "experiments/exp_heritability_vus_se_frequency/results.json"

GNOMAD_API = "https://gnomad.broadinstitute.org/api"
# Cap the "outside-SE" comparator to a random, fixed-seed subsample for a
# tractable number of gnomAD API calls -- documented here (pre-registration
# addendum), same pattern as ARCHCODE's Hypothesis C benign-subsampling.
OUTSIDE_SE_SAMPLE_SIZE = 3000
SAMPLE_SEED = 42


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
                return 0.0  # not found in gnomAD -- treated as AF=0 (ICE strategy, see claim.md)
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


def annotate_af(variants, cache):
    remaining = [v for v in variants if _vkey(v) not in cache]
    print(
        f"  Querying gnomAD for {len(remaining)} remaining variants (of {len(variants)} total)..."
    )
    for i, v in enumerate(remaining):
        key = _vkey(v)
        if not v.get("position_vcf") or not v.get("ref_vcf") or not v.get("alt_vcf"):
            cache[key] = None
            continue
        af = gnomad_af(v["chrom"], v["position_vcf"], v["ref_vcf"], v["alt_vcf"])
        cache[key] = af
        if (i + 1) % 100 == 0:
            with open(GNOMAD_CACHE_FILE, "w") as f:
                json.dump(cache, f)
            print(f"    ...{i + 1}/{len(remaining)} annotated (cache saved)", file=sys.stderr)
        time.sleep(0.05)
    with open(GNOMAD_CACHE_FILE, "w") as f:
        json.dump(cache, f)
    return cache


def _vkey(v):
    return f"{v['chrom']}:{v.get('position_vcf')}:{v.get('ref_vcf')}:{v.get('alt_vcf')}"


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
    # AF=0 (absent from gnomAD) mapped to a floor value below the smallest
    # observable gnomAD AF (~1/gnomAD sample size), not log(0) (undefined).
    floor = -7.0  # ~1e-7, below gnomAD's practical detection limit
    if af is None or af == 0.0:
        return floor
    return math.log10(af)


def main():
    with open(VUS_FILE) as f:
        vus_data = json.load(f)
    variants = vus_data["variants"]
    valid = [
        v
        for v in variants
        if v.get("position_vcf")
        and v.get("ref_vcf")
        and v.get("alt_vcf")
        and len(v.get("ref_vcf", "")) == 1
        and len(v.get("alt_vcf", "")) == 1
    ]
    print(f"Loaded {len(variants)} VUS total, {len(valid)} valid simple SNVs for gnomAD lookup")

    in_k562_full = [v for v in valid if v["in_se"]["K562"]]
    in_hepg2_full = [v for v in valid if v["in_se"]["HepG2"]]
    outside_both = [v for v in valid if not v["in_se"]["K562"] and not v["in_se"]["HepG2"]]

    def subsample(vlist, cap, seed):
        return random.Random(seed).sample(vlist, cap) if len(vlist) > cap else vlist

    # Pre-registered in claim.md addendum (2026-07-08), after seeing population sizes but
    # BEFORE any gnomAD AF lookup: 25,726 K562-SE + 9,537 HepG2-SE VUS is too many individual
    # gnomAD API calls for this session -- subsample each to the same cap as outside-SE.
    in_k562 = subsample(in_k562_full, OUTSIDE_SE_SAMPLE_SIZE, SAMPLE_SEED)
    in_hepg2 = subsample(in_hepg2_full, OUTSIDE_SE_SAMPLE_SIZE, SAMPLE_SEED)
    outside_sample = subsample(outside_both, OUTSIDE_SE_SAMPLE_SIZE, SAMPLE_SEED)
    print(
        f"K562 SE: {len(in_k562)} sampled (of {len(in_k562_full)}), "
        f"HepG2 SE: {len(in_hepg2)} sampled (of {len(in_hepg2_full)}), "
        f"outside-both: {len(outside_sample)} sampled (of {len(outside_both)}), seed={SAMPLE_SEED}"
    )

    to_annotate = in_k562 + in_hepg2 + outside_sample
    cache = {}
    if GNOMAD_CACHE_FILE.exists():
        with open(GNOMAD_CACHE_FILE) as f:
            cache = json.load(f)
        print(f"  Resuming from partial gnomAD cache: {len(cache)} variants already annotated")
    cache = annotate_af(to_annotate, cache)

    def afs_for(vlist):
        out = []
        for v in vlist:
            af = cache.get(_vkey(v))
            if af is not None:
                out.append(log10_af(af))
        return out

    log_af_k562 = afs_for(in_k562)
    log_af_hepg2 = afs_for(in_hepg2)
    log_af_outside = afs_for(outside_sample)

    u_k562, p_k562, delta_k562 = mann_whitney_u(log_af_k562, log_af_outside)
    u_hepg2, p_hepg2, delta_hepg2 = mann_whitney_u(log_af_hepg2, log_af_outside)
    p_adj = benjamini_hochberg([p_k562, p_hepg2])

    def median(xs):
        s = sorted(xs)
        n = len(s)
        if n == 0:
            return None
        mid = n // 2
        return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0

    results = {
        "n_vus_total": len(variants),
        "n_valid_snv": len(valid),
        "n_in_k562_se_total": len(in_k562_full),
        "n_in_k562_se_sampled": len(in_k562),
        "n_in_hepg2_se_total": len(in_hepg2_full),
        "n_in_hepg2_se_sampled": len(in_hepg2),
        "n_outside_both_total": len(outside_both),
        "n_outside_sampled": len(outside_sample),
        "sample_seed": SAMPLE_SEED,
        "k562_vs_outside": {
            "n_k562": len(log_af_k562),
            "n_outside": len(log_af_outside),
            "median_log10af_k562": median(log_af_k562),
            "median_log10af_outside": median(log_af_outside),
            "mann_whitney_U": u_k562,
            "p_value": p_k562,
            "cliffs_delta": delta_k562,
            "p_value_bh": p_adj[0],
        },
        "hepg2_vs_outside": {
            "n_hepg2": len(log_af_hepg2),
            "n_outside": len(log_af_outside),
            "median_log10af_hepg2": median(log_af_hepg2),
            "median_log10af_outside": median(log_af_outside),
            "mann_whitney_U": u_hepg2,
            "p_value": p_hepg2,
            "cliffs_delta": delta_hepg2,
            "p_value_bh": p_adj[1],
        },
        "mcid": "abs(cliffs_delta) >= 0.2 AND p_value_bh < 0.05",
    }

    print(json.dumps(results, indent=2))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
