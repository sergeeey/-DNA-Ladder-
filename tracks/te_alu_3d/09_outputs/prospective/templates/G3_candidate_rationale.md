# G3 — Candidate rationale



**Status:** `PARTIAL` for R4 shortlist C1–C3 — see  

`09_outputs/prospective/G3G4_r4_shortlist_desk_pass_v1.md`  

**Do not fill from:** HBB enrichment outcomes, holdout scores, ClinVar labels.



```yaml

candidate_id: C1   # preferred; also C2 (same site), C3 (second locus)

variant:

  chrom: chr11

  pos: 62753923

  ref: A

  alt: G

  genome_build: GRCh38

mechanism_class: M1

direct_molecular_endpoint: CTCF_occupancy_or_CHIP_TF_delta_at_anchor

competing_mechanisms: [M3, M4, M5]

discriminating_predictions:

  - M1_vs_M3: occupancy vs activity without CTCF loss

  - M5: independent edits + neutrals

cell_state: HUDEP-2

notes: >

  Named from leakage-free AG contact-Δ R4 panel (non-holdout).

  E/P provisional from K562 proxy only; G9 not frozen.

```


