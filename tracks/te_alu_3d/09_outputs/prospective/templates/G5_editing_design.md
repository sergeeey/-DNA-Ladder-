# G5 — Editing design sheet (DRAFT only — C1/C2)

**Status:** `DRAFT_DESK` / feasibility **HARD** for SpCas9 classic BE  
**Date:** 2026-07-14  
**No wet-lab GO.** No orders. No freeze.

```yaml
locus:
  chrom: chr11
  pos: 62753923
  genome_build: GRCh38
  te_family: AluSz
candidates:
  C1: {ref: A, alt: G, role: primary_M3_ranked}
  C2: {ref: A, alt: T, role: allelic_amplitude_control}
editing_strategy: prime_edit_preferred   # SpCas9 NGGbase-edit window FAIL
guides_SpCas9_NGG:
  - strand: "-"
    pam: CGG
    spacer: TGGCTAAGGGGCGGGACTTC
    edit_pos_in_spacer: 18
    in_BE_window_4_8: false
  - strand: "-"
    pam: GGG
    spacer: GGCTAAGGGGCGGGACTTCC
    edit_pos_in_spacer: 17
    in_BE_window_4_8: false
base_edit_ABE_for_C1_A_to_G: NOT_IN_WINDOW_4_8_with_found_PAMs
base_edit_for_C2_A_to_T: NOT_STANDARD_BE
prime_edit: REQUIRED_IF_EDIT
allele_discrimination_assay: amplicon_NGS_or_ddPCR
confounding_risks:
  promoter_motif: UNKNOWN
  splice_element: UNKNOWN
  autonomous_enhancer_activity: HIGH_PRIOR   # AG M3 lean POLR2/GABPB1
  Alu_off_target_homology: HIGH_PRIOR
feasibility: HARD
wet_lab_go: STOPPED
```

## Desk verdict

```text
G5: DRAFT_ONLY
SpCas9 BE: FAIL (edit positions 17–18, outside 4–8)
If future edit: prime editing + M5 neutrals + activity readout (not CTCF-first)
Still blocked: HUDEP-2 G4, G6–G9, wet-lab
```

Context:  
`c1_chip_tf_channel_unpack.md` · `c1_c2_channel_compare.md` · `g2_r4_shortlist.md`
