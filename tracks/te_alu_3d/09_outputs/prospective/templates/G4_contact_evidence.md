# G4 — Wild-type contact evidence

**Status:** allele form `UNFILLED` · desk locus pass → see  
`09_outputs/prospective/G4_contact_desk_pass_v1.md`  
**Requirement:** native erythroid contact between pre-specified E and P.  
**Desk note (2026-07-14):** HUDEP-2 CTCF anchors dense in L-HO_A/B/C;  
named E–P + observed contact still **UNKNOWN** (public HUDEP-2 maps gap at 64–68 Mb).

```yaml
enhancer_E:
  chrom: null
  start: null
  end: null
  evidence: null
promoter_P:
  chrom: null
  start: null
  end: null
  gene: null
wt_contact:
  assay: null            # Capture-C / Micro-Capture-C / Hi-C / 4C
  cell_state: HUDEP-2_required
  observed: UNKNOWN
  provenance_url_or_path: null
  reproducible: UNKNOWN
locus_anchor_desk:
  status: PARTIAL_PASS
  artifact: 09_outputs/prospective/G4_contact_desk_pass_v1.md
```

Fail allele-G4 if no observed WT contact in the intended cell state.
