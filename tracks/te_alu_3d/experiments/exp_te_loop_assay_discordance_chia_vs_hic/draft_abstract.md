# Draft abstract — C-A1 loop-assay discordance TE enrichment

**Candidate:** C-A1 · **Track:** te_alu_3d · **Date:** 2026-07-20  
**Actual outcome:** **INCONCLUSIVE** (`INCONCLUSIVE_CROSS_CELL`)

---

## Scenario A — Positive (counterfactual; NOT observed)

If K562 AluSz OR were ≥ 1.3 after umap gating and GM12878/HCT116 replication retained
OR ≥ 1.15 in the same direction, we would report descriptive enrichment of AluSz among
Pol II ChIA-PET vs Hi-C discordant loop-anchor windows in processed public call sets,
with CTCF gates passing, and file a cautious SUPPORT_DESK→replicated note without causal
language. **This scenario did not occur.**

## Scenario B — Negative / REJECT (counterfactual; NOT fully met)

If K562 OR remained < 1.1 after mappability **and** both replication arms fell < 1.15 or
flipped sign, we would file claim-level REJECT and close the assay-blind-spot enrichment
hypothesis for AluSz. **Replication arms did not enter that falsify zone** (GM12878 ≈ 1.25;
HCT116 ≈ 1.28).

## Scenario C — Actual: INCONCLUSIVE

Across K562, GM12878, and HCT116, AluSz odds ratios for Pol II ChIA-PET versus Hi-C loop
anchors (1 kb midpoint windows, GRCh38) were inconsistent in sign and magnitude: K562
primary OR ≈ 0.91 (FAIL below 1.1; umap and DELTA caller-swap remain ≈ 0.90–0.91), while
GM12878 ≈ 1.25 and HCT116 ≈ 1.28 sit in the mid-zone below MCID 1.3. CTCF positive-control
gates passed in all tested lines. We therefore close the desk experiment as
**INCONCLUSIVE_CROSS_CELL**, file an **INCONCLUSIVE** null_results note (not REJECT), and
forbid causal TE→loop, wet-lab, holdout, or C1 overclaim language.
