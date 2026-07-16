# Primer in-silico uniqueness — desk pass (A1 pre-order)

**Status:** PRE-REGISTERED (before UCSC isPCR results)
**Date locked:** 2026-07-16
**L0:** Descriptive technical QC — not wet-lab GO; does not authorize oligo order alone
**Scope:** OT0–OT4 amplicon primer pairs from `OT_amplicon_primer_panel_desk_v1.md`

## Engines

| Engine | Role |
|--------|------|
| **UCSC In-Silico PCR (hg38)** | Primary desk batch: count genome products ≤ max size |
| **NCBI Primer-BLAST** | Optional human confirm (manual or later); more sensitive to mismatches |

UCSC notes: not guaranteed to find all off-target sites; optimized for high-identity matches. Failures → redesign, not silent PASS.

## Labels (per pair)

| ID | Rule |
|----|------|
| **ISPCR_PASS** | Exactly **1** product; overlaps expected amplicon locus |
| **ISPCR_WARN** | 1 product but length/locus soft mismatch, or polyA/flag risk |
| **ISPCR_MULTI** | ≥2 products → redesign / do not order |
| **ISPCR_NONE** | 0 products → primers wrong orientation or site error |
| **ISPCR_FAIL** | HTTP/parse error |

## Panel label

| ID | Rule |
|----|------|
| **PRIMER_DESK_PASS** | All OT0–OT4 are ISPCR_PASS or ISPCR_WARN (no MULTI/NONE/FAIL) |
| **PRIMER_DESK_GAPS** | Any WARN or none-only soft issues; no MULTI |
| **PRIMER_DESK_REDESIGN** | Any MULTI or NONE |
| **PRIMER_DESK_BLOCKED** | Engine unreachable |

## Forbidden

- Treating this as signed A1 GO
- Ordering oligos
- Skipping OT2 polyA note if WARN

## Arts

Script: `pilot_scaffold/scripts/run_primer_ispcr_desk.py`
Out: `PRIMER_ISPCR_desk_v1.md` / `.json`
