# G5 continuation — prime editing desk for C1 (non-GO)

**Status:** DESK_ONLY · wet-lab **STOPPED** until architecture/activity panel freeze  
**Variant:** chr11:62753923 A>G (GRCh38)

## Prior desk

SpCas9 NGG places variant at spacer positions **17–18** → classic cytosine/adenine BE window FAIL.

## PE sketch (to complete before any wet GO)

```yaml
edit_type: prime_edit
intended: A>G at chr11:62753923
pegRNA_design_pending: true
nicking_sgRNA_pending: true
off_target_desk_pending: true
verification_plan:
  - PCR + Sanger / amplicon NGS
  - clonality / editing rate gate
```

## Tools to run (next compute pass)

1. PrimeDesign / pegFinder / Easy-Prime style pegRNA candidates  
2. Cas9 / PE2 / PE3 nickase availability note  
3. Off-target Cas-OFFinder for spacer+PBS

## Gate

Even with perfect pegRNA, **no wet GO** without:

- activity or architecture primary endpoint frozen  
- MCID  
- fail conditions  
- (for architecture) G4b assay plan  

Artifact linked from G5 desk: extend `G5_editability_desk_pass_v1.md` when pegRNA list exists.
