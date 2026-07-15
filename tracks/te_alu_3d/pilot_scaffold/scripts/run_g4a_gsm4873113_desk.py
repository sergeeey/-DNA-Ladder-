"""G4a desk: locked E–P contact vs same-distance background in GSM4873113."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DUMP = ROOT / "09_outputs" / "prospective" / "g4a_dumps"
OUT_MD = ROOT / "09_outputs" / "prospective" / "G4a_gsm4873113_desk_pass_v1.md"
OUT_JSON = ROOT / "09_outputs" / "prospective" / "G4a_gsm4873113_metrics.json"

# hg19 locked
E = (62157472, 62162472)
P = (62457472, 62462472)
C1 = 62521395


def load_triples(path: Path) -> list[tuple[int, int, float]]:
    rows: list[tuple[int, int, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        rows.append((int(parts[0]), int(parts[1]), float(parts[2])))
    return rows


def bin_of(coord: int, binsize: int) -> int:
    return (coord // binsize) * binsize


def analyze(obs_path: Path, oe_path: Path, binsize: int) -> dict:
    obs = load_triples(obs_path)
    oe = {(a, b): v for a, b, v in load_triples(oe_path)}
    # expand upper triangle to both orientations for lookup
    obs_map: dict[tuple[int, int], float] = {}
    for a, b, v in obs:
        obs_map[(a, b)] = v
        obs_map[(b, a)] = v

    e_bins = sorted({bin_of(E[0], binsize), bin_of(E[1] - 1, binsize)})
    p_bins = sorted({bin_of(P[0], binsize), bin_of(P[1] - 1, binsize)})
    c1_bin = bin_of(C1, binsize)

    ep_pairs = [(eb, pb) for eb in e_bins for pb in p_bins]
    ep_obs = []
    ep_oe = []
    for a, b in ep_pairs:
        if (a, b) in obs_map:
            ep_obs.append(obs_map[(a, b)])
        if (a, b) in oe:
            ep_oe.append(oe[(a, b)])
        elif (b, a) in oe:
            ep_oe.append(oe[(b, a)])

    # primary EP: mid bins (10kb: 62160000 x 62460000; 25kb: 62150000 x 62450000)
    e_mid = bin_of((E[0] + E[1]) // 2, binsize)
    p_mid = bin_of((P[0] + P[1]) // 2, binsize)
    primary = (e_mid, p_mid)
    primary_obs = obs_map.get(primary)
    primary_oe = oe.get(primary) or oe.get((p_mid, e_mid))

    # same genomic distance background within dumped window
    target_dist = abs(p_mid - e_mid)
    tol = binsize  # ±1 bin
    bg_obs = []
    bg_oe = []
    for a, b, v in obs:
        d = abs(b - a)
        if abs(d - target_dist) <= tol and not (
            min(a, b) in e_bins and max(a, b) in p_bins
        ):
            bg_obs.append(v)
            ov = oe.get((a, b)) or oe.get((b, a))
            if ov is not None:
                bg_oe.append(ov)

    def pct_rank(x: float | None, arr: list[float]) -> float | None:
        if x is None or not arr:
            return None
        return sum(1 for t in arr if t <= x) / len(arr)

    mean_bg = statistics.mean(bg_obs) if bg_obs else None
    med_bg = statistics.median(bg_obs) if bg_obs else None
    enrich = (primary_obs / mean_bg) if (primary_obs and mean_bg) else None

    # coverage: nonzero pixels around C1 row
    c1_row = [v for (a, b), v in obs_map.items() if a == c1_bin or b == c1_bin]
    coverage_c1 = len([v for v in c1_row if v > 0])

    return {
        "binsize": binsize,
        "e_bins": e_bins,
        "p_bins": p_bins,
        "c1_bin": c1_bin,
        "primary_pair": list(primary),
        "primary_obs_KR": primary_obs,
        "primary_oe_KR": primary_oe,
        "ep_pair_obs_values": ep_obs,
        "ep_pair_oe_values": ep_oe,
        "same_distance_bg_n": len(bg_obs),
        "same_distance_bg_mean_obs": mean_bg,
        "same_distance_bg_median_obs": med_bg,
        "enrichment_vs_mean_bg": enrich,
        "primary_obs_percentile_same_dist": pct_rank(primary_obs, bg_obs),
        "primary_oe_percentile_same_dist": pct_rank(primary_oe, bg_oe),
        "same_distance_bg_mean_oe": statistics.mean(bg_oe) if bg_oe else None,
        "c1_row_nonzero_pixels": coverage_c1,
        "n_obs_pixels_in_dump": len(obs),
    }


def verdict(m10: dict, m25: dict) -> str:
    """Conservative desk verdict — not wet-lab GO."""
    checks = []
    for m in (m10, m25):
        e = m.get("enrichment_vs_mean_bg")
        p = m.get("primary_obs_percentile_same_dist")
        oe = m.get("primary_oe_KR")
        ok = (
            m.get("primary_obs_KR") is not None
            and m.get("c1_row_nonzero_pixels", 0) > 0
            and e is not None
            and e >= 1.5
            and p is not None
            and p >= 0.75
            and oe is not None
            and oe >= 1.2
        )
        soft = (
            m.get("primary_obs_KR") is not None
            and e is not None
            and e >= 1.2
            and p is not None
            and p >= 0.60
        )
        checks.append((ok, soft, m["binsize"]))
    if all(c[0] for c in checks):
        return "PASS_DESK"
    if any(c[0] for c in checks) or all(c[1] for c in checks):
        return "INCONCLUSIVE_LEAN_POSITIVE"
    if any(c[1] for c in checks):
        return "INCONCLUSIVE"
    return "FAIL_DESK"


def main() -> None:
    m10 = analyze(
        DUMP / "obs_KR_10kb_chr11_62Mb.txt",
        DUMP / "oe_KR_10kb_chr11_62Mb.txt",
        10000,
    )
    m25 = analyze(
        DUMP / "obs_KR_25kb_chr11_62Mb.txt",
        DUMP / "oe_KR_25kb_chr11_62Mb.txt",
        25000,
    )
    v = verdict(m10, m25)
    payload = {
        "dataset": "GSE160422",
        "sample": "GSM4873113",
        "biosource": "HUDEP-2",
        "genome_build": "hg19",
        "locked_E_hg19": f"chr11:{E[0]}-{E[1]}",
        "locked_P_hg19": f"chr11:{P[0]}-{P[1]}",
        "C1_hg19": f"chr11:{C1}",
        "norm": "KR",
        "verdict": v,
        "metrics_10kb": m10,
        "metrics_25kb": m25,
        "g4b": "NOT_TESTED",
        "note": "Desk G4a only; single .hic, no independent replicate file in this dump.",
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def fmt(m: dict) -> str:
        return "\n".join(
            [
                f"| binsize | {m['binsize']} |",
                f"| primary pair | {m['primary_pair'][0]} × {m['primary_pair'][1]} |",
                f"| observed KR | {m['primary_obs_KR']} |",
                f"| OE KR | {m['primary_oe_KR']} |",
                f"| same-dist bg n | {m['same_distance_bg_n']} |",
                f"| bg mean obs | {m['same_distance_bg_mean_obs']} |",
                f"| enrichment vs mean | {m['enrichment_vs_mean_bg']} |",
                f"| obs percentile | {m['primary_obs_percentile_same_dist']} |",
                f"| OE percentile | {m['primary_oe_percentile_same_dist']} |",
                f"| C1-row nonzero | {m['c1_row_nonzero_pixels']} |",
            ]
        )

    md = f"""# G4a desk pass — GSM4873113 (HUDEP-2 WT Hi-C)

