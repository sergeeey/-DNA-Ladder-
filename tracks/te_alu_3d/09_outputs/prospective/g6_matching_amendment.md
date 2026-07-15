# G6 matching amendment — GC + K562 ATAC

**ATAC:** ENCODE `ENCFF055NNT` (K562 proxy, not HUDEP-2)  
**GC:** Ensembl windows ±100 bp / ±1 kb  
**panel_frozen:** still false

## GC vs C1

| ID | |ΔGC| ±100bp | |ΔGC| ±1kb | Grade |
|----|------------:|-----------:|-------|
| C1 | 0 | 0 | reference (GC±100=0.622) |
| N1 | 0.070 | 0.122 | POOR |
| N2 | 0.129 | 0.138 | POOR |
| N3 | 0.045 | 0.042 | TIGHT |
| C3 | 0.100 | 0.041 | OK |

## K562 ATAC overlap

| ID | In peak | ≤250bp | Dist | vs C1 |
|----|---------|--------|-----:|-------|
| C1 | True | True | 177 | MATCH |
| N1 | False | True | 19 | MISMATCH |
| N2 | True | True | 13 | MATCH |
| N3 | True | True | 85 | MATCH |
| C3 | True | True | 79 | MATCH |

## Neutral keep/drop (desk)

- **N1**: DROP/REPLACE (GC POOR, ATAC MISMATCH)
- **N2**: DROP/REPLACE (GC POOR, ATAC MATCH)
- **N3**: KEEP (GC TIGHT, ATAC MATCH)

## ARCHCODE hunt

- Local workspace / common user paths: **ABSENT**
- Unlock still needs binary/repo path or continue AlphaGenome-only

Artifact: `g6_matching_amendment.json`
