# Decision: TE/Alu Stage-3 architecture contact qualification

**Date:** 2026-07-21  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive  
**Verdict:** CLOSED — A754 NOT SUPPORTED; A518 INCONCLUSIVE

## Result

The Stage-3 contact branch tested two pre-frozen non-holdout candidates using
public HUDEP-2 Hi-C:

| Candidate | GSE160422 primary | Exact-distance sensitivity | GSE201820 replication | Closure |
|-----------|-------------------|----------------------------|----------------------|---------|
| A754 | PARTIAL | UNSUPPORTED | REPLICATION_UNSUPPORTED in both noIAA controls | NOT SUPPORTED |
| A518 | INCONCLUSIVE | INCONCLUSIVE | REPLICATION_INCONCLUSIVE | INCONCLUSIVE |

A754's only PASS occurred at 10 kb with a mixed 0/1/2-bin background. With the
pre-declared exact-distance sensitivity, `enrich_mean` fell from 1.6667 to
1.3894 and the score changed from PASS to FAIL. In the independently generated
GSE201820 noIAA differentiated and undifferentiated matrices, A754 failed at
both 10 kb and 25 kb.

A518 failed at 10 kb in all decision-bearing analyses. Its 25 kb anchors occupy
the same matrix bin, so that resolution is non-discriminating and remains
inconclusive rather than negative.

## Evidence chain

- Main preregistration:
  `G4a_stage3_architecture_wt_contact_CLAIM_v1.md`
- Main decision:
  `G4a_stage3_architecture_wt_contact_decision_v1.md`
- Exact-distance sensitivity decision:
  `G4a_stage3_architecture_wt_contact_bgtol0_sensitivity_decision_v1.md`
- Independent-source GSE201820 decision:
  `G4c_stage3_architecture_replic_decision_v1.md`
- Terminology correction:
  `G4_stage3_background_direction_ERRATUM_v1.md`
- Frozen anchors, manifests, preflight records, dump hashes, and result JSONs
  are under `tracks/te_alu_3d/09_outputs/prospective/`.

## What This Result Does NOT Mean

1. It does not show that either variant lacks any biological effect.
2. It does not test an ALT-versus-REF contact difference or any allele effect.
3. It does not identify a target gene, enhancer–promoter interaction,
   regulatory mechanism, pathogenicity, or causality.
4. It does not make A518 negative at 25 kb; that comparison is geometrically
   unresolved.
5. It does not generalize beyond the tested HUDEP-2 WT/noIAA conditions and
   frozen anchors.
6. It does not authorize holdout access or wet-lab work.

## Closure decision

No further threshold, normalization, background-tolerance, or anchor search on
these matrices is allowed as a rescue analysis. Reopening requires a genuinely
new pre-registered estimand and independent information source, not another
parameterization of the same contact question.

Holdout remains SEALED. Wet-lab remains NO-GO.
