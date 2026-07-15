# Queue B — proxy contact map for L-HO_* (K562 Hi-C)

**Date:** 2026-07-14  
**Status:** `PROXY_PARTIAL` — closes genome-wide **gap** for desk G4 prep; does **not** PASS strict HUDEP-2 allele G4  
**Evidence:** E1–E2 · Independence: public ENCODE (I3 dataset) · Cell mismatch → not I5  

---

## Decision

```text
genomewide_proxy_at_64_68Mb:  PASS (data on disk)
strict_G4_HUDEP2_E_P:         FAIL / UNKNOWN (cell-state mismatch)
allele_freeze:                BLOCKED (needs Queue A)
```

---

## Provenance

| Field | Value |
|-------|-------|
| Experiment | ENCODE `ENCSR545YBD` — K562 in situ Hi-C |
| Assembly | GRCh38 |
| Loops | `ENCFF693XIL`, `ENCFF134HIZ` (bedpe.gz) |
| Contact domains | `ENCFF173VDJ` (preferred bedpe.gz) |
| Local path | `pilot_scaffold/data/hic_proxy/` |
| Summary JSON | `pilot_scaffold/data/hic_proxy/l_ho_proxy_contact_summary.json` |
| Full .hic | **not downloaded** (~20 GB) — loops/domains sufficient for desk |

**Caveat:** K562 ≠ HUDEP-2. Use as geography prior for *where contacts exist*, not as wet-lab WT proof.

---

## Hits intersecting L-HO_* ± HUDEP-2 CTCF (±5 kb)

From preferred loops `ENCFF693XIL` (primary desk table):

| Locus | Loops with ≥1 anchor in window | Both anchors in window | Both anchors near HUDEP-2 CTCF |
|-------|--------------------------------|------------------------|--------------------------------|
| L-HO_C (64–65 Mb) | 8 | 6 | 7 |
| L-HO_A (65–66 Mb) | 10 | 7 | 7 |
| L-HO_B (67–68 Mb) | 21 | 7 | 10 |

Domains (`ENCFF173VDJ`): all three windows have contact domains with both ends inside the Mb and near HUDEP-2 CTCF peaks (C:8, A:9, B:5).

**Interpretation:** L-HO geography is not “empty chromatin” under a hematopoietic Hi-C proxy. Local loop/domain structure exists and aligns with our HUDEP-2 CTCF density bins. This upgrades G4 *locus readiness* from GAP → **PROXY_PARTIAL**.

---

## Example high-priority proxy pairs (not frozen E–P)

See JSON `windows.*.loops.top` for coordinates. Prefer pairs where:

```text
both_anchors_in_window = true
AND a_near_HUDEP2_CTCF AND b_near_HUDEP2_CTCF
```

These become **candidate E/P scaffolds** only after:

1. Queue A primary admission  
2. Allele ranking without holdout leakage  
3. Optional HUDEP-2 / erythroid Capture-C validation of the same pair  

---

## Explicit non-claims

- No allele V selected  
- No confirmatory enrichment  
- No “3D disruption”  
- No unblind  
- No wet-lab GO  

---

## Next if credentials arrive

```text
Queue A PASS → rank alleles in Alu/SVA near these loop anchors
→ fill allele G4 with named E,P from validated assay
→ G3–G9 freeze ≤3
```
