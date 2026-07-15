# G4b protocol draft — allele-specific ΔContact for C1 (DESK ONLY)

**Status:** `DRAFT` · not authorized · not funded  
**Depends on:** G4a PASS_DESK + P1 assay-chain + G5 edit feasible  

## Estimand

```text
ΔContact = Contact_C1 - Contact_WT  for locked (E, P) in HUDEP-2
```

Public Hi-C **cannot** open G4b. Requires genome edit + contact assay.

## Preferred assays (rank order)

1. **Capture-C / NG Capture-C** with bait covering locked E **or** P (hg19/hg38 consistent)  
2. **MCC / Micro-Capture-C** if higher resolution needed at ~300 kb E–P  
3. Genome-wide Hi-C only if depth sufficient for 10–25 kb at this locus (unlikely as sole G4b)

## Design

```yaml
cell: HUDEP-2
alleles:
  - WT parental / unedited
  - C1 A>G (PE)
  - optional C2 A>T allelic control
replicates: >=2 independent clones or cultures
baits:
  - cover locked E chr11:62390000-62395000 (GRCh38)
  - and/or locked P chr11:62690000-62695000
normalization: predefined before unblinding scores
primary_contrast: C1 vs WT at E–P pixel/strip
controls:
  - P1-local planted break (sensitivity)
  - N3 neutral (specificity)
```

## PASS (scientific)

```text
edit verified
AND Contact Δ in predicted direction
AND effect exceeds MCID
AND reproducible across replicates
AND P1-local control shows assay is not blind
```

## Fail → pivot

If assay blind to P1-local → stop architecture claim; remain on Branch B activity.
