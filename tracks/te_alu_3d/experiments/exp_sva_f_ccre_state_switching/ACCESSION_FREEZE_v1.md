# ACCESSION_FREEZE v1 — C-A2 SVA_F dELS switching

**Date:** 2026-07-20  
**Encyclopedia:** ENCODE **v3 / current** cell-type cCRE beds with
`All-data/Full-classification` (spot-checked).  
**Agnostic registry:** SCREEN Registry-V3 (preferred over portal v4 agnostic for class labels
`dELS` / `pELS` / … consistent with prior DNA Ladder cCRE freezes).

## Agnostic registry

| Role | URL / accession | Assembly |
|------|-----------------|----------|
| SCREEN Registry-V3 | `https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.bed` | GRCh38 |

dELS filter: column 6 contains `dELS` (e.g. `dELS` or `dELS,CTCF-bound`).

## Held-out baseline (matching only; excluded from switching \(N\))

| Biosample | File | Annotation | Encyclopedia |
|-----------|------|------------|--------------|
| SK-N-SH | **ENCFF948UCK** | ENCSR728TSY | ENCODE v3 current |

## Switching panel (ordered alphabetically by biosample — odd/even split)

| Order idx | Biosample | File | Annotation |
|-----------|-----------|------|------------|
| 0 | GM12878 | **ENCFF733BFV** | ENCSR450FYE |
| 1 | H1 | **ENCFF803RKE** | ENCSR183TOR |
| 2 | HCT116 | **ENCFF127CMS** | ENCSR384XUL |
| 3 | HeLa-S3 | **ENCFF830EEV** | ENCSR003ZIC |
| 4 | HepG2 | **ENCFF287MQD** | ENCSR356UJZ |
| 5 | IMR-90 | **ENCFF799ZNT** | ENCSR112MKQ |
| 6 | K562 | **ENCFF210CAN** | ENCSR940SYU |
| 7 | MCF-7 | **ENCFF837CPX** | ENCSR887CZM |
| 8 | Panc1 | **ENCFF812GKZ** | ENCSR438ZZW |
| 9 | PC-3 | **ENCFF664YMN** | ENCSR522AJP |

\(N = 10\). Odd panel = idx 0,2,4,6,8. Even panel = idx 1,3,5,7,9.

## TE / covariates

| Role | Source |
|------|--------|
| RepeatMasker | `https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz` |
| GENCODE TSS | `https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/gencode.v47.basic.annotation.gtf.gz` (protein-coding gene TSS) |
| Genome (GC) | `https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.2bit` |

## Rejected / not frozen

| Candidate | Reason |
|-----------|--------|
| Single SCREEN `GRCh38-cCREs.CTS` / `.Signal` URL | HTTP 404 |
| ENCODE v4 preferred_default beds with `Missing-data/Partial-classification` (many) | Incomplete activity calls |
| A549 / NCI-H460 v3–v4 beds probed | No Full-classification + dELS in spot-check |
| ChIA-PET / Hi-C loop files | Wrong estimand (not this C-A2) |

## Download path

`data/input/` (gitignored bulky beds). Checksums → `data_manifest.md` after T1.
