# C1 CHIP_TF / contact channel unpack

**Variant:** `chr11:62753923:A:G` (C1)  
**Date:** 2026-07-14  
**Window:** 100 kb  
**Channel lean:** `M3_lean_activity_channels`  
**Holdout:** not scored  

---

## Machine decision

```text
M1 (CTCF/cohesin) channels:  WEAK in local Δ (best ~rank 476/1617)
M3 (activity/RNAPII) channels: STRONG (top local MAE)
G2 Arm B (AG ≫ motif):       CONFIRMED as non-motif; NOT confirmed as architecture
Preferred claim class:        M3 competitor LIVE — do not freeze as CTCF-anchor alone
wet-lab / G9:                 STOPPED
```

---

## Top CHIP_TF tracks (local ±16 bins MAE)

| Rank | Local MAE | TF | Biosample |
|-----:|----------:|----|-----------|
| 1 | 202.8 | POLR2G | HepG2 |
| 2 | 188.8 | GABPB1 | **K562** |
| 3 | 183.7 | POLR2A | GM15510 |
| 4 | 169.8 | RBFOX2 | HepG2 |
| 5 | 150.0 | RBFOX2 | **K562** |
| 10 | 130.5 | POLR2AphosphoS5 | **GM12878** |
| 13 | 114.1 | POLR2G | **K562** |

Pattern: polymerase II / splicing-related TFs dominate. Hematopoietic proxies (K562/GM12878) appear in the top activity set.

---

## Architecture channels (CTCF / RAD21 / SMC)

| Fact | Value |
|------|------:|
| Tracks with CTCF/RAD21/SMC* | 178 |
| Best local MAE among them | ~5.9 (RAD21 HepG2) |
| Rank of best among all 1617 | **476** |
| CTCF/RAD21 in CHIP_TF top-30 | **0** |

→ Local AG Δ is **not** CTCF-disruption-dominated for C1.

---

## Contact-map channels (global MAE)

Top biosamples by contact Δ: HFFc6, H1-hESC, IMR-90 (MAE ≈ 0.006–0.008).  
Contact Δ remains small vs CHIP_TF local spikes; consistent with G2 (contact MAE 0.0049).

---

## Interpretation vs prior G2

| Prior | Update |
|-------|--------|
| Arm B: AG ≫ motif | Still true |
| Preferred M1 (CTCF anchor) | **Downgrade** — channels favor **M3 activity** |
| C3 motif-high competitor | Still the motif-leaning allele |
| C1 cultivation role | Keep as **activity / RNAPII-sensitive** candidate; require activity assay before architecture freeze |

Discriminating next tests:

1. Unpack whether POLR2 Δ is causal vs correlated noise (replicates / other alts at same site = C2).  
2. If claiming architecture: show CTCF occupancy Δ experimentally — AG does not support it as primary channel.  
3. HUDEP-2 G4 still required for any contact claim.

---

## Non-claims

- Not wet-lab GO / not G9 / not holdout unblind / not “3D disruption”

Artifact: `c1_chip_tf_channel_unpack.json`
