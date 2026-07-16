# Primer genomic uniqueness desk v1 (UCSC BLAT)

**Date:** 2026-07-16
**Status:** `PRIMER_BLAT_DESK_COMPLETE`
**Claim:** `PRIMER_NCBI_BLAST_CLAIM_v1.md`
**Label:** **`PRIMER_BLAT_DESK_REDESIGN`**
**Engine:** UCSC hgBlat hg38 (PSL) — NCBI blastn-short was flaky (HTTP 502)
**Oligo order:** FORBIDDEN

## Results (per primer)

| Pair | Role | Sequence | Label | n strong | Top hits |
|------|------|----------|-------|---------:|----------|
| OT0 | fwd | `TTTCTCCTAGGTCACACCCA` | **BLAST_OK** | 1 | chr11:62753822-62753842 (100.0%) |
| OT0 | rev | `TTAGGGAGTTCTCGAAGTGG` | **BLAST_OK** | 1 | chr11:62754038-62754058 (100.0%) |
| OT1 | fwd | `AGGTCCCCAGGAGAGAGGT` | **BLAST_OK** | 0 | — |
| OT1 | rev | `TCTTGTCACCCAGATGAGCT` | **BLAST_OK** | 1 | chr7:4805709-4805729 (100.0%) |
| OT2b | fwd | `GGCACTTGTAGTCCCAGCTAC` | **BLAST_MULTI** | 89 | chr9:66617845-66617866 (100.0%); chr9:66929910-66929931 (100.0%); chr9:42777590-42777611 (100.0%) |
| OT2b | rev | `ATGTTTTCCGGGGTGGGAAGG` | **BLAST_OK** | 1 | chr12:121534495-121534516 (100.0%) |
| OT3 | fwd | `CGGTTCTATGCTCACAGTGT` | **BLAST_MULTI** | 23 | chrX:55674042-55674062 (100.0%); chrX:14463535-14463555 (100.0%); chr6:83292808-83292828 (100.0%) |
| OT3 | rev | `ATTATCGGAGCTTGAACGCG` | **BLAST_OK** | 1 | chr1:92389050-92389070 (100.0%) |
| OT4 | fwd | `TGAGCCAGAGTTCATGGTCA` | **BLAST_OK** | 1 | chr13:114290080-114290100 (100.0%) |
| OT4 | rev | `TTGGAACTGAGAACCCCTGA` | **BLAST_OK** | 1 | chr13:114290302-114290322 (100.0%) |

## Reading

- Strong hit: ≥95% identity and ≥90% query coverage on a `chr*` target
- Complements UCSC **isPCR** (pair products already checked)
- Interactive NCBI Primer-BLAST UI remains optional lab SOP confirm

## Joint reading vs UCSC isPCR

| Pair | isPCR (pair) | BLAT F | BLAT R | Desk take |
|------|--------------|--------|--------|-----------|
| OT0 | PASS | OK (1) | OK (1) | clean |
| OT1 | PASS | OK (0)* | OK (1) | *F 19bp; genome has +1 base — pair still OK |
| OT2b | WARN (polyA) | **MULTI (89)** | OK (1) | F multi-maps alone; **pair** unique in isPCR |
| OT3 | PASS | **MULTI (23)** | OK (1) | F multi-maps alone; **pair** unique in isPCR |
| OT4 | PASS | OK (1) | OK (1) | clean |

**Verdict nuance:** `PRIMER_BLAT_DESK_REDESIGN` flags non-unique single primers. For amplicon-NGS the deciding desk check remains **isPCR pair uniqueness** (already PASS/WARN). OT2b/OT3 F multi-maps are **disclosures**, not automatic kill of the pair — optional further F redesign if lab wants unique singles.

## Plain language

Одиночные праймеры прогнаны через BLAT по hg38. Это desk-уникальность, не заказ олиго.

Full dump: `PRIMER_NCBI_BLAST_desk_v1.json`
