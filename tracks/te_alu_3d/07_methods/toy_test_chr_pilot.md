# Toy Test — Chromosome Pilot (draft)

Цель: проверить pipeline mechanics на одной хромосоме до full-genome run.

## Suggested Pilot

**Chr 11** — β-globin locus (HBB ARCHCODE validation) + dense gene content + known regulatory architecture.

Alternative: **Chr 22** — small; faster iteration.

## Pilot Steps

```text
1. Extract ClinVar P/LP + gnomAD rare variants on chr11 (hg38)
2. Annotate TE overlap (RepeatMasker bed intersect)
3. Apply QC masks (mappability ≥ 0.9, blacklist, segdup)
4. Score ARCHCODE disruption for TE vs matched controls (n=20)
5. Report: n variants per stage, enrichment OR, KC1-KC4 flags
```

## Success Criteria (pilot)

| Check | Pass |
|-------|------|
| Pipeline runs end-to-end without manual fixes | |
| Control matching achieves SMD < 0.1 | |
| ≥ 10 TE-overlapping P/LP variants post-QC | |
| Permutation null calibrated (not degenerate) | |

## Outputs

```text
09_outputs/pilot_chr11/
  variant_counts.json
  enrichment_summary.csv
  qc_dropout_report.md
  manhattan_placeholder.png  # optional
```

## Do NOT

- Interpret pilot enrichment as biological conclusion
- Skip QC to "see signal faster"
- Use pilot to tune thresholds without holdout chr
