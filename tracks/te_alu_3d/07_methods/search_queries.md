# Systematic Search Queries

Использовать: PubMed, Europe PMC, Google Scholar, bioRxiv, medRxiv, OpenAlex.

## Core TE × 3D

```text
("transposable elements" OR repeats OR retrotransposons)
AND (CTCF OR cohesin OR "loop anchor" OR "TAD boundary")
AND (human OR mammalian)
```

```text
("TE-derived CTCF" OR "repeat-derived CTCF")
AND ("chromatin loop" OR "3D genome" OR "TAD")
```

## Disease / Noncoding

```text
("noncoding variants" OR "regulatory variants")
AND ("3D genome" OR "enhancer-promoter" OR "TAD disruption")
AND disease
```

## ClinVar / gnomAD QC

```text
ClinVar AND noncoding AND under-ascertainment
```

```text
gnomAD AND mappability AND coverage AND repeats
```

```text
("transposable elements" AND "mappability" AND "short-read sequencing")
```

## HERV / Development

```text
("endogenous retrovirus" OR HERV OR LTR7 OR "HERV-H")
AND enhancer AND human development
```

## Technology

```text
("Micro-C" OR "Hi-C")
AND ("transposable elements" OR repeats)
AND chromatin
```

## Negative Evidence (explicit)

```text
CTCF AND ("no effect" OR "modest" OR "limited") AND expression
```

```text
("mapping artifact" OR "false positive") AND repeats AND variants
```

## Collection Targets by Block

| Block | Target n | Indexed | Status |
|-------|----------|---------|--------|
| TE/regulation | 30 | 9 | 🟡 |
| 3D genome/CTCF | 20 | 8 | 🟡 |
| Noncoding disease | 15 | 7 | 🟡 |
| ClinVar/gnomAD/QC | 10 | 4 | 🟡 |
| Methods/artifacts | 10 | 8 | 🟢 |
| Negative/contradiction | 10 | 6 | 🟡 |
| **Total** | **80–120** | **42** | **51%** |
