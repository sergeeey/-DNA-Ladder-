# P1-local — HUDEP-2 CTCF confirmation v1

**Date:** 2026-07-15  
**Sources:** GSM2805379 (CUT&RUN CTCF HUDEP-2), GSM3671075 (ChIP CTCF HUDEP-2), GSE104676; peaks hg19  
**Nominees:** from K562 ENCFF710VEH shortlist, lifted GRCh38→hg19

| ID | GRCh38 | hg19 | CUT&RUN | ChIP | Confirm |
|----|--------|------|---------|------|---------|
| E_strong | chr11:62379961-62380183 | chr11:62147433-62147655 | peak 62162396-62162525 dist=14852 score=25.1 | peak 62148228-62148576 dist=684 score=22.2 | **FAIL** |
| E_near | chr11:62395253-62395469 | chr11:62162725-62162941 | peak 62162396-62162525 dist=308 score=25.1 | peak 62162340-62162575 dist=258 score=13.5 | **PASS** |
| P_strong | chr11:62673547-62673691 | chr11:62441019-62441163 | peak 62439764-62439960 dist=1131 score=9.2 | peak 62448270-62448615 dist=7179 score=23.1 | **FAIL** |
| P_near | chr11:62690572-62690788 | chr11:62458044-62458260 | peak 62462305-62462433 dist=4153 score=26.4 | peak 62462223-62462516 dist=4071 score=24.4 | **FAIL** |
| C1_near | chr11:62742674-62742890 | chr11:62510146-62510362 | peak 62521280-62521406 dist=11026 score=12.2 | peak 62500372-62500553 dist=9701 score=6.6 | **FAIL** |

## Decision

HUDEP-2-confirmed planted-P1 nominees: **E_near**

Primary pick: prefer strongest signal among PASS near P (promoter-side of locked E–P).

Still DESIGN_ONLY — no CRISPR order.

JSON: P1_local_HUDEP2_CTCF_confirm_v1.json

## HUDEP-2-native peak search (not K562-only)

Within 50 kb of locked E/P (hg19), strongest peaks:

- **P1_local_P_side_CUTRUN**: hg19 [62462305, 62462433] score=26.44881 dist=2397 → GRCh38 [62694833, 62694961]
- **P1_local_P_side_ChIP**: hg19 [62462223, 62462516] score=24.38423 dist=2397 → GRCh38 [62694751, 62695044]
- **P1_local_E_side_CUTRUN**: hg19 [62162396, 62162525] score=25.08526 dist=2488 → GRCh38 [62394924, 62395053]
- **P1_local_E_side_ChIP**: hg19 [62192174, 62192544] score=35.55931 dist=32387 → GRCh38 [62424702, 62425072]

### Frozen planted-P1 nominees (HUDEP-2 CTCF)

| Priority | Anchor side | hg19 peak | GRCh38 peak | Evidence |
|----------|-------------|-----------|-------------|----------|
| 1 (preferred) | P | chr11:62462223-62462516 | chr11:62694751-62695044 | ChIP score=24.4, dist=2397 |
| 2 | E | chr11:62192174-62192544 | chr11:62424702-62425072 | ChIP score=35.6, dist=32387 |
| 3 backup | P | chr11:62462305-62462433 | chr11:62694833-62694961 | CUT&RUN score=26.4, dist=2397 |
| 4 backup | E | chr11:62162396-62162525 | chr11:62394924-62395053 | CUT&RUN score=25.1, dist=2488 |

**Decision:** P1-local design may proceed with HUDEP-2 ChIP peak on **P-side** as primary planted break target; E-side as alternate.
K562-only nominees demoted unless they coincide with HUDEP-2 peaks (only E_near passed ±500 bp rule).
