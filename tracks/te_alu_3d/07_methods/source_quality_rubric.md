# Source Quality Rubric

Оценка `quality_score` (1–5) для каждой записи в `evidence_matrix.csv`.

## Шкала

| Score | Label | Критерии |
|-------|-------|----------|
| **5** | Definitive | Peer-reviewed; primary data + public coordinates; direct TE×3D claim; reproduced or meta-analytic |
| **4** | Strong | Peer-reviewed; clear methods; relevant to RQ; limitations stated |
| **3** | Adequate | Review or solid computational; indirect evidence; some gaps |
| **2** | Weak | Preprint without validation; small n; overclaiming; heavy ascertainment |
| **1** | Exclude / caution | Narrative only; no methods; superseded; known artifact source |

## Модификаторы (+/−)

| Factor | Adjustment |
|--------|------------|
| Open data (GEO, 4DN, ENCODE) | +0.5 (cap at 5) |
| Direct contradiction with higher-score source | −1 |
| Negative / null result explicitly reported | +0.5 (valuable for contradiction map) |
| ClinVar-only clinical series without molecular validation | −1 |
| Repeat / mapping QC explicitly addressed | +0.5 |

## Source Type Weights

| source_type | Default cap | Notes |
|-------------|-------------|-------|
| experimental | 5 | Gold for mechanism |
| computational | 4 | Needs validation layer |
| review | 4 | Context, not primary evidence |
| database | 3 | Metadata quality varies |
| preprint | 3 | Upgrade after peer review |

## must_read Flag

`true` if ANY:
- Directly defines TE × CTCF × 3D intersection
- Defines ClinVar/gnomAD limitations for noncoding/repeats
- Provides reusable dataset for pipeline
- Documents negative evidence or artifact case

## Reviewer Checklist

```text
[ ] key_claim is one falsifiable sentence
[ ] relation_to_hypothesis is explicit (supports/contradicts/neutral/methods)
[ ] limitations field non-empty
[ ] genome_build recorded if coordinates used
[ ] contradicts field checked against contradiction_map
```

## Red Flags (auto quality_score ≤ 2)

- No accessible methods section
- Claims clinical pathogenicity without functional assay
- TE variants analyzed without mappability control
- "Junk DNA" narrative without empirical anchor
