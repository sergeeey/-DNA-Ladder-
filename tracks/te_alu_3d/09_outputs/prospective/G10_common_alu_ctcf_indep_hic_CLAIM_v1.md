# G10 — Common Alu∩CTCF × independent HUDEP-2 Hi-C contact — CLAIM v1

**Pre-registration date:** 2026-07-24  
**L0 gate:** Descriptive  
**Status:** LOCKED — before Ensembl freeze / juicer dump / contact peek  
**Related:** Stage-3 G4a/G4c CLOSED; does **not** reopen A754/A518 or GSM4873113 rescue

---

## 1. Why G10

Stage-3 rare architecture contact on GSM4873113 / GSE201820 (same anchors) is CLOSED.
G10 tests a **different estimand** on **new anchors** drawn from the frozen G9c common
Alu∩CTCF panel, using **GSE201820** (independent of GSM4873113) as the contact matrix.

Not a rescue of G4a/G4c. Not allele-specific. Not regulatory/causal language.

---

## 2. Estimand

Among pre-declared common Alu∩CTCF SNVs (chr11, non-holdout), does WT-like HUDEP-2 Hi-C
(GSE201820 CTCF-AID **noIAA differentiated** merge) show elevated contact between the
containing CTCF peak (E) and the nearest protein-coding TSS window (P), relative to
exact-distance background (`bg_tol_bins=0`), at the Stage-3 pixel thresholds?

Cell-line note: GSE201820 is CTCF-AID noIAA control (not native WT GSM4873113).

---

## 3. Locked slot selection (deterministic, before any dump)

Source freeze (hash-verified at run): `g9c_common_alu_ctcf_panel_freeze_v1.json`

Filter:

1. `role == CASE_CTCF_ALU`
2. `chrom == chr11`
3. `pos` ∉ `{518575, 75445532}` (Stage-3 A518/A754 — excluded)
4. Exclude HBB `5.2–5.3 Mb` and holdout `64–68 Mb` (GRCh38)
5. Deduplicate by `(peak_start, peak_end)`: keep lexicographically smallest
   `(pos, ref, alt)` per peak
6. Sort by `(pos, ref, alt)`; take **first 4** peaks → slots `G10_01` … `G10_04`

No chromosome additions after this CLAIM. No peeking contact to choose slots.

---

## 4. Anchor definition (same family as Stage-3)

| Piece | Rule |
|-------|------|
| E | HUDEP-2 CTCF BED peak containing variant (`BED_start < pos ≤ BED_end`); peak from G9c freeze fields if consistent with BED |
| T | Nearest protein-coding TSS within ±1 Mb (Ensembl REST; strand-aware; ENSG tie-break) |
| P | TSS ± 2500 bp (1-based inclusive) |
| Map | GRCh38 → GRCh37 via Ensembl `/map`; single same-chrom mapping required |
| Failures | `BLOCKED_NO_CTCF_ANCHOR` / `BLOCKED_NO_ELIGIBLE_TSS` / `BLOCKED_MAP_FAILED` |

Holdout sealed: no dump region overlapping hg19 chr11:64–68 Mb.

---

## 5. Analysis

| Knob | Value |
|------|-------|
| Primary matrix | GSE201820 `noIAAdiff` remote `.hic` (same URL as G4c) |
| Secondary (info only) | GSE201820 `noIAAundiff` — reported, **excluded from panel verdict** |
| Norm / resolutions | KR; 10 kb and 25 kb |
| Background | **Primary `bg_tol_bins=0`**; tol=1 informational only |
| Pixel PASS | Same as Stage-3: obs present, focal_row_nonzero>0, bg_n≥20, enrich_mean≥1.5, obs_percentile≥0.75, OE≥1.2 |
| Slot verdict | `sample_verdict(res10, res25)` from `hic_contact_lib.py` |
| Panel PASS | Among slots with status OK after freeze: ≥50% (ceil) are PASS **and** ≥2 PASS |
| Panel REJECT | Among OK slots: 0 PASS and ≥2 FAIL |
| Else | INCONCLUSIVE |
| If OK slots &lt; 2 | INCONCLUSIVE `underpowered_freeze` (no contact fishing) |

Allowed language: contact-candidate only. Forbidden: architecture / regulatory / causal.

---

## 6. Forbidden

- Re-analysis of A754/A518 or GSM4873113 Stage-3 dumps  
- Changing thresholds / tol / panel rules after results  
- Unsealing holdout / wet GO / oligo order  
- Rewriting G4a/G4c/G9* verdicts  

---

## 7. Artifacts

- `G10_common_alu_ctcf_indep_hic_CLAIM_v1.md` (this file)  
- `g10_common_alu_ctcf_anchor_freeze_v1.json` (+ sha256)  
- `g10_common_alu_ctcf_indep_hic_v1.json`  
- `G10_common_alu_ctcf_indep_hic_decision_v1.md`  
- Scripts: `freeze_g10_common_alu_ctcf_anchors.py`, `run_g10_common_alu_ctcf_indep_hic.py`
