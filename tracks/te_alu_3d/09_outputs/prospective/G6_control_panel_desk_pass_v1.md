# G6 — Control panel desk-pass v1 (C1-centric M3)

**Date:** 2026-07-14  
**Status:** `DESK_DRAFT` · `panel_frozen: false`  
**Wet-lab:** STOPPED  
**Holdout:** SEALED / not scored  

Refs: `ag_cultivation_r4_scores.tsv`, `c1_c2_channel_compare.md`, `g2_r4_shortlist.md`, `G5_editability_desk_pass_v1.md`

---

## Machine decision

```text
G6: DESK_DRAFT (not frozen)
panel_size: smaller_feasibility_panel (justified below)
architecture_positive_P1: DEFERRED (no validated CTCF/loop wet control in-repo)
motif_positive_proxy: C3 (PWM loss) — NOT architecture P1
wet_lab_go: STOPPED
NO_GO_FOR_WET_LAB: G4 HUDEP-2 FAIL + G5 HARD + G6 unfrozen
```

---

## Why a smaller / incomplete panel is allowed now

| Requirement (full G6) | Now |
|-----------------------|-----|
| 3 candidates | **YES** — C1, C2, C3 named |
| 3 matched neutrals | **YES** — N1–N3 from AG-low panel alleles (desk IDs) |
| 1 positive architecture control | **NO** — deferred; C3 is motif-loss proxy only |
| panel_frozen | **false** |

Justification: until a validated erythroid CTCF/loop-edit positive exists, freezing a fake architecture P1 would be rigor theater. This desk panel is for **design**, not GO.

---

## Manifest (draft)

```yaml
panel_frozen: false
frozen_at: null
role: cultivation_M3_primary_with_motif_competitor
cell_state_intended: HUDEP-2
genome_build: GRCh38

candidates:
  - id: C1
    variant_id: chr11:62753923:A:G
    role: primary_ranked_M3
    ag_contact_mae: 0.00494
    ag_chip_tf_mae: 0.541
    g2: ARM_B_AG_gt_motif
    channel_lean: M3_activity
  - id: C2
    variant_id: chr11:62753923:A:T
    role: allelic_amplitude_control_same_site
    ag_contact_mae: 0.00206
    ag_chip_tf_mae: 0.255
    channel_lean: M3_activity_shared_with_C1
  - id: C3
    variant_id: chr11:72434037:C:T
    role: motif_competitor_not_architecture_claim
    ag_contact_mae: 0.00162
    motif_only: 0.870
    g2: ARM_B_motif_gt_AG

matched_neutrals:
  # After GC+K562 ATAC amendment (g6_matching_amendment.md):
  - id: N3
    variant_id: chr11:108009167:T:C
    te_family: FLAM_C
    status: KEEP
    gc_match_grade: TIGHT
    access_match_vs_C1: MATCH
  - id: N1
    variant_id: chr11:35821778:C:G
    status: DROP
    reason: GC_POOR_and_ATAC_MISMATCH
  - id: N2
    variant_id: chr11:35822097:A:T
    status: DROP
    reason: GC_POOR
# N1/N2 slots open — reselect TE-SNVs with |ΔGC|<=0.05 and ATAC MATCH vs C1

positive_control:
  architecture_P1:
    status: DEFERRED
    reason: no validated HUDEP-2 CTCF/loop disruption allele in-repo
  motif_proxy_P_motif:
    id: C3
    note: high PWM disruption — use only as motif-loss comparator, never as 3D proof

matching_axes:
  locus_neighborhood: PARTIAL   # N1/N2 shared peak; N3 distant
  substitution_type: PARTIAL
  dist_to_E_P: UNKNOWN          # E/P proxy only
  gc: PARTIAL_DONE              # see g6_matching_amendment.md
  accessibility: PROXY_K562_ATAC
  baseline_ctcf_occupancy: PARTIAL  # all near HUDEP-2 peaks by construction
  editability: HARD_for_C1_C2       # G5 SpCas9 BE FAIL

replacement_after_outcome_view: FORBIDDEN
```

### Matching amendment (2026-07-14)

See `g6_matching_amendment.md` (ENCODE `ENCFF055NNT` K562 ATAC + Ensembl GC).  
**N3 KEEP**; **N1/N2 DROP**. ATAC is proxy (≠ HUDEP-2).

---

## Intended contrasts (if ever executed)

| Contrast | Tests |
|----------|-------|
| C1 vs C2 | Allele amplitude of shared M3 program |
| C1 vs N1/N2/N3 | Specificity vs low-AG TE-SNVs |
| C1 vs C3 | Activity/contact lean vs motif-loss lean |
| C1 vs architecture_P1 | Only after P1 exists — M1 vs M3 discriminator |

Primary readout if edited (from channel unpack): **activity / RNAPII-related**, not CTCF-first.  
Contact assay: secondary / only after HUDEP-2 G4.

---

## What still fails before freeze

| Gate | Status |
|------|--------|
| G1 | OK path (no ClinVar in rank) — re-audit at freeze |
| G2 | PREP done |
| G3 | PARTIAL (M3 preferred for C1; was M1 default) |
| G4 | PROXY only (K562) — **FAIL strict** |
| G5 | HARD — **FAIL classic BE** |
| G6 | DESK_DRAFT — **not frozen**; architecture P1 missing |
| G7–G9 | EMPTY |

```text
NO_GO_FOR_WET_LAB = true
```

---

## Next desk options (no lab)

1. Match GC/accessibility for N1–N3 (public tracks)  
2. Catalog non-SpCas9 PAMs for C1 BE  
3. Pause — bottleneck is HUDEP-2 G4 + real P1  

Template mirror: `templates/G6_control_panel.yaml`
