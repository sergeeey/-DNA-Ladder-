# Primer genomic uniqueness desk v1 (UCSC BLAT)

**Date:** 2026-07-16
**Status:** `PRIMER_BLAT_DESK_COMPLETE`
**Claim:** `PRIMER_NCBI_BLAST_CLAIM_v1.md`
**Label:** **`PRIMER_BLAT_DESK_PASS`**
**Engine:** UCSC hgBlat hg38 (PSL) — NCBI blastn-short was flaky (HTTP 502)
**Oligo order:** FORBIDDEN

## Results (per primer)

| Pair | Role | Sequence | Label | n strong | Top hits |
|------|------|----------|-------|---------:|----------|
| OT0 | fwd | `TTTCTCCTAGGTCACACCCA` | **BLAST_OK** | 1 | chr11:62753822-62753842 (100.0%) |
| OT0 | rev | `TTAGGGAGTTCTCGAAGTGG` | **BLAST_OK** | 1 | chr11:62754038-62754058 (100.0%) |
| OT1 | fwd | `AGGTCCCCAGGAGAGAGGT` | **BLAST_OK** | 0 | — |
| OT1 | rev | `TCTTGTCACCCAGATGAGCT` | **BLAST_OK** | 1 | chr7:4805709-4805729 (100.0%) |
| OT2c | fwd | `CTCGAGAGCTGAGGTGGGAA` | **BLAST_OK** | 1 | chr12:121533930-121533950 (100.0%) |
| OT2c | rev | `ATCTCTAGCTGTTTGTGTGG` | **BLAST_OK** | 1 | chr12:121534445-121534465 (100.0%) |
| OT3b | fwd | `TAGCCCACAGAGGGTTAGCC` | **BLAST_OK** | 1 | chr1:92388529-92388549 (100.0%) |
| OT3b | rev | `ATTATCGGAGCTTGAACGCG` | **BLAST_OK** | 1 | chr1:92389050-92389070 (100.0%) |
| OT4 | fwd | `TGAGCCAGAGTTCATGGTCA` | **BLAST_OK** | 1 | chr13:114290080-114290100 (100.0%) |
| OT4 | rev | `TTGGAACTGAGAACCCCTGA` | **BLAST_OK** | 1 | chr13:114290302-114290322 (100.0%) |

## Reading

- Strong hit: ≥95% identity and ≥90% query coverage on a `chr*` target
- Complements UCSC **isPCR** (pair products already checked)
- Interactive NCBI Primer-BLAST UI remains optional lab SOP confirm

## Plain language

Одиночные праймеры прогнаны через BLAT по hg38. Это desk-уникальность, не заказ олиго.

Full dump: `PRIMER_NCBI_BLAST_desk_v1.json`
