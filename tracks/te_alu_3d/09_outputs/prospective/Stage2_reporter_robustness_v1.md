# Stage-2 reporter robustness desk v1

**Overall:** `REPORTER_DESK_OK_TECHNICAL`  
**Kills:** none  
**R1 note:** R1 not scored — need AG per window length before freeze of length invariance

## Frozen before wet (design lock)

```yaml
{
  "primary_window": "minimal_301bp",
  "orientation": "genomic_sense",
  "backbone": "minP_luc_or_FP_TBD_at_GO",
  "normalization": "ALT/REF ratio with empty-backbone control",
  "primary_endpoint": "|log2(ALT/REF)|>=0.5 in >=2 tx",
  "secondary_windows": [
    "context_1kb",
    "context_2kb"
  ]
}
```

## C1 technical

- edge risk 301bp: False
- max |ΔGC|: 0.0033222591362125353
- idx in 301bp: 150

Length-invariance of predicted ALT/REF: **P5 R1 DONE** — AG 16/100/500 kb signed CHIP_TF → **`R1_PASS`**  
(literal 301/1kb/2kb not AG-native; see `P5_R1_window_length_ag_v1.md`).
