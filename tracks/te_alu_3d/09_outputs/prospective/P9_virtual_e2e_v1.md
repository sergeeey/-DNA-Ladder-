# P9 — Virtual end-to-end dry-run v1

**Date:** 2026-07-16
**Status:** `P9_VIRTUAL_E2E_COMPLETE`
**Claim:** `P9_VIRTUAL_E2E_CLAIM_v1.md`
**Label:** **`P9_GAPS`**

## Summary

| Class | n |
|-------|--:|
| OK checks | 32 |
| Soft gaps | 3 |
| Hard blocks | 0 |

## Soft gaps

| ID | Detail |
|----|--------|
| `BACKBONE_TBD` | Reporter backbone vendor/plasmid ID still lab-fill before order |
| `PRIMER_BLAST_MANUAL` | Genome-wide Primer-BLAST still manual before oligo order |
| `CAPTURE_UNDERPOWERED` | Capture-C P8_UNDERPOWERED — must not be sold as powered primary |

## Hard blocks

| ID | Detail |
|----|--------|
| — | none |

## Phase walk

| Phase | Result |
|-------|--------|
| B0 reporter | FASTA present; MCID present; ORDER FORBIDDEN; backbone lab-fill soft |
| A1 PE | `PE_OT_CONDITIONAL_PASS`; RADIL watch; Primer-BLAST manual soft |
| A2 Capture-C | baits locked; quote sheet present; **P8_UNDERPOWERED** soft |
| Cross-cutting | holdout SEALED · Stage-3 LOCKED · GO UNSIGNED_DRAFT |

## Plain language

План B0→A1→A2 на бумаге **сходится**: артефакты есть, замки целы, жёстких противоречий нет.
Остаются мягкие дыры (backbone, Primer-BLAST, Capture недомощен) — это не редизайн, а чеклист до human GO.

## What this does NOT mean

- Not wet-lab authorization
- Not oligo order
- Not Capture-C powered primary
- Not biological proof of C1

Full dump: `P9_virtual_e2e_v1.json`
