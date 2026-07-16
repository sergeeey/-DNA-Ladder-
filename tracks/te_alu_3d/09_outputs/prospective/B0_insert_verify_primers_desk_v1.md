# B0 insert-verify / Sanger primers — desk v1

**Date:** 2026-07-16  
**Status:** `DESK_CANDIDATE` · **ORDER FORBIDDEN** until Phase B0 GO  
**Scope:** primers that bind **inside** the 301 bp C1 insert (backbone-independent)  
**Not included:** insert↔backbone junction oligos (require frozen `backbone_id` + MCS map)

**JSON:** `B0_insert_verify_primers_desk_v1.json`  
**Insert hashes:** see `B0_bmin_hash_spotcheck_v1.json`

---

## Design notes

- Window: `c1_reporter_minimal_301bp_{REF,ALT}.fa` (301 bp; C1 index **150**, A→G)  
- Method: local Tm (SantaLucia-approx Wallace form) + GC 35–65%; 3′ G/C preferred  
- Genome uniqueness: **not** Primer-BLASTed (plasmid verify / colony PCR context)  
- Same primer pair works on REF and ALT; Sanger distinguishes A vs G at index 150  

---

## Recommended panel

| ID | Role | Seq 5′→3′ | Bind (0-based) | Tm≈ | GC | Notes |
|----|------|-----------|----------------|----:|---:|-------|
| **B0-IV-F** | Insert verify F | `CTTGCCACTCCAAAACAATCGC` | 11–32 | 54.8 | 0.50 | with IV-R ≈ full insert gel |
| **B0-IV-R** | Insert verify R | `GCGTGAGGGAGATGCTTAGG` | 281–300 (RC) | 55.9 | 0.60 | |
| **B0-SG-F** | Sanger F (flank SNP) | `AAGCTCTCCCATTAGCTCCGCC` | 70–91 | 58.6 | 0.59 | amplicon ~150 bp w/ SG-R |
| **B0-SG-R** | Sanger R (flank SNP) | `TACTTCGTGGAGCCGTTGGACG` | 198–219 (RC) | 58.6 | 0.59 | read covers base 150 |

Amplicon IV-F/R: ~290 bp (insert-internal).  
Amplicon SG-F/R: positions 70–219 → **150 bp**; expected Sanger call REF=`A` / ALT=`G` at insert index 150.

---

## After backbone freeze (still TODO at wet)

| ID | Role | Status |
|----|------|--------|
| B0-JX-F | Junction F (backbone → insert 5′) | **BLOCKED** until MCS map |
| B0-JX-R | Junction R (insert 3′ → backbone) | **BLOCKED** until MCS map |

---

## Order gate

- [ ] Phase B0 GO signed  
- [ ] Prefer order with B-min gBlocks, not as PE/OT mix  
- [ ] Lab gradient / melt before relying on colony PCR  

---

## Linked

- `BranchB_oligo_checklist_v1.md`  
- `B0_backbone_desk_nominate_v1.md`  
- `B0_PO_draft_v1.md`  
