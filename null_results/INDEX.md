# Null Results Index

Shared across monorepo tracks. Historical filings below belong to **`tracks/se_llps`**
(experiment folders: `tracks/se_llps/experiments/exp_<slug>/`). New TE/Alu nulls go here too,
with track tag in the slug or body.

| ID | Date | Slug | Verdict | Why (10 words) | Track |
|---|---|---|---|---|---|
| 20260720-sva-f-dels-state-switching | 2026-07-20 | SVA_F dELS active↔inactive switching vs matched non-TE? | REJECT | OR 0.49; odd+even OR&lt;1.1 FAIL_KILL | te_alu_3d |
| 20260720-topology-community-crispr-eg-delta-auc | 2026-07-20 | CRE-community topology ΔAUC over dist+ELS+SE for CRISPR E–G? | REJECT | Holdout ΔAUC −0.007; FAIL_KILL; distance alone AUC 0.88 | se_llps |
| 20260720-te-chia-vs-hic-alusz-anchor-discordance | 2026-07-20 | AluSz enrichment Pol II ChIA-PET vs Hi-C discordant anchors? | INCONCLUSIVE | K562 FAIL; GM12878/HCT116 mid-zone; cross-cell inconsistent | te_alu_3d |
| 20260708-heritability-vus-se-frequency | 2026-07-08 | ClinVar VUS rarer inside super-enhancers? | REJECT | Cliff's delta -0.01/-0.03, neither significant nor meaningful | se_llps |
| 20260710-llps-promoter-vs-se-chip-evidence | 2026-07-10 | BRD4/MED1 favor super-enhancers over active chromatin? | REJECT | Matched H3K27ac control falsifies it; BRD4 reverses, MED1 splits 1-1, ENCODE data exhausted | se_llps |
| 20260710-gnocchi-constraint-se-vs-typical-enhancer | 2026-07-10 | Super-enhancers show different germline constraint (Gnocchi) than typical enhancers? | REJECT | Cliff's delta +0.05 (K562) vs -0.04 (HepG2), sign flips, both far below MCID 0.2 | se_llps |
| 20260710-heritability-vus-se-vs-typical-enhancer | 2026-07-10 | ClinVar VUS rarer in SE vs matched typical enhancer? | REJECT | Cliff's delta +0.008/-0.019, essentially zero, third convergent null on this direction | se_llps |
| META_missing_heritability_2026-07-10 | 2026-07-10 | Does SE membership explain missing heritability, across all 4 tests? | CLOSED | Pipeline validated (positive control delta=0.61); 3 estimands, 2 data sources converge on null | se_llps |
| 20260710-rloop-se-vs-typical-enhancer | 2026-07-10 | R-loops (DRIP-seq) more common in SE vs matched typical enhancer, K562? | REJECT | Cliff's delta -0.042, wrong-for-hypothesis direction, p at floor but n-driven not effect-driven | se_llps |
| 20260710-g4-se-vs-typical-enhancer | 2026-07-10 | G-quadruplexes (BG4 ChIP-seq) more common in SE vs typical enhancer, K562+HepG2? | REJECT | Cliff's delta -0.047/-0.024, wrong direction both lines, 5th convergent REJECT this direction | se_llps |
| 20260710-se-continuous-rank-dichotomization-check | 2026-07-10 | Does continuous SE-size (not binary membership) correlate with Gnocchi/R-loop/G4? | REJECT-with-signal | Max rho=0.163 (below 0.2 MCID) but real, robust, directionally consistent for R-loop/G4 | se_llps |
