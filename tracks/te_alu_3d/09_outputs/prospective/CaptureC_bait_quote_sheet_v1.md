# Capture-C bait quote sheet v1 — C1 locked E/P

**Date:** 2026-07-15  
**Status:** `QUOTE_ONLY` · **ORDER FORBIDDEN**  
**Use:** send to core / vendor for **price + lead time** only  
**Not:** wet-lab GO · not bait redesign · Phase A2 of `GO_note_draft_C1_B_first_v1.md`

Windows locked in `G4b_bait_windows_locked.yaml` — **do not move after data view**.

---

## Request summary (paste to vendor)

```text
Project: C1 allele ΔContact (future)
Assay: NG Capture-C or Capture-C (double-bait multiplex preferred)
Cell (future): HUDEP-2
Genome: GRCh38 design; legacy Hi-C maps may be hg19 — state build on quote
Baits: two viewpoints (E and P), ~5 kb each
Optional later: P1-local CTCF neighborhood (P-side) — separate line item
```

---

## Locked bait windows

| ID | Role | GRCh38 | hg19 | Size |
|----|------|--------|------|-----:|
| **bait_E** | enhancer anchor | `chr11:62390000-62395000` | `chr11:62157472-62162472` | 5 kb |
| **bait_P** | promoter anchor | `chr11:62690000-62695000` | `chr11:62457472-62462472` | 5 kb |
| viewpoint_C1 | variant site — **not** required as bait | `chr11:62753923` | `chr11:62521395` | point |

Approximate span E→P: ~300 kb (GRCh38).

---

## Quote line items (fill when vendor replies)

| Line | Description | Qty hint | Price | Lead time | Notes |
|------|-------------|----------|------:|-----------|-------|
| Q1 | Capture oligos / probes for **bait_E** | 1 design | | | build _______ |
| Q2 | Capture oligos / probes for **bait_P** | 1 design | | | |
| Q3 | Multiplex Capture-C both baits | package | | | preferred |
| Q4 | Library prep / sequencing package (optional) | per sample | | | samples TBD |
| Q5 | Optional P1-local P-side CTCF bait neighborhood | later | | | GRCh38 `chr11:62694751-62695044` peak ± design pad |
| Q6 | MCC / Micro-Capture-C escalation package | if Capture-C blind | | | G4b escalation |

```yaml
vendor: null
quote_date: null
quote_id: null
currency: null
validity_days: null
contact: null
```

---

## Design rules for vendor (non-negotiable)

```text
1. Use exactly the GRCh38 intervals above (or exact hg19 lift if processing hg19).
2. Do not optimize / shift ends to “stronger” DNase/CTCF without written amendment.
3. Prefer baits on E and/or P; C1 site not required as viewpoint.
4. Report probe density / uniqueness / repeat masking briefly in quote technical sheet.
5. Quote is informational — synthesis starts only after Phase A2 GO + A1 edit PASS.
```

---

## Scientific endpoints (for context, not vendor SOW)

```text
Primary: ΔContact(E,P) allele C1 vs WT
MCID: |ΔContact| ≥ 25% of WT OR |ΔOE| ≥ 0.5
Primary assay: Capture-C; Hi-C not sole readout
```

---

## Linked

- `G4b_protocol_freeze_v1.md`  
- `G4b_bait_windows_locked.yaml`  
- `GO_note_draft_C1_B_first_v1.md`  
- `P1_local_HUDEP2_CTCF_confirm_v1.md`  
- `NDE_C1_exhaustion_A_plus_B_v1.md`  
