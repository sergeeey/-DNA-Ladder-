# Gate card — prospective panel admission (one variant)

**Protocol:** `SCALE_PROTOCOL_prospective_panel_v1.md`  
**Fill before** frozen-panel admission. Do not use holdout or ClinVar labels.

```yaml
candidate_id: null
variant: {chrom: null, pos: null, ref: null, alt: null, build: GRCh38}
cell_type_intended: HUDEP-2
mechanism_prior: null          # M1 / M2 / M3 / …
candidate_class: null          # convergence | principled_disagreement | negative | positive_control
```

| Gate | PASS? | Evidence (path / metric) | Notes |
|------|:-----:|--------------------------|-------|
| G0 QC / map / not segdup | ☐ | | |
| G1 cell-type relevant | ☐ | | |
| G2 WT context or contact | ☐ | | if fail → computational only |
| G3 mechanism + competitors | ☐ | | |
| G4 no ClinVar/consequence leak; holdout untouched | ☐ | | |
| G5 editable (BE/PE desk) | ☐ | | |
| G6 matched controls feasible | ☐ | | |
| G7 direction or UNKNOWN+MCID pre-set | ☐ | | |
| G8 claim + coords frozen | ☐ | | |

```text
Admission:  REJECT | COMPUTATIONAL_ONLY | FROZEN_PANEL_CANDIDATE
Stage-3 eligible later?: YES / NO / ONLY_IF_DISAGREEMENT_SLOT
```

Signature (desk): _____________ Date: _____________
