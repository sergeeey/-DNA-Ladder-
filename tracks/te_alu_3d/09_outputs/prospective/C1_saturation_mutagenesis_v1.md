# C1 saturation mutagenesis v1 (301 bp)

**Overall:** `ALLELE_LEAN_RETAINED`  
**Kills:** none  
**AG scored:** 101 / 903 possible

## Pre-registered kill criteria

- S1: C1 not in top 5% by CHIP_TF
- S2: ≥20 peers within 90% of C1 CHIP_TF
- S3: mean other A→G CHIP_TF ≥ C1

## Stats

```json
{
  "n_ag_scored": 101,
  "c1_chip_tf": 0.5408127170767988,
  "c1_contact": 0.00494472762303693,
  "c1_rank": 1,
  "c1_percentile_from_top": 0.009900990099009901,
  "n_within_90pct_c1": 0,
  "mean_other_AtoG_chip": 0.15475044509991495,
  "top5": [
    {
      "chip": 0.5408127170767988,
      "id": "chr11:62753923:A:G",
      "is_c1": true
    },
    {
      "chip": 0.4310308443445738,
      "id": "chr11:62753865:C:G",
      "is_c1": false
    },
    {
      "chip": 0.3824034191313244,
      "id": "chr11:62753960:C:T",
      "is_c1": false
    },
    {
      "chip": 0.3634613169220103,
      "id": "chr11:62753860:C:G",
      "is_c1": false
    },
    {
      "chip": 0.35315620832850186,
      "id": "chr11:62753860:C:T",
      "is_c1": false
    }
  ]
}
```

JSON: `C1_saturation_mutagenesis_v1.json`

Does not prove wet biology; only allele-vs-window artifact test.
