# C1 claim freeze pack — search-locked (NOT wet-lab GO)

**Date:** 2026-07-15 (rev after G4a+P1+G4b desk freeze)  
**Status:** `CLAIM_LOCKED` + `G4b_PROTOCOL_DESK_FROZEN`  
**Not:** G9 immutable wet-lab freeze · Not wet-lab GO  

Allowed language:

> C1 — sequence/activity-effect candidate; HUDEP-2 locked E–P contact desk-detected; allele-specific architecture effect not tested.

Also OK:

> Provisional architecture panel may be designed (assay chain grounded by 3′HS1 P1).

Forbidden:

> C1 нарушает enhancer–promoter loop в HUDEP-2.

---

## Machine status

```text
C1 sequence/activity evidence     PARTIAL
C1 WT contact in HUDEP-2 (G4a)    PASS_DESK
C1 allele-specific contact (G4b)  PROTOCOL_DESK_FROZEN / NOT TESTED in cells
architecture positive control     PASS_DESK (P1-system 3′HS1)
independent 3D scorer             ABSENT / UNVALIDATED
architecture freeze               PROVISIONAL_OPEN_LANGUAGE_ONLY
wet-lab architecture GO           BLOCKED
activity investigation            CONDITIONAL GO (Branch B)
ARCHCODE comparison               EXPLORATORY GO
PE path                           DESK shortlist (no order)
```

---

## Locked package

```yaml
candidate: C1
genome_build: GRCh38
variant_coordinate: chr11:62753923
variant_coordinate_hg19: chr11:62521395
ref: A
alt: G
te_context: AluSz
cell_state_intended: HUDEP-2

enhancer_E:
  chrom: chr11
  start: 62390000
  end: 62395000
  hg19: chr11:62157472-62162472
  status: LOCKED_PROVISIONAL
promoter_P:
  chrom: chr11
  start: 62690000
  end: 62695000
  hg19: chr11:62457472-62462472
  status: LOCKED_PROVISIONAL
  gene: UNKNOWN_pending_HUDEP2_TSS

mechanism_class_primary: M3_activity
mechanism_class_conditional_architecture: M1_IF_G4b_PASS

predicted_direction:
  contact: UNKNOWN_do_not_preclaim
  activity_chip_tf: decrease_vs_REF
  expression: UNKNOWN_secondary

primary_endpoint_architecture_branch: delta_Contact_E_P_HUDEP2
mcid:
  contact: |
    |ΔContact| ≥ 25% of WT Contact(E,P)
    OR |ΔOE| ≥ 0.5 (see G4b_protocol_freeze_v1.md)
  activity: null
fail_condition:
  - cannot_edit_or_verify_allele
  - assay_blind_to_P1_local
  - abs_delta_contact_below_MCID
  - shopping_new_E_or_P_after_data_view
```

## Linked freezes

- `G4b_protocol_freeze_v1.md`  
- `G4b_bait_windows_locked.yaml`  
- `G5_PE_shortlist_C1_desk_v1.md`  
- `BranchA_panel_freeze_provisional_v1.md`  
- `G4a_gsm4873113_desk_pass_v1.md`  
- `P1_3primeHS1_desk_pass_v1.md`  
