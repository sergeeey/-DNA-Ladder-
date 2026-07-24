# Stage-3 Architecture WT Contact — Independent-Source Replication CLAIM v1

**Pre-registration date:** 2026-07-21
**L0 gate:** Descriptive
**Status:** LOCKED — written before any matrix access, network preflight, or juicer dump
**Supersedes:** none (new claim; parallel to G4a_stage3_architecture_wt_contact_CLAIM_v1.md)
**Related:** `G4a_stage3_architecture_wt_contact_CLAIM_v1.md`,
             `G4a_stage3_architecture_wt_contact_decision_v1.md`,
             `G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_CLAIM_v1.md`

---

## 1. Estimand

**Measure:** Contact(anchor\_ctcf, anchor\_tss) in CTCF-AID HUDEP-2 noIAA cells (active CTCF)

**Population / data source:** GSE201820, two merged Hi-C files:
- `GSE201820_hic_merge_cloneC16_C3noIAAdiff.inter_30.hic` (differentiated state)
- `GSE201820_hic_merge_cloneC16_C3noIAAundiff.inter_30.hic` (undifferentiated state)

Both files: CTCF-AID HUDEP-2, noIAA treatment (= active CTCF), clones C16+C3 merged,
hg19 genome, KR normalisation, MAPQ >= 30.
Remote access via NCBI FTP (no local download of full .hic files).

**Estimand type:** Descriptive — does a second, independently-generated Hi-C dataset
(different GEO series, different cell clones, different experimental timeline) support
elevated contact frequency at the same pre-frozen anchors, relative to same-distance
background, at the pre-registered thresholds?

**NOT being tested:**
- Enhancer–promoter contact (no transcription claim)
- Target-gene identification or expression effect
- Allele-specific contact change (ALT vs REF)
- Regulation or pathogenicity of the variant
- Stage-3 reassignment (outcomes do not alter slot assignments)
- Allele-effect comparison between differentiated and undifferentiated

---

## 2. Locked slots (reused from G4a freeze, GRCh38)

| Slot ID | Candidate | Variant (GRCh38) | Anchors source |
|---------|-----------|-----------------|----------------|
| ARCH_01 | A754 | chr11:75445532:G:A | stage3_architecture_anchor_freeze_v1.json |
| ARCH_02 | A518 | chr11:518575:C:A | stage3_architecture_anchor_freeze_v1.json |

Source: `stage3_architecture_anchor_freeze_v1.json` (frozen 2026-07-21, SHA256 on disk).
**No anchor recomputation.** Anchors are reused verbatim; any Ensembl REST access is
forbidden for this experiment (anchors already frozen).
Holdout: SEALED — not accessed, not unblinded, no change.

---

## 3. Anchor coordinates (copied from freeze, no recomputation)

### ARCH_01 (A754)
- E_grch37: chrom=11, start=75156315, end=75156841
- P_grch37: chrom=11, start=75141748, end=75146748
- focal_row_coord (1-based): 75156578

### ARCH_02 (A518)
- E_grch37: chrom=11, start=518575, end=519098
- P_grch37: chrom=11, start=504895, end=509895
- focal_row_coord (1-based): 518836

---

## 4. Analysis protocol

**Data URLs (fixed, no fallback):**
```
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/GSE201820_hic_merge_cloneC16_C3noIAAdiff.inter_30.hic
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE201nnn/GSE201820/suppl/GSE201820_hic_merge_cloneC16_C3noIAAundiff.inter_30.hic
```

**Tool:** juicer_tools.jar dump, `observed KR` and `oe KR`, BP units
**Resolutions:** 10 000 bp and 25 000 bp
**Dump region:** chr11 spanning min(E_start, P_start) − 500 000 to max(E_end, P_end) + 500 000
(hg19), clamped to ≥ 0; same region as G4a dump.
**Library:** `hic_contact_lib.py` pure functions, unmodified.

**Remote preflight (mandatory before any dump):**
1. HTTP HEAD: URL reachable, Content-Length > 0, Accept-Ranges: bytes
2. HTTP GET Range: bytes=0-3: status 206, bytes[0:3] == b"HIC"
If any check fails → **BLOCKED**; runner exits immediately. No fallback, no alternative URL.

**Primary background tolerance:** `bg_tol_bins=0` (exact-distance background only).
This is the primary analysis; the bg_tol_bins=1 result is shown as informational and
**excluded from the verdict**.

**Reason for primary=0:** G4a bg_tol_bins=0 sensitivity showed that the tol=1 background
(used in G4a primary) mixes 0/1/2-bin distances, inflating bg_n and compressing enrich_mean.
This experiment applies the stricter, unambiguous exact-distance definition from the outset.

---

## 5. Decision rule (pre-registered, per resolution, per slot, per sample)

### Resolution-level score (unchanged from G4a)

