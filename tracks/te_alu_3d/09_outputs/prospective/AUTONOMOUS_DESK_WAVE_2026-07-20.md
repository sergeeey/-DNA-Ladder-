# Autonomous desk wave — 2026-07-20

**Status:** **STOP** — human pause recommended.  
**Master merge target:** include this file + C-L1 close on `master`.  
**Do not** auto-start C-D1 / C-E1 / C-F1 / C-G1 / C-J1 overnight without human queue.

## Wave outcomes (standing-order remaps)

| ID | True desk estimand | Path | Verdict |
|----|--------------------|------|---------|
| C-A1 | Pol II ChIA vs Hi-C AluSz discordance | `exp_te_loop_assay_discordance_chia_vs_hic/` | INCONCLUSIVE_CROSS_CELL |
| C-B1 | Topology ΔAUC over SE for CRISPR E–G (se_llps) | `exp_topology_community_crispr_eg/` | REJECT FAIL_KILL |
| C-K1 | H3K4me3 PLAC vs Hi-C Alu | `exp_plac_vs_hic_alu_anchors/` | BLOCKED_DATA |
| C-A2 | SVA_F dELS switching vs matched non-TE | `exp_sva_f_ccre_state_switching/` | REJECT FAIL_KILL |
| **C-H1** | TE-derived pELS vs matched non-TE Gnocchi | `se_llps/.../exp_te_derived_pels_gnocchi/` | **SUPPORT** \|\Δ\|=0.211 |
| **C-I1** | Micro-C vs Hi-C Alu anchors | `exp_microc_vs_hic_alu_anchors/` | **BLOCKED_DATA** |
| **C-L1** | L1HS 5′UTR @ CTCF∩Hi-C vs matched CTCF | `exp_l1hs_ctcf_loop_anchors/` | **REJECT** OR≈0.14 |

## Parked / not started (heavier)

| ID | Title (registry) | Status |
|----|------------------|--------|
| C-B1-TE-AluY-AG | AluY@CTCF+RAD21+AG | PARKED (creds) |
| C-C1 | SVA vs Alu Hi-C anchors | not started |
| C-D1 | TE age vs loop reproducibility | not started |
| C-E1 | TE vs non-TE rare-SNV PWM | not started |
| C-F1 | Mustache vs HiCCUPS TE concordance | not started — **do not auto-start** |
| C-G1 | RAD21 vs CTCF ChIA TE odds | not started |
| C-J1 | TE orientation vs anchor asymmetry | not started |
| C-L1-crosscell-original | K562→GM12878 transfer | PARKED |
| C-H1-microc-original | remapped → C-I1 | REMAPPED |
| C-I1-alujo-nc-original | AluJo NC | PARKED_AS_C-A1_CONTROL |

## Recommendation

Pause autonomous fruit queue. Human picks next among parked/heavier candidates (C-F1 if caller concordance is priority; C-L1-crosscell if transfer is priority). Holdout / C1 / wet remain untouched.
