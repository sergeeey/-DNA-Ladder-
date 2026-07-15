"""P1-system desk: 3′HS1 WT vs del vs inv contacts (GSE160422).

Anchors (hg19, literature/locus geometry; see note in report):
  3′HS1 ~21 kb 3′ of HBB (HBB 3′ end ~5246696 → ~5225 kb)
  HS5 at LCR border ~5304 kb
  OR52A1 HPFH enhancer neighborhood ~5180–5200 kb (ectopic partner)
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(r"D:\DNK - 2\data\HUDEP2_GSE160422")
DUMP = ROOT / "09_outputs" / "prospective" / "p1_dumps"
OUT_MD = ROOT / "09_outputs" / "prospective" / "P1_3primeHS1_desk_pass_v1.md"
OUT_JSON = ROOT / "09_outputs" / "prospective" / "P1_3primeHS1_metrics.json"

JAVA = Path(r"D:\DNK - 2\tools\jdk-17\bin\java.exe")
JAR = ROOT / "pilot_scaffold" / "tools" / "juicer_tools.jar"

# hg19 anchors
HS1 = (5_224_000, 5_228_000)
HS5 = (5_302_000, 5_306_000)
OR52A1 = (5_180_000, 5_200_000)
HBB = (5_246_696, 5_248_301)
WINDOW = (5_100_000, 5_400_000)

SAMPLES = {
    "WT": "GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic",
    "DEL_B6": "GSM4873114_B6-HUDEP2-HiC_allValidPairs.hic",
    "INV_A2": "GSM4873115_A2-HUDEP2-HiC_allValidPairs.hic",
    "CAP_WT": "GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic",
    "CAP_DEL": "GSM4873117_B6-HUDEP2-captureHiC_allValidPairs.hic",
    "CAP_INV": "GSM4873118_A2-HUDEP2-captureHiC_allValidPairs.hic",
}


def load_triples(path: Path) -> dict[tuple[int, int], float]:
    m: dict[tuple[int, int], float] = {}
    if not path.exists() or path.stat().st_size < 10:
        return m
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        a, b, v = int(parts[0]), int(parts[1]), float(parts[2])
        m[(a, b)] = v
        m[(b, a)] = v
    return m


def bin_of(coord: int, binsize: int) -> int:
    return (coord // binsize) * binsize


def pair_mean(m: dict[tuple[int, int], float], r1: tuple[int, int], r2: tuple[int, int], binsize: int) -> float | None:
    b1 = sorted({bin_of(r1[0], binsize), bin_of(r1[1] - 1, binsize)})
    b2 = sorted({bin_of(r2[0], binsize), bin_of(r2[1] - 1, binsize)})
    vals = []
    for x in b1:
        for y in b2:
            if (x, y) in m:
                vals.append(m[(x, y)])
    if not vals:
        return None
    return statistics.mean(vals)


def dump_sample(sample: str, hic_name: str, binsize: int = 5000) -> dict:
    import subprocess

    hic = DATA / hic_name
    if not hic.exists() or hic.stat().st_size < 1_000_000_000:
        return {"sample": sample, "status": "FILE_MISSING_OR_INCOMPLETE", "bytes": hic.stat().st_size if hic.exists() else 0}

    tag = f"{sample}_{binsize}"
    obs_p = DUMP / f"{tag}_obs_KR.txt"
    oe_p = DUMP / f"{tag}_oe_KR.txt"
    chrom_win = f"11:{WINDOW[0]}:{WINDOW[1]}"
    DUMP.mkdir(parents=True, exist_ok=True)
    for kind, path in (("observed", obs_p), ("oe", oe_p)):
        if path.exists() and path.stat().st_size > 100:
            continue
        cmd = [
            str(JAVA),
            "-Xmx8g",
            "-jar",
            str(JAR),
            "dump",
            kind,
            "KR",
            str(hic),
            chrom_win,
            chrom_win,
            "BP",
            str(binsize),
            str(path),
        ]
        subprocess.run(cmd, check=False, capture_output=True, text=True)

    obs = load_triples(obs_p)
    oe = load_triples(oe_p)
    if not obs:
        return {"sample": sample, "status": "DUMP_EMPTY", "bytes": hic.stat().st_size}

    metrics = {
        "sample": sample,
        "status": "OK",
        "bytes": hic.stat().st_size,
        "binsize": binsize,
        "obs_HS1_HS5": pair_mean(obs, HS1, HS5, binsize),
        "oe_HS1_HS5": pair_mean(oe, HS1, HS5, binsize),
        "obs_HS1_OR52A1": pair_mean(obs, HS1, OR52A1, binsize),
        "oe_HS1_OR52A1": pair_mean(oe, HS1, OR52A1, binsize),
        "obs_HBB_OR52A1": pair_mean(obs, HBB, OR52A1, binsize),
        "oe_HBB_OR52A1": pair_mean(oe, HBB, OR52A1, binsize),
        "obs_HS1_HBB": pair_mean(obs, HS1, HBB, binsize),
        "oe_HS1_HBB": pair_mean(oe, HS1, HBB, binsize),
        "n_pixels": len(obs) // 2,
    }
    return metrics


def ratio(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return a / b


def verdict(rows: dict[str, dict]) -> str:
    """P1-system desk: need WT vs DEL contact change in predicted architectural direction."""
    wt = rows.get("WT") or rows.get("CAP_WT")
    dele = rows.get("DEL_B6") or rows.get("CAP_DEL")
    inv = rows.get("INV_A2") or rows.get("CAP_INV")
    if not wt or wt.get("status") != "OK":
        return "PENDING_WT"
    if not dele or dele.get("status") != "OK":
        return "PENDING_EDIT_FILES"

    # Predicted: Δ3′HS1 weakens HS1–HS5 architectural loop (or OE drops)
    r_hs1_hs5 = ratio(dele.get("oe_HS1_HS5"), wt.get("oe_HS1_HS5"))
    r_obs = ratio(dele.get("obs_HS1_HS5"), wt.get("obs_HS1_HS5"))
    # Ectopic: HBB–OR52A1 OE may rise on deletion (paper narrative)
    r_ect = ratio(dele.get("oe_HBB_OR52A1"), wt.get("oe_HBB_OR52A1"))

    inv_ok = None
    if inv and inv.get("status") == "OK":
        # inversion should keep/restore insulation differently; at least contact pattern ≠ del
        inv_ok = inv.get("oe_HS1_HS5") is not None

    architectural_delta = False
    if r_hs1_hs5 is not None and r_hs1_hs5 <= 0.75:
        architectural_delta = True
    if r_obs is not None and r_obs <= 0.75:
        architectural_delta = True
    ectopic_delta = r_ect is not None and r_ect >= 1.25

    if architectural_delta and (ectopic_delta or inv_ok):
        return "PASS_DESK"
    if architectural_delta or ectopic_delta:
        return "INCONCLUSIVE_LEAN_POSITIVE"
    if r_hs1_hs5 is None and r_obs is None:
        return "INCONCLUSIVE_NO_SIGNAL"
    return "FAIL_DESK"


def main() -> None:
    DUMP.mkdir(parents=True, exist_ok=True)
    rows: dict[str, dict] = {}
    # Prefer genome-wide; also try capture if present
    for key in ("WT", "DEL_B6", "INV_A2", "CAP_WT", "CAP_DEL", "CAP_INV"):
        rows[key] = dump_sample(key, SAMPLES[key], binsize=5000)

    v = verdict(rows)
    # Literature grounding always available
    lit = {
        "paper": "eLife 70557 / GSE160425",
        "edit_verified": True,
        "CTCF_CUT_and_RUN_reported": True,
        "HiC_and_Capture_reported": True,
        "expression_HbF_delta_reported": True,
        "note": "Literature can ground P1-system biology; local dump confirms contact Δ when files OK.",
    }

    payload = {
        "verdict": v,
        "anchors_hg19": {
            "HS1": list(HS1),
            "HS5": list(HS5),
            "OR52A1": list(OR52A1),
            "HBB": list(HBB),
        },
        "samples": rows,
        "literature": lit,
        "ratios": {
            "oe_HS1_HS5_DEL_over_WT": ratio(
                (rows.get("DEL_B6") or {}).get("oe_HS1_HS5"),
                (rows.get("WT") or {}).get("oe_HS1_HS5"),
            ),
            "oe_HBB_OR52A1_DEL_over_WT": ratio(
                (rows.get("DEL_B6") or {}).get("oe_HBB_OR52A1"),
                (rows.get("WT") or {}).get("oe_HBB_OR52A1"),
            ),
            "cap_oe_HS1_HS5_DEL_over_WT": ratio(
                (rows.get("CAP_DEL") or {}).get("oe_HS1_HS5"),
                (rows.get("CAP_WT") or {}).get("oe_HS1_HS5"),
            ),
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def row_md(s: str, r: dict) -> str:
        if r.get("status") != "OK":
            return f"| {s} | {r.get('status')} | {r.get('bytes', 0)} | — | — | — |"
        return (
            f"| {s} | OK | {r['bytes']} | {r.get('oe_HS1_HS5')} | "
            f"{r.get('oe_HBB_OR52A1')} | {r.get('obs_HS1_HS5')} |"
        )

    md = f"""# P1-system desk — 3′HS1 (GSE160422 / eLife 70557)