```
PASS if ALL:
  primary_obs is not None
  focal_row_nonzero > 0
  bg_n >= 20
  enrich_mean >= 1.5
  obs_percentile >= 0.75
  OE >= 1.2

UNRESOLVED_SAME_BIN if E_mid_bin == P_mid_bin
INSUFFICIENT_BG if bg_n < 20 (regardless of other metrics)
FAIL otherwise
```

### Sample-level slot verdict (per sample: diff or undiff)

Same mapping as G4a `sample_verdict`:
| 10 kb | 25 kb | Slot-sample verdict |
|-------|-------|---------------------|
| PASS | PASS | **PASS** |
| INSUFFICIENT_BG or UNRESOLVED_SAME_BIN (either) | — | **INCONCLUSIVE** |
| FAIL | FAIL | **UNSUPPORTED** |
| ≥1 PASS, other non-INSUFFICIENT | — | **PARTIAL** |
| other | — | **INCONCLUSIVE** |

### Cross-sample slot verdict (combining diff + undiff for one slot)

| diff verdict | undiff verdict | Slot verdict |
|-------------|----------------|--------------|
| PASS | PASS | **REPLICATION_PASS** |
| PASS | PARTIAL or UNSUPPORTED | **REPLICATION_PARTIAL** |
| PARTIAL | PASS | **REPLICATION_PARTIAL** |
| UNSUPPORTED | UNSUPPORTED | **REPLICATION_UNSUPPORTED** |
| either INCONCLUSIVE | — | **REPLICATION_INCONCLUSIVE** |
| other | — | **REPLICATION_PARTIAL** |

### Panel-level verdict (both slots)

| Condition | Panel verdict |
|-----------|---------------|
| Both slots REPLICATION_PASS | REPLICATION_SUPPORTED |
| ≥1 slot REPLICATION_PASS, ≥1 not | REPLICATION_PARTIAL |
| Both slots REPLICATION_UNSUPPORTED | REPLICATION_UNSUPPORTED |
| ≥1 REPLICATION_INCONCLUSIVE, none PASS | REPLICATION_INCONCLUSIVE |
| ≥1 slot BLOCKED | BLOCKED |

### No-upgrade invariant (mandatory)

A G4c verdict of REPLICATION_PASS or REPLICATION_SUPPORTED does **NOT** upgrade
the G4a panel verdict (INCONCLUSIVE). Stage-3 slot assignments remain LOCKED.
G4c informs independent replication only; causal/regulatory language is forbidden
regardless of G4c outcome.

---

## 6. Fail-closed invariants

- **Hash chain:** freeze hash → eligibility freeze hash → preflight hash → dump hashes → result.
  Runner verifies each link before the next step.
- **Same-bin guard:** if E_mid_bin == P_mid_bin at primary bg_tol_bins=0, score is
  `UNRESOLVED_SAME_BIN`; verdict is `INCONCLUSIVE`. Computation is not attempted.
- **No-upgrade:** G4c result cannot strengthen G4a panel verdict.
- **No fallback:** if remote preflight or juicer dump fails, outcome is BLOCKED.
  Runner writes BLOCKED to the result JSON and exits. No improvisation.
- **Holdout guard:** any path or URL containing the literal string "holdout" is rejected.
- **Sealed region guard:** no dump region overlapping chr11:64,000,000–68,000,000 (hg19).

---

## 7. Scope constraints

- allele_effect: NOT_TESTED
- G4b allele ΔContact: NOT_TESTED
- wet-lab: NO_GO (B0 unsigned; user confirmed desk-only 2026-07-21)
- Language: outcome may not use "regulatory", "pathogenic", "causal",
  "enhancer–promoter", or "target gene" phrasing.
- tol=1 informational output: labelled "informational only — excluded from verdict" in
  all result and decision files.

---

## 8. Novelty check

This is within-project independent-source replication of G4a. It uses:
- A different GEO series (GSE201820 vs GSE160422)
- A different cell clone set (C16+C3 vs single replicate)
- A different experimental condition (CTCF-AID noIAA vs wild-type Hi-C)

No claim of independent discovery. Novelty is in replication evidence, not the hypothesis.
If G4c replicates G4a contact signals in a cell type with confirmed active CTCF but
distinct chromatin state, that strengthens but does not prove the G4a contact call.

---

## 9. GEO eligibility

Verified from GEO metadata before writing this CLAIM:
- GSE201820: "Hi-C analysis of CTCF-AID HUDEP2 cells"
- noIAA condition: CTCF fully active (no degradation)
- C16/C3: two independent HUDEP-2 clones, merged replicates
- Genome: hg19 (confirmed from GEO record + file naming convention)
- File suffix `inter_30`: MAPQ >= 30, all contact types
- Differentiated (erythroid) and undifferentiated (progenitor) states

Full metadata recorded in `G4c_stage3_architecture_replic_eligibility_v1.json`.
