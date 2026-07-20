# Null result — TE AluSz anchor discordance (Pol II ChIA-PET vs Hi-C)

**Date:** 2026-07-20  
**Track:** `te_alu_3d`  
**Experiment:** `tracks/te_alu_3d/experiments/exp_te_loop_assay_discordance_chia_vs_hic/`  
**Candidate:** C-A1  
**Verdict:** **INCONCLUSIVE** (desk closed as `INCONCLUSIVE_CROSS_CELL`)  
**Not:** REJECT (replication arms not in falsify zone; caller-swap does not flip to global null)

## Pre-registered claim (frozen)

In K562, AluSz OR ≥ **1.3** for Pol II ChIA-PET vs Hi-C discordant/matched loop-anchor
comparison, with independent replication supporting direction (OR ≥ 1.15).

**Falsification (claim.md):** after mappability gate, OR < 1.1 **and** replication OR < 1.15
or opposite → REJECT.

## Result summary

| Arm | OR | Interpretation |
|-----|-----|----------------|
| K562 HiCCUPS | 0.908 | FAIL primary (< 1.1) |
| K562 umap ≥ 0.3 | 0.898 | strengthens FAIL |
| K562 DELTA caller-swap | 0.913 | FAIL robust (Mustache N/A) |
| GM12878 | 1.252 | mid-zone (1.15–1.3) |
| HCT116 | 1.280 | mid-zone (1.15–1.3) |

CTCF positive-control gates **PASS** on all tested cells.

**Why INCONCLUSIVE not REJECT:** Primary K562 enrichment claim failed, but replication does
not enter the preregistered falsify zone on either independent cell type. Cross-cell sign
is inconsistent; that blocks SUPPORT and also blocks a clean global REJECT of the broader
“assay blind-spot enrichment” story.

## What this does NOT mean

1. Does **NOT** mean TE insertions are proven irrelevant to 3D contacts in every cell type —
   only that the frozen K562 AluSz MCID claim failed and replication is mid-zone / sign-mixed.
2. Does **NOT** authorize causal language (TE drives / creates / disrupts loops).
3. Does **NOT** license wet-lab GO, oligo order, holdout unblind, or C1 E/P edits.
4. Does **NOT** reopen closed SE/LLPS or HBB TE enrichment directions.
5. Does **NOT** promote exploratory secondary subfamilies (AluJo, SVA_F) to primary claim.
6. Does **NOT** mean HiCCUPS is “wrong” because intact-localizer sensitivity OR ≈ 1.11 —
   that is a different assay+caller path, not a Mustache/HiCCUPS rescue of primary SUPPORT.
7. Does **NOT** convert GM12878/HCT116 mid-zone OR into SUPPORT (both < MCID 1.3).

## Recommendation

Close C-A1 desk. Next fruit: see experiment `NEXT_FRUIT_NOTE.md` (recommend **C-B1** over
C-K1; do not auto-start without human queue). STOP only if credentials / AG overlay for
C-B1 remain blocked.
