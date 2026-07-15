# G4b protocol freeze v1 — allele ΔContact (DESK FREEZE, not wet GO)

**Date:** 2026-07-15  
**Status:** `PROTOCOL_DESK_FROZEN`  
**Not:** wet-lab authorization · not G9  

**Prereqs met:** G4a PASS_DESK · P1-system PASS_DESK · claim/E/P locked  

---

## Estimand (frozen)

```text
ΔContact(E,P) = Contact_C1 − Contact_WT
in HUDEP-2, same assay, locked E and P
```

Direction is **not** pre-claimed (occupancy/AGC leave M1 uncertain).  
Report signed Δ and whether |Δ| ≥ MCID.

---

## Assay (frozen rank order)

1. **Primary:** NG Capture-C or Capture-C with bait on locked **E and/or P**  
2. **Escalation:** MCC / Micro-Capture-C if Capture-C blind at ~300 kb  
3. **Not sole readout:** genome-wide Hi-C (use only as secondary maps)

Normalization / binning must be fixed **before** allele contrasts:
- KR or sinkhorn as available for the chosen pipeline  
- Primary resolution: **5–10 kb** strip covering E×P  
- Secondary: 25 kb robustness check  

---

## Baits (frozen — do not shop)

See `G4b_bait_windows_locked.yaml`.

| ID | GRCh38 | hg19 |
|----|--------|------|
| bait_E | chr11:62390000-62395000 | chr11:62157472-62162472 |
| bait_P | chr11:62690000-62695000 | chr11:62457472-62462472 |
| C1 site (not required as bait) | chr11:62753923 | chr11:62521395 |

---

## Alleles / replicates

```yaml
cell: HUDEP-2
alleles:
  WT: parental or mock-edited
  C1: A>G via prime editing (see G5_PE_shortlist_C1_desk_v1.md)
  C2_optional: A>T same-site allelic control
replicates: >=2 independent edited clones OR two culture reps if clones unavailable
edit_verification: amplicon NGS ≥70% intended allele in scored samples (desk default; adjustable)
```

---

## Controls

| Control | Role |
|---------|------|
| P1-system 3′HS1 (historical) | assay-chain already PASS_DESK |
| P1-local planted CTCF near P or E | sensitivity at C1 neighborhood (design sketch) |
| N3 neutral TE-SNV | specificity / matching |

---

## MCID (desk default — change only with written amendment)

From G4a WT 10 kb enrichment baseline (~3.4× vs same-distance bg) and OE≈3.2:

```yaml
mcid_contact:
  primary_metric: OE_KR_or_Capture_normalized_EP
  rule: |
    |ΔContact| ≥ 25% of WT Contact(E,P)
    OR |ΔOE| ≥ 0.5 absolute units for OE-scaled metrics
  replicate_rule: same direction in ≥2/2 replicates
rationale: >
  Detectable against WT noise; aligned with P1-system scale
  (HS1–HS5 OE fell to ~0.34× WT — assay sees large architecture breaks).
  C1 expected effect may be smaller; 25% relative is a go/no-go floor, not a biology claim.
```

---

## PASS / FAIL

**PASS (scientific G4b):**

```text
edit verified
AND |ΔContact| ≥ MCID in predicted-or-observed consistent direction
AND reproducible across replicates
AND assay not blind (P1-local OR documented P1-system transferability note)
```

**FAIL → pivot Branch B:**

```text
edit ok but |ΔContact| < MCID
OR assay blind to P1-local
OR cannot verify allele
```

---

## Still blocked

```text
wet-lab GO: NO
guide ordering: NO
holdout unblind: NO
claim "C1 disrupts loop": NO until PASS above
```

## Linked arts

- Baits: `G4b_bait_windows_locked.yaml`  
- PE: `G5_PE_shortlist_C1_desk_v1.md`  
- Panel: `BranchA_panel_freeze_provisional_v1.md`  
- Claim pack: `C1_claim_freeze_pack_v1.md`  
