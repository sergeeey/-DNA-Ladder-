# P9 — Virtual end-to-end dry-run v1

**Date:** 2026-07-16
**Status:** `P9_VIRTUAL_E2E_COMPLETE`
**Claim:** `P9_VIRTUAL_E2E_CLAIM_v1.md`
**Label:** **`P9_GAPS`**

## Summary

| Class | n |
|-------|--:|
| OK checks | 32 |
| Soft gaps | 4 |
| Hard blocks | 0 |

## Soft gaps

| ID | Detail |
|----|--------|
| `BACKBONE_DESK_NOMINATED` | Desk default Promega E8411; lab still freezes `backbone_id` at GO |
| `B0_INSERT_VERIFY_PRIMERS` | Insert-internal IV/Sanger desk; junction oligos wait MCS map |
| `PRIMER_BLAST_MANUAL` | OT isPCR+BLAT PASS; NCBI Primer-BLAST optional for A1 |
| `CAPTURE_UNDERPOWERED` | Capture held as non-primary (`A2_CAPTURE_HELD_v1.md`) |

## Hard blocks

| ID | Detail |
|----|--------|
| — | none |

## Phase walk

| Phase | Result |
|-------|--------|
| B0 reporter | FASTA+hashes; IV/Sanger primers desk; PO draft; backbone nominated; ORDER FORBIDDEN until GO |
| A1 PE | `PE_OT_CONDITIONAL_PASS`; RADIL watch; Primer-BLAST manual soft |
| A2 Capture-C | baits locked; quote sheet present; **P8_UNDERPOWERED** soft |
| Cross-cutting | holdout SEALED · Stage-3 LOCKED · GO UNSIGNED_DRAFT |

## Plain language

План B0→A1→A2 на бумаге **сходится**. B0 paperwork desk-closed (backbone nominate, IV/Sanger, PO draft). Жёсткий блокер один: human GO signature. Capture не primary.

## What this does NOT mean

- Not wet-lab authorization
- Not oligo order
- Not Capture-C powered primary
- Not biological proof of C1

Full dump: `P9_virtual_e2e_v1.json`
