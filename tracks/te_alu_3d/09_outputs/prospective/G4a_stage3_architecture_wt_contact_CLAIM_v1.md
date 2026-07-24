# Stage-3 Architecture WT Contact Qualification — CLAIM v1

**Pre-registration date:** 2026-07-21  
**L0 gate:** Descriptive  
**Status:** LOCKED — do not edit after analysis begins  
**Supersedes:** none (new claim)  
**Related:** `G4a_gsm4873113_desk_pass_v1.md`, `G4a_multisample_kill_test_v1.md`  

---

## 1. Estimand

**Measure:** Contact(anchor\_ctcf, anchor\_tss) in WT HUDEP-2

**Population / data source:** GSE160422 GSM4873113 (WT HUDEP-2 genome-wide Hi-C), KR
normalisation, 10 kb and 25 kb resolution.  
**Estimand type:** Descriptive — does the observed Hi-C matrix support elevated contact frequency
between the CTCF anchor bin and the TSS anchor bin relative to same-distance background, at the
specified thresholds?  

**NOT being tested:**
- Enhancer–promoter contact (no transcription claim)
- Target-gene identification or expression effect
- Allele-specific contact change (ALT vs REF)
- Regulation or pathogenicity of the variant
- Stage-3 reassignment (outcomes do not alter slot assignments)

---

## 2. Locked slots (non-holdout, GRCh38)

| Slot ID | Candidate | Variant (GRCh38) | Registry key |
|---------|-----------|-----------------|--------------|
| ARCH_01 | A754 | chr11:75445532:G:A | architecture_strong_1 |
| ARCH_02 | A518 | chr11:518575:C:A | architecture_strong_2 |

Source: `prospective_panel_registry_v1.yaml` `stage3_slot_assignments` (locked 2026-07-15).  
Holdout: SEALED — not accessed, not unblinded, no change.

---

## 3. Deterministic anchor definition (FROZEN before analysis)

### E — CTCF anchor

Source BED: `pilot_scaffold/data/ctcf_HUDEP2_peaks.bed` (ChIP-Atlas SRX5821035, hg38)  
Rule: the unique HUDEP-2 CTCF peak where `BED_start < variant_pos_1based <= BED_end`
(half-open BED convention; 1-based variant position).  
If zero peaks satisfy this condition → slot status `BLOCKED_NO_CTCF_ANCHOR`.  
If >1 peaks satisfy → take the peak with the widest score; if score tied → take
lexicographically smaller peak ID.

### T — nearest protein-coding TSS

Source: Ensembl REST `/overlap/region/human/{chr}:{start}-{end}?feature=gene;biotype=protein_coding`
restricted to ±1 Mb of the variant position (GRCh38).  
Response and Ensembl release (`/info/data`) cached under
`09_outputs/prospective/stage3_architecture_anchor_cache/` and SHA256-hashed.

TSS definition (strand-aware, 1-based Ensembl coordinates):
- `+` strand gene: TSS = `gene['start']`
- `−` strand gene: TSS = `gene['end']`

Selection: nearest TSS by `abs(TSS − variant_pos_1based)`; tie-break ascending ENSG ID.  
Window: P = (TSS − 2500, TSS + 2500) in 1-based coordinates (inclusive).  
If no protein-coding gene found within ±1 Mb → slot status `BLOCKED_NO_ELIGIBLE_TSS`.

### Coordinate mapping (GRCh38 → GRCh37)

Endpoint: Ensembl REST `/map/human/GRCh38/{chr}:{start}..{end}/GRCh37`  
Requirement: single mapped region on the same chromosome.  
If mapping fails or maps to multiple/different chromosomes → slot status `BLOCKED_MAP_FAILED`.  
Hi-C analysis uses GRCh37 (hg19) coordinates throughout.

### FORBIDDEN access

- Any path containing the literal string `holdout`  
- Any GRCh38 E/P window that overlaps the sealed interval chr11:64,000,000–68,000,000  
- Any GRCh37 dump region that overlaps chr11:64,000,000–68,000,000 (approximate hg19 equivalent
  of the sealed locus)

---

## 4. Analysis

