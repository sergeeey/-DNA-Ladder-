# Null Results Index

Shared across monorepo tracks. Historical filings below belong to **`tracks/se_llps`**
(experiment folders: `tracks/se_llps/experiments/exp_<slug>/`). New TE/Alu nulls go here too,
with track tag in the slug or body.

| ID | Date | Slug | Verdict | Why (10 words) |
|---|---|---|---|---|
| 20260708-heritability-vus-se-frequency | 2026-07-08 | ClinVar VUS rarer inside super-enhancers? | REJECT | Cliff's delta -0.01/-0.03, neither significant nor meaningful |
| 20260710-llps-promoter-vs-se-chip-evidence | 2026-07-10 | BRD4/MED1 favor super-enhancers over active chromatin? | REJECT | Matched H3K27ac control falsifies it; BRD4 reverses, MED1 splits 1-1, ENCODE data exhausted |
| 20260710-gnocchi-constraint-se-vs-typical-enhancer | 2026-07-10 | Super-enhancers show different germline constraint (Gnocchi) than typical enhancers? | REJECT | Cliff's delta +0.05 (K562) vs -0.04 (HepG2), sign flips, both far below MCID 0.2 |
| 20260710-heritability-vus-se-vs-typical-enhancer | 2026-07-10 | ClinVar VUS rarer in SE vs matched typical enhancer? | REJECT | Cliff's delta +0.008/-0.019, essentially zero, third convergent null on this direction |
| META_missing_heritability_2026-07-10 | 2026-07-10 | Does SE membership explain missing heritability, across all 4 tests? | CLOSED | Pipeline validated (positive control delta=0.61); 3 estimands, 2 data sources converge on null |
| 20260710-rloop-se-vs-typical-enhancer | 2026-07-10 | R-loops (DRIP-seq) more common in SE vs matched typical enhancer, K562? | REJECT | Cliff's delta -0.042, wrong-for-hypothesis direction, p at floor but n-driven not effect-driven |
| 20260710-g4-se-vs-typical-enhancer | 2026-07-10 | G-quadruplexes (BG4 ChIP-seq) more common in SE vs typical enhancer, K562+HepG2? | REJECT | Cliff's delta -0.047/-0.024, wrong direction both lines, 5th convergent REJECT this direction |
