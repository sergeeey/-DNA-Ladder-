# OT amplicon primer panel — desk v1 (Phase A1 pre-work)

**Date:** 2026-07-15  
**Status:** `DESK_ONLY` · **ORDER FORBIDDEN** until Phase A1 GO + **Primer-BLAST**  
**Method:** local heuristic (Wallace Tm); genome hg38 via UCSC API  
**JSON:** `ot_amplicon_primers_desk_v1.json`  
**Script:** `pilot_scaffold/tools/design_ot_amplicon_primers_v1.py`

These primers are **candidates for amplicon-NGS**, not proven unique. Do not order without:

1. Primer-BLAST (nr / genome human) uniqueness check  
2. Signed Phase A1 in `GO_note_draft_C1_B_first_v1.md`  
3. Lab PCR gradient / melt validation  

Sites = watchlist from CRISPOR PD1 — **not** proven off-targets.

---

## Primer table

| ID | Locus | Amplicon (GRCh38) | bp | Forward (5′→3′) | Rev (5′→3′) | Flag |
|----|-------|-------------------|---:|-----------------|-------------|------|
| OT0 | C1 on-target | chr11:62753823-62754058 | 236 | `TTTCTCCTAGGTCACACCCA` | `TTAGGGAGTTCTCGAAGTGG` | edit verify |
| OT1 | RADIL exon | chr7:4805443-4805729 | 287 | `AGGTCCCCAGGAGAGAGGT` | `TCTTGTCACCCAGATGAGCT` | priority watch |
| ~~OT2 / OT2b~~ | KDM2B old | — | — | — | — | DEPRECATED |
| **OT2c** | KDM2B intron | chr12:121533931-121534465 | 535 | `CTCGAGAGCTGAGGTGGGAA` | `ATCTCTAGCTGTTTGTGTGG` | redesign v2; BLAT-unique |
| ~~OT3~~ | RPAP2 old | — | — | `CGGTTCTATGCTCACAGTGT` | — | DEPRECATED F multi |
| **OT3b** | RPAP2 exon | chr1:92388530-92389070 | 541 | `TAGCCCACAGAGGGTTAGCC` | `ATTATCGGAGCTTGAACGCG` | redesign v2; BLAT-unique |
| OT4 | UPF3A intron | chr13:114290091-114290332 | 242 | `TGAGCCAGAGTTCATGGTCA` | `TTGGAACTGAGAACCCCTGA` | |

Coordinates: UCSC 0-based design internally; table shows 1-based inclusive amplicon span.

Optional secondary exon watches (no primers yet): TEX40, PHF12, PRKG1 — see `G5_PE_OT_CRISPOR_PD1_v1.md`.

---

## Locked-P TSS nomination (desk)

Locked P: `chr11:62690000-62695000`.

| Finding | Detail |
|---------|--------|
| TSS **inside** locked P | **none** (refGene) |
| Closest TSS | **LRRN4CL** (−) TSS `chr11:62689530` (~3 kb from P midpoint; just upstream of P start) |
| Gene **body** overlapping locked P | **BSCL2** / **HNRNPUL2-BSCL2** read-through (−), overlap ~4.7 kb; their TSS are downstream of P |

**Nomination for future expression / promoter naming (provisional):**

```text
architecture P window intersects BSCL2 gene body
nearest upstream promoter-like TSS: LRRN4CL
C1 cis-activity nearer genes (Branch B): ZBTB3, POLR2G — separate from locked P
```

Do **not** claim C1 regulates LRRN4CL/BSCL2 until HUDEP-2 RNA / TSS-seq nominates.

---

## Pre-order gate (A1)

- [x] UCSC isPCR — **PRIMER_DESK_PASS** (`PRIMER_ISPCR_desk_v1.md`) active set OT0/1/2c/3b/4
- [x] Forward redesign — **OT2c** + **OT3b** (`OT_forward_redesign_v1.md`)
- [x] Single-primer BLAT — **PRIMER_BLAT_DESK_PASS** (`PRIMER_NCBI_BLAST_desk_v1.md`)
- [ ] Phase A1 GO signed
- [ ] Include Illumina tails / indices per core SOP

**If A1 GO unchecked → no oligo PO.**

---

## Linked

- `GO_note_draft_C1_B_first_v1.md`  
- `G5_PE_OT_CRISPOR_PD1_v1.md`  
- `NDE_C1_exhaustion_A_plus_B_v1.md`  
- `BranchB_reporter_design_v1.md`  
