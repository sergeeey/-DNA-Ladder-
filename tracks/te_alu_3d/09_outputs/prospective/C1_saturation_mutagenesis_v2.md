# C1 saturation mutagenesis v2 (expand AG)

**Overall:** `ALLELE_LEAN_RETAINED`  
**Kills:** none  
**AG scored:** 255 / 903 possible (reuse 101 + new 154)
**A→G covered:** 60 / 60 sites (incl. C1)

## Claim

`P2_SATMUT_EXPAND_CLAIM_v1.md` — same S1/S2/S3 as v1; expanded universe.

## Stats

```json
{
  "n_ag_scored": 255,
  "n_prior_reuse": 101,
  "n_new_ok": 154,
  "n_new_fail": 0,
  "n_AtoG_scored_incl_c1": 60,
  "n_AtoG_other": 59,
  "c1_chip_tf": 0.5408127170767988,
  "c1_contact": 0.00494472762303693,
  "c1_rank": 2,
  "c1_percentile_from_top": 0.00784313725490196,
  "n_within_90pct_c1": 1,
  "mean_other_AtoG_chip": 0.17766434207956763,
  "top5": [
    {
      "chip": 0.5665203205361068,
      "id": "chr11:62753922:A:G",
      "is_c1": false
    },
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
      "chip": 0.37455932815353593,
      "id": "chr11:62753989:A:G",
      "is_c1": false
    }
  ],
  "seed_random": 20260716,
  "random_n_requested": 100
}
```

## Plain language

Добавили все остальные A→G в окне 301 bp и 100 случайных замен. Если C1 всё ещё редкий выброс на этом фоне — аллельный lean держится; если толпа соседей или средний A→G догоняет — это артефакт окна.

## What this does NOT mean

- Not wet-lab proof
- Not full 903 AG
- Not holdout / Stage-3 / oligo GO

JSON: `C1_saturation_mutagenesis_v2.json`