**Dataset:** GSM4873113 WT HUDEP-2, local `.hic` at
`D:\DNK - 2\data\HUDEP2_GSE160422\GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic`  
**Tool:** juicer_tools.jar dump, `observed KR` and `oe KR`, BP units  
**Resolutions:** 10 000 bp and 25 000 bp  
**Dump region:** chr11 spanning min(E_mid, P_mid) − 500 000 to max(E_mid, P_mid) + 500 000
(hg19), clamped to 0; chromosome boundary clamped as needed.  
**Library:** `hic_contact_lib.py` pure functions; no modification of existing G4a scripts.

**Dump freshness guard:** generated dump files must have `mtime > freeze_json mtime`; if stale,
recompute.

---

## 5. Decision rule (pre-registered, per resolution, per slot)

### Resolution-level score (PASS / INSUFFICIENT_BG / FAIL)

```
PASS if ALL:
  primary_obs is not None
  focal_row_nonzero > 0
  bg_n >= 20
  enrich_mean >= 1.5
  obs_percentile >= 0.75
  OE >= 1.2

INSUFFICIENT_BG if bg_n < 20 (regardless of other metrics)
FAIL otherwise
```

### Slot verdict

| 10 kb | 25 kb | Slot verdict |
|-------|-------|--------------|
| PASS | PASS | **PASS** |
| INSUFFICIENT_BG (either) | — | **INCONCLUSIVE** (inadequate background) |
| FAIL | FAIL | **UNSUPPORTED** |
| ≥1 PASS, other non-INSUFFICIENT | — | **PARTIAL** |
| other | — | **INCONCLUSIVE** |

### Panel-level verdict (both slots)

| Condition | Panel verdict |
|-----------|---------------|
| Both slots PASS | SUPPORTED |
| ≥1 slot PASS, ≥1 not PASS | PARTIAL |
| Both slots UNSUPPORTED | PANEL_UNSUPPORTED |
| ≥1 slot INCONCLUSIVE, none PASS | INCONCLUSIVE |
| ≥1 slot BLOCKED | BLOCKED (retain pre-reg outcome for that slot) |

**No Stage-3 slot reassignment regardless of outcome.**

---

## 6. Scope constraints

- allele_effect: NOT_TESTED (G4b not in scope here)
- G4b allele ΔContact: NOT_TESTED
- wet-lab: NO_GO (B0 unsigned; user confirmed desk-only 2026-07-21)
- Language constraint: outcome may not use "regulatory", "pathogenic", "causal",
  "enhancer–promoter", or "target gene" phrasing.

---

## 7. Novelty check

Local library searched: no exact match found (closest is the C1/G4a analysis which tests a
different locus, different estimand anchors, and different stage).  
Literature concern: GSE160422 (Antoniani et al. 2022) focuses on β-globin locus.  
This experiment tests chr11:75Mb and chr11:518kb — independent of the β-globin window.  
Classification: **within-project replication** extending G4a Stage-2 methodology to two
pre-registered Stage-3 architecture candidates.  
No claim of independent discovery.

---

## 8. Post-analysis integrity amendment (2026-07-21)

This section was added **after** the first result and does not alter anchors,
thresholds, or observed values.

The original rule omitted the case where E and P resolve to the same matrix
bin. A diagonal self-bin cannot discriminate contact between two distinct
anchors. Therefore:

- if `E_mid_bin == P_mid_bin`, resolution score is
  `UNRESOLVED_SAME_BIN`;
- any slot containing that score is `INCONCLUSIVE`;
- it must not be labelled `FAIL` or `UNSUPPORTED`.

This correction applies to A518 at 25 kb. The original result is retained in
version history; the corrected decision must identify this amendment.

The original implementation used `bg_tol_bins=1`, inherited from the C1 G4a
method but not stated explicitly in §4. For anchors separated by only one bin,
that background includes diagonal, one-bin, and two-bin pixels. This is a
conservative but heterogeneous near-diagonal comparison and must be reported as
a caveat; exact-distance (`bg_tol_bins=0`) results may be shown only as a
post-analysis sensitivity check.

Coordinate audit also found that the CTCF BED start is 0-based while Ensembl
REST mapping is 1-based inclusive. The freeze implementation is corrected to
map `BED_start + 1 .. BED_end`. This one-base correction is mechanical, does not
change anchor selection, and is applied before regenerating the corrected
freeze/result artifacts.
