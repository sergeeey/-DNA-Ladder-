# Branch A provisional panel skeleton (NO GO)

**Status:** `DRAFT_ONLY` · not frozen · not wet-lab authorized  
**Prereqs so far:** G4a PASS_DESK · P1-system dump via overnight job · G5 BE FAIL  

## Intended primary claim (only after P1 desk + G4b plan)

> C1 changes a pre-specified E–P contact in HUDEP-2 (to be measured by Capture-C/MCC after edit).

## Suggested panel (architecture mode)

| ID | Role | Notes |
|----|------|-------|
| C1 | test | A>G; PE preferred |
| C2 | same-site allelic control | A>T activity twin |
| P1-system | pos control | 3′HS1 del (B6) — literature + local Hi-C |
| P1-local | pos control | planted CTCF near P or E |
| N3 | neutral | GC+ATAC matched KEEP |
| N_new | neutrals | replace N1/N2 |

## Endpoints

```yaml
primary: delta_Contact_E_P   # G4b
secondary:
  - CTCF_or_cohesin_occupancy
  - expression_neighborhood   # optional
mcid: null
fail_condition:
  - no_delta_contact_vs_WT
  - assay_blind_to_P1_local
  - edit_not_verified
```

## Still blocked for GO

```text
[ ] P1-system local dump PASS
[ ] G4b assay protocol + bait design covering E or P
[ ] PE pegRNA shortlist + off-target desk
[ ] MCID + fail conditions signed
```

Until checked: **NO_GO_FOR_WET_LAB**.
