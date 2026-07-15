# C1 vs C2 channel compare (same site)

**Site:** `chr11:62753923`  
**Alleles:** C1 `A>G` · C2 `A>T`  
**Date:** 2026-07-14  
**Status:** `COMPARE_COMPLETE`  
**Holdout:** not scored  

---

## Decision

```text
same_site_program:     SHARED (9/10 top TF·biosample pairs overlap)
direction:             ALT lowers POLR2/GABPB1/RBFOX2 (signed mean negative)
C1 vs C2 magnitude:    C1 stronger (local MAE peaks ~200 vs ~109)
architecture channels: WEAK both (best RAD21 rank ~440–476)
mechanism lean:        M3_activity for both — C2 is dose/allelic control, not M1 rescue
```

---

## Top channels

| Rank | C1 (A>G) | Local MAE | C2 (A>T) | Local MAE |
|-----:|----------|----------:|----------|----------:|
| 1 | POLR2G HepG2 | 202.8 | GABPB1 K562 | 109.0 |
| 2 | GABPB1 K562 | 188.8 | GABPB1 HepG2 | 73.8 |
| 3 | POLR2A GM15510 | 183.7 | POLR2G HepG2 | 69.2 |
| 4 | RBFOX2 HepG2 | 169.8 | RBFOX2 HepG2 | 58.7 |
| 5 | RBFOX2 K562 | 150.0 | POLR2A GM15510 | 50.9 |

Overlap top-10 TF×biosample: **9**. Interpretation: `allele_shared_activity_program`.

---

## Use in cultivation

| Role | Allele | Why |
|------|--------|-----|
| Primary ranked M3 candidate | **C1** | Strongest shared activity Δ |
| Allelic amplitude / direction control | **C2** | Same locus, weaker but same TF program |
| Neutral / M5 later | TBD | Need non-activity scrambled control at edit |

Do **not** interpret C2 as “architecture-null control” — both are M3-lean.

Artifact: `c1_c2_channel_compare.json`