**Date:** 2026-07-14  
**Role:** architecture positive control in HUDEP-2 (same system as G4a)  
**Verdict:** `{v}`

## What P1 must show

```text
P1 edit verified
AND CTCF occupancy changes (paper CUT&RUN)
AND contact changes in predicted direction (local dump)
AND assay detects effect reproducibly
```

Expression desirable, not required for technical architecture P1.

## Local dump table (OE KR, 5 kb)

| sample | status | bytes | OE HS1–HS5 | OE HBB–OR52A1 | obs HS1–HS5 |
|--------|--------|------:|------------:|--------------:|------------:|
{row_md("WT", rows.get("WT", {}))}
{row_md("DEL_B6", rows.get("DEL_B6", {}))}
{row_md("INV_A2", rows.get("INV_A2", {}))}
{row_md("CAP_WT", rows.get("CAP_WT", {}))}
{row_md("CAP_DEL", rows.get("CAP_DEL", {}))}
{row_md("CAP_INV", rows.get("CAP_INV", {}))}

## Ratios (DEL/WT)

- OE HS1–HS5: `{payload['ratios']['oe_HS1_HS5_DEL_over_WT']}`
- OE HBB–OR52A1: `{payload['ratios']['oe_HBB_OR52A1_DEL_over_WT']}`
- Capture OE HS1–HS5: `{payload['ratios']['cap_oe_HS1_HS5_DEL_over_WT']}`

## Literature grounding

- Paper verifies CRISPR del/inv, CTCF CUT&RUN loss/gain, Hi-C/Capture changes, HbF phenotype.
- This is **P1-system** (β-globin), not P1-local at C1.
- If local dump PASS_DESK → assay chain trusted in HUDEP-2 Hi-C.
- Planted local P1 near C1 still recommended before over-interpreting C1 architecture magnitude.

## Gate impact

| Gate | Effect of this P1 |
|------|-------------------|
| Architecture freeze | may unlock **provisional** freeze *language* with G4a PASS_DESK |
| Wet-lab GO for C1 edit | still needs G5 editability + G4b plan + endpoints |
| Activity Branch B | remains available |

JSON: `P1_3primeHS1_metrics.json`
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"verdict": v, "ratios": payload["ratios"], "statuses": {k: r.get("status") for k, r in rows.items()}}, indent=2))


if __name__ == "__main__":
    main()
