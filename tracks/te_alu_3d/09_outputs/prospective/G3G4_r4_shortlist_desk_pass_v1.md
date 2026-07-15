# G3/G4 desk-pass — R4 AlphaGenome shortlist (v2, n=12 panel)

**Date:** 2026-07-14  
**Status:** `DESK_PARTIAL` · Evidence E1–E2 · Decision **IMMATURE** (not G9)  
**Router:** R4 ALLOW · Holdout SEALED / unscored  
**Panel:** `run_ag_cultivation_r4.py --max-score 12` → 6 CTCF×Alu peaks  

---

## Machine decision

```text
G1 leakage path:     assumed OK for this panel (no ClinVar/VEP in rank features)
G2 vs motif/distance: DONE (prep) — see `g2_r4_shortlist.md`
G3 candidate fill:   PARTIAL (V named; E/P provisional from K562 proxy)
G4 allele WT contact: PROXY_PARTIAL (K562 loops; not HUDEP-2)
G5–G9:               EMPTY
wet-lab:             STOPPED
```

---

## Updated shortlist (after n=12)

| ID | Variant | AG contact MAE | CHIP_TF MAE | TE | Peak mid | Neighborhood (desk) |
|----|---------|---------------:|------------:|----|----------|---------------------|
| **C1** | `chr11:62753923:A:G` | 0.0049 | 0.541 | AluSz | 62,754,214 | ~SLC22A organic-anion cluster (SLC22A8 ~62.99 Mb) |
| **C2** | `chr11:62753923:A:T` | 0.0021 | 0.255 | AluSz | same locus | allelic alternate at same site |
| **C3** | `chr11:72434037:C:T` | 0.0016 | 0.271 | AluSx1 | 72,434,361 | ARAP1–FCHSD2 neighborhood (11q13.4) |

Prior v1 top (`57568168` / CTNND1 neighborhood) drops out of top-3 after broader sampling — keep as **watchlist W1**.

---

## G3 — candidate rationale (filled)

### C1 — preferred cultivation head

```yaml
candidate_id: C1
variant:
  chrom: chr11
  pos: 62753923
  ref: A
  alt: G
  genome_build: GRCh38
  af_gnomad: 6.86e-7
  te_family: AluSz
mechanism_class: M1   # preferred default
direct_molecular_endpoint: CTCF_occupancy_or_CHIP_TF_delta_at_anchor
competing_mechanisms: [M3, M4, M5]
discriminating_predictions:
  - M1: allele-specific CTCF/RAD21 Δ matches contact-loop Δ at proxy pair
  - M3: CHIP_TF / activity Δ without CTCF occupancy loss
  - M4: nearby gene expression/splice Δ without contact change
  - M5: replicate edit + neutral controls null
cell_state: HUDEP-2_intended
ag_scores:
  contact_mae_all: 0.00494
  chip_tf_mae: 0.5408
notes: >
  Highest AG contact + TF delta in n=12 panel. Same site as C2 (allele branch).
  E/P not frozen — see G4 proxy loop below.
```

### C2 — allele competitor at same site

```yaml
candidate_id: C2
variant: {chrom: chr11, pos: 62753923, ref: A, alt: T, genome_build: GRCh38}
mechanism_class: M1
competing_mechanisms: [M3, M5]
notes: Same anchor as C1; use as allelic contrast / M5-adjacent control before freeze.
```

### C3 — second locus

```yaml
candidate_id: C3
variant:
  chrom: chr11
  pos: 72434037
  ref: C
  alt: T
  genome_build: GRCh38
  te_family: AluSx1
mechanism_class: M1
competing_mechanisms: [M3, M4, M5]
direct_molecular_endpoint: CTCF_occupancy_delta
ag_scores:
  contact_mae_all: 0.00162
  chip_tf_mae: 0.2714
notes: >
  Near ARAP1–FCHSD2. Strong CHIP_TF relative to contact — M3 competitor important.
```

---

## G4 — WT contact (proxy)

Cell mismatch: K562 ENCODE `ENCSR545YBD` loops ≠ HUDEP-2. **Fails strict G4.**  

### C1/C2 locus (~62.75 Mb)

| Proxy loop anchors | Span | d(min) to allele |
|--------------------|-----:|-----------------:|
| `62,390–62,395 kb` ↔ `62,690–62,695 kb` | 300 kb | ~61 kb |
| `62,375–62,400 kb` ↔ `62,850–62,875 kb` | 475 kb | ~109 kb |

Provisional **E/P scaffolds** (not frozen):

```yaml
enhancer_E: {chrom: chr11, start: 62390000, end: 62395000, evidence: K562_loop_ENCFF693XIL}
promoter_P: {chrom: chr11, start: 62690000, end: 62695000, evidence: K562_loop_ENCFF693XIL}
wt_contact:
  assay: Hi-C_loops
  cell_state: K562_proxy_not_HUDEP2
  observed: PROXY_YES
  reproducible: UNKNOWN
```

### C3 locus (~72.43 Mb)

| Proxy loop anchors | Span | d(min) |
|--------------------|-----:|-------:|
| `72,025–72,030 kb` ↔ `72,430–72,435 kb` | 405 kb | ~1.5 kb |
| `71,575–71,600 kb` ↔ `72,425–72,450 kb` | 850 kb | ~3.5 kb |

```yaml
enhancer_E: {chrom: chr11, start: 72025000, end: 72030000, evidence: K562_loop}
promoter_P: {chrom: chr11, start: 72430000, end: 72435000, evidence: K562_loop}
wt_contact:
  assay: Hi-C_loops
  cell_state: K562_proxy_not_HUDEP2
  observed: PROXY_YES
```

---

## G2 snapshot (2026-07-14)

| ID | Motif-only | Δlogodds | AG contact | Arm lean |
|----|-----------:|---------:|-----------:|----------|
| C1 | 0.065 | −4.09 (motif gain) | 0.0049 | **ARM_B AG ≫ motif** |
| C2 | 0.065 | −4.09 | 0.0021 | ARM_B AG ≫ motif |
| C3 | 0.870 | +4.09 (motif loss) | 0.0016 | ARM_B motif ≫ AG |

### Channel unpack (C1)

Top local CHIP_TF Δ = POLR2 / GABPB1 / RBFOX2. CTCF/RAD21 best ≈ rank **476/1617**.  
→ **M3 activity lean**; do not freeze C1 as M1 CTCF-anchor on AG alone.

C1 remains preferred *ranked* head but **mechanism class shifts toward M3** pending occupancy assay.  
C3 remains motif-driven competitor.

---

## Discriminators before any freeze

1. ~~Motif PWM Δ at C1/C3~~ → done (`g2_r4_shortlist.md`)  
2. ~~CHIP_TF channel unpack (C1)~~ → done (`c1_chip_tf_channel_unpack.md`) — M3 lean  
3. Arm A/B documented above  
4. Optional Capture-C bait on provisional E/P only after G5 editability  
5. If architecture claim: CTCF occupancy Δ (AG does not currently support as primary channel)  

---

## Explicit non-claims

```text
NO wet-lab GO
NO holdout unblind
NO confirmatory enrichment
NO 3D disruption claim
NO G9 freeze
```

Artifacts: `ag_cultivation_r4_report.json` (n=12), this file.
