# P1-local planted control — design sketch (near C1)

**Status:** DESIGN_ONLY  
**Need:** if Branch A advances after P1-system PASS; local control often more informative than distant 3′HS1.

## Goal

Detectability check for the chosen contact assay at the C1 neighborhood:

```text
planted break at nearest CTCF/cohesin anchor to locked E or P
→ same Capture-C / Micro-C / Hi-C assay as C1 plan
→ expected direction pre-registered
```

## Candidate search (desk, GRCh38)

Region of interest (locked neighborhood):

```text
chr11:62,300,000–62,850,000
```

### Nearest K562 CTCF peaks (ENCFF710VEH proxy — not HUDEP-2)

| Anchor | Nearest peak | Signal | Distance |
|--------|--------------|-------:|---------:|
| E mid | chr11:62395253-62395469 | 32.6 | ~2.8 kb |
| E (stronger) | chr11:62379961-62380183 | 380.9 | ~12 kb |
| P mid | chr11:62690572-62690788 | 63.0 | ~1.7 kb |
| P (stronger) | chr11:62673547-62673691 | 361.0 | ~19 kb |
| C1 | chr11:62742674-62742890 | 53.7 | ~11 kb |

**K562 proxy nominates (demoted unless HUDEP-2-confirmed):**

1. `chr11:62673547-62673691` (K562 strong near P) — HUDEP-2 confirm **FAIL**  
2. `chr11:62379961-62380183` (K562 strong near E) — HUDEP-2 confirm **FAIL**  
3. `chr11:62395253-62395469` (K562 near E) — HUDEP-2 **PASS** (±~300 bp)

**HUDEP-2-native planted-P1 (authoritative — see `P1_local_HUDEP2_CTCF_confirm_v1.md`):**

1. **P-side ChIP** GRCh38 `chr11:62694751-62695044` (hg19 62462223-62462516)  
2. **E-side CUT&RUN** GRCh38 `chr11:62394924-62395053` (hg19 62162396-62162525) — at locked E edge  

Sources: GSM3671075 (ChIP), GSM2805379 (CUT&RUN), GSE104676.

## PASS criteria (same as system P1)

```text
edit verified
AND CTCF occupancy ↓ (or motif orientation change)
AND Contact(E,P) changes in predicted direction
AND reproducible across replicates
```

## Relationship to 3′HS1 P1-system

| Control | Purpose |
|---------|---------|
| 3′HS1 system | Proves HUDEP-2 + Hi-C/Capture assay chain works |
| Local planted | Calibrates effect size / sensitivity at C1 locus |

Do not substitute literature 3′HS1 for local control when quantifying C1 architecture effect magnitude.