**Date:** 2026-07-14  
**Method:** `juicer_tools dump` observed/OE KR on local `.hic`  
**Locks:** `C1_claim_freeze_pack_v1.md` / `c1_ep_liftover_hg19.yaml`  
**Verdict:** `{v}`

## Status translation

| Gate | Status |
|------|--------|
| G4a WT Contact(E,P) | **{v}** (desk) |
| G4b allele ΔContact | NOT TESTED |
| Architecture freeze | still **NO-GO** until P1 + edit/assay path |
| Allowed language | still activity-candidate unless Branch A fully opens |

## Locus (hg19)

| Anchor | Coordinate |
|--------|------------|
| E | chr11:62157472-62162472 |
| P | chr11:62457472-62462472 |
| C1 | chr11:62521395 |

## Metrics 10 kb

{fmt(m10)}

## Metrics 25 kb

{fmt(m25)}

## Decision rule (pre-registered for this desk)

```text
PASS_DESK if at BOTH 10kb and 25kb:
  primary_obs present
  AND enrichment_vs_mean_bg ≥ 1.5
  AND obs percentile among same-distance bins ≥ 0.75
  AND OE ≥ 1.2
  AND C1-row has nonzero coverage
```

Soft positive / mixed → INCONCLUSIVE(_LEAN_POSITIVE).  

## Caveats

- Single sample `.hic` (no second WT replicate dump here).
- E/P remain K562-proxy locks mapped to hg19 — gene identity of P not claimed.
- KR values are relative; do not over-interpret absolute counts.
- Capture Hi-C of this series is β-globin-targeted and was not used for C1.

## Next

- If PASS / lean-positive: download GSM4873114/3115 for P1-system.
- If FAIL: Branch B activity; drop architecture primary claim.
- Do not rewrite E/P after seeing these numbers.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"verdict": v, "m10": m10, "m25": m25}, indent=2))


if __name__ == "__main__":
    main()
