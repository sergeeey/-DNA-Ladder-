# G4 desk-pass v1 — WT contact readiness for L-HO_* (no alleles)

**Date:** 2026-07-14  
**Router:** R3 ALLOW (desk only) · Evidence: **E1–E2** · Independence: none (I5 N/A)  
**Status:** `LOCUS_CONTACT_READINESS` — **not** allele G4 PASS  
**Forbidden:** scoring `data/holdout/`, freezing E–P pairs from sealed alleles, wet-lab GO

---

## Decision (machine)

```text
G4_allele_E_P:     FAIL / UNFILLED   (no named V, E, P)
G4_locus_anchors:  PARTIAL_PASS      (HUDEP-2 CTCF peaks in-window)
G4_public_contact: PROXY_PARTIAL     (K562 ENCSR545YBD loops/domains; not HUDEP-2)
H4:                NOT YET
wet-lab:           STOPPED
```

---

## What was measured (desk)

Source: `pilot_scaffold/data/ctcf_HUDEP2_peaks.bed`  
Provenance: ChIP-Atlas SRX5821035 / GSE131055, hg38, chr11 slice (development CTCF context).

| Locus | Window (GRCh38) | CTCF peaks (n) | Top 100 kb bins (start, n) | Landmark genes (public, not claims) |
|-------|-----------------|----------------|----------------------------|-------------------------------------|
| L-HO_C | chr11:64–65 Mb | 41 | 64.2 Mb (8); 64.3 (7); 64.7 (6) | 11q13.1 / MEN1 neighborhood |
| L-HO_A | chr11:65–66 Mb | 48 | 65.5 Mb (8); 65.2 (6); 65.0 (5) | CAPN1 ~65.18–65.21 Mb; RELA / MAP3K11 vicinity |
| L-HO_B | chr11:67–68 Mb | 42 | 67.6 Mb (8); 67.3 (7); 67.2 (5) | GSTP1 / TCIRG1 neighborhood |

**Interpretation:** occupied erythroid CTCF anchors exist in all three sealed geography windows. That supports *future* M1 cultivation at these bins. It does **not** show any enhancer–promoter contact change or any variant effect.

---

## Public contact landscape (honest gap)

| Resource | Cell | Coverage of L-HO_* | Use for G4 |
|----------|------|--------------------|------------|
| HUDEP-2 Micro-Capture-C (e.g. GSE292671) | HUDEP-2 | Locus-focused (BCL11A, chr2) | **Cannot** fill L-HO_* E–P |
| HUDEP-2 Hi-C (β-globin papers) | HUDEP-2 | HBB / extended β locus (~5 Mb) | **Wrong window** (and HBB = development) |
| K562 in situ Hi-C ENCSR545YBD (loops/domains on disk) | K562 proxy | Genome-wide incl. 64–68 Mb | **PROXY_PARTIAL** — see `queue_B_proxy_hic_LHO_2026-07-14.md` |

```yaml
# Strict G4 (allele) remains empty
enhancer_E: { chrom: null, start: null, end: null, evidence: null }
promoter_P: { chrom: null, start: null, end: null, gene: null }
wt_contact:
  assay: null
  cell_state: HUDEP-2_required
  observed: UNKNOWN
  provenance_url_or_path: null
  reproducible: UNKNOWN
```

---

## Priority bins for future allele ranking (not frozen)

When a primary scorer is admitted, prefer search neighborhoods:

1. **L-HO_A** — densest CTCF; `chr11:65,500,000–65,600,000` (+ secondary `65.2 Mb` near CAPN1)  
2. **L-HO_C** — `chr11:64,200,000–64,400,000`  
3. **L-HO_B** — `chr11:67,600,000–67,700,000`

Still: alleles **UNKNOWN**; ranking **BLOCKED** without ARCHCODE / AlphaGenome admission.

---

## Differentiating tests needed next (not done)

| Test | Why | Blocker |
|------|-----|---------|
| Fetch/query genome-wide erythroid Hi-C for 64–68 Mb | Observe WT loops / TADs before naming E,P | Dataset choice + QC |
| Name E and P only after contact observed | Strict G4 | Allele + contact map |
| Capture-C / MCC baited to frozen E,P | I5 lab | G1–G9 PASS |

---

## Registry note

```text
observation: HUDEP-2 CTCF peaks dense in L-HO_A/B/C
supporting_artifact: 09_outputs/prospective/G4_contact_desk_pass_v1.md
alternative_explanations: density ≠ functional E–P loop; peaks may be non-looping
testable_prediction: after primary admission, ≥1 allele in top bins will sit in Alu/SVA within 250 bp of an occupied peak
disconfirming_test: zero rare TE-SNVs near peaks after QC; or no WT contact at named E–P in erythroid map
evidence_level: E1
status: PARTIAL / IMMATURE
expiry: review at next admission gate
```
