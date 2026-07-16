# NCBI-style primer uniqueness desk pass

**Status:** PRE-REGISTERED (before BLAST results)
**Date locked:** 2026-07-16
**L0:** Descriptive technical QC — not A1 GO; does not authorize oligo order
**Pairs:** OT0, OT1, OT2b, OT3, OT4 (OT2 deprecated skipped)

## Engine

| Engine | Role |
|--------|------|
| **UCSC BLAT hg38 (PSL)** | Primary desk batch for single-primer hit counts |
| NCBI `blastn-short` / Primer-BLAST UI | Optional; often flaky remotely — lab SOP confirm |

Not a full interactive Primer-BLAST product-pairing report. Complements UCSC isPCR pair check.

## Labels (per primer)

| ID | Rule |
|----|------|
| **BLAST_OK** | ≤3 genomic hits at ≥95% identity over ≥90% of primer |
| **BLAST_WARN** | 4–10 such hits |
| **BLAST_MULTI** | >10 such hits |
| **BLAST_FAIL** | engine error |

## Panel label

| ID | Rule |
|----|------|
| **PRIMER_BLAT_DESK_PASS** | all primers BLAST_OK; no FAIL |
| **PRIMER_BLAT_DESK_GAPS** | any WARN, no MULTI/FAIL |
| **PRIMER_BLAT_DESK_REDESIGN** | any MULTI |
| **PRIMER_BLAT_DESK_BLOCKED** | engine unreachable for majority |

## Forbidden

- Ordering oligos / signing A1 from this alone
- Treating as wet PCR proof

## Arts

Script: `pilot_scaffold/scripts/run_primer_ncbi_blast_desk.py`
Out: `PRIMER_NCBI_BLAST_desk_v1.md` / `.json`
