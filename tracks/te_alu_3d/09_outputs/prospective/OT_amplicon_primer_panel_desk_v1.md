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

| ID | Locus | Amplicon (GRCh38) | bp | Forward (5′→3′) | Rev (5′→3′) | Tm F/R | Flag |
|----|-------|-------------------|---:|-----------------|-------------|--------|------|
| OT0 | C1 on-target | chr11:62753823-62754058 | 236 | `TTTCTCCTAGGTCACACCCA` | `TTAGGGAGTTCTCGAAGTGG` | 60/60 | edit verify |
| OT1 | RADIL exon | chr7:4805443-4805729 | 287 | `AGGTCCCCAGGAGAGAGGT` | `TCTTGTCACCCAGATGAGCT` | 62/60 | priority watch |
| OT2 | KDM2B intron | chr12:121534283-121534502 | 220 | `AGCTTGCAGTGAGCCGAGA` | `GGGAAGGTGAGTTTCAGTTG` | 60/60 | **polyA inside amp — redesign if PCR poor** |
| OT3 | RPAP2 exon | chr1:92388850-92389070 | 221 | `CGGTTCTATGCTCACAGTGT` | `ATTATCGGAGCTTGAACGCG` | 60/60 | |
| OT4 | UPF3A intron | chr13:114290091-114290332 | 242 | `TGAGCCAGAGTTCATGGTCA` | `TTGGAACTGAGAACCCCTGA` | 60/60 | |

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

- [x] UCSC in-silico PCR desk batch — `PRIMER_ISPCR_desk_v1.md` (**OT2 FAIL → redesign**)
- [ ] NCBI Primer-BLAST human confirm (optional/SOP) for OT0/1/3/4
- [ ] Redesign OT2 (Alu-like F primer / polyA amp — isPCR 0 products)
- [ ] Phase A1 GO signed
- [ ] Include Illumina tails / indices per core SOP (not in this desk file)

**If OT2 unchecked redesign → no oligo PO for full OT panel.**

---

## Linked

- `GO_note_draft_C1_B_first_v1.md`  
- `G5_PE_OT_CRISPOR_PD1_v1.md`  
- `NDE_C1_exhaustion_A_plus_B_v1.md`  
- `BranchB_reporter_design_v1.md`  
