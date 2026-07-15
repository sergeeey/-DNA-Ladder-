# Branch B — reporter / activity assay design v1

**Date:** 2026-07-15  
**Status:** `DESIGN_DESK` · CONDITIONAL GO for planning · **no transfection**  
**Primary claim class:** M3 activity (not architecture)

## Goal

Measure REF(A) vs ALT(G) sequence-dependent activity at C1 outside 3D contact claims.

## Recommended reporter constructs

| Construct | GRCh38 window | Length | Files |
|-----------|---------------|-------:|-------|
| **B-min** (start here) | chr11:62753773-62754073 | 301 bp | `c1_reporter_minimal_301bp_{REF,ALT}.fa` |
| B-1kb | chr11:62753423-62754423 | 1001 bp | `c1_reporter_context_1kb_*` |
| B-2kb | chr11:62752923-62754923 | 2001 bp | `c1_reporter_context_2kb_*` |

Alleles: REF=`A`, ALT=`G` at chr11:62753923 (center/indexed).

### Backbone (desk default)

```text
Minimal promoter + insert (REF or ALT) + luciferase/fluorescent reporter
Cell: HUDEP-2 preferred; K562 acceptable for first pass
Controls: empty backbone; optional scrambled insert; C2 A>T if synthesized
```

## Endogenous secondary (only if PE available)

Nearest protein-coding genes (GRCh38, by distance to C1):

| Gene | Approx distance | Note |
|------|----------------:|------|
| ZBTB3 | ~5 kb | nearest |
| POLR2G | ~7.5 kb | RNAPII subunit — AG channel-relevant |
| TTC9C | ~14 kb | |
| TAF6L | ~17 kb | |

Do **not** claim a target gene until HUDEP-2 TSS/chromatin nominates one.

## MCID (activity desk default)

```yaml
mcid_reporter: |
  |log2(ALT/REF)| ≥ 0.5 in ≥2 independent transfections
fail: no reproducible direction across replicates
```

## Relationship to Branch A

- Same PE allele can later feed G4b; reporter does not require contact assay.  
- Keep language free of “loop disruption”.

## STOP

```text
No oligo order without wet-lab GO note
No transfection until GO
```

Meta: `BranchB_reporter_sequences_meta.json`  
FASTA under `pilot_scaffold/data/cultivation/`.
