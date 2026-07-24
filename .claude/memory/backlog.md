# Backlog — DNA Ladder (scope-guard log)

## Rejected scope items

### 2026-07-24 — Further DHS threshold / peak-set fishing after G12b

**Rejected because:** G12 PASS + G12b INCONCLUSIVE already bound the accessibility story
(CTCF-driven, no Alu residual under α=0.01). Changing DNase accessions or α post-hoc is fishing.

**Return condition:** New accessibility modality (e.g. HUDEP-2 ATAC independent call set)
with CLAIM before peek; OR wet B0; OR EGA eQTL.

### 2026-07-24 — Extra GTEx tissues on same G9c panel after blood+LCL REJECT

**Rejected because:** G9c (blood) and G11 (LCL) both REJECT with negligible risk_diff.
Adding liver/spleen/etc. after seeing two nulls is tissue fishing on a fixed panel.

**Return condition:** New panel freeze OR EGA erythroblast unlock with CLAIM before peek.

### 2026-07-22 — Panel×blood-eQTL effect lookup after G8 POWER_FAIL

**Rejected because:** r4_panel is 12/12 AF < 0.01; open blood eQTL maps are common-variant. Looking up p-values would produce non-informative “not tested” nulls dressed as biology. Gate verdict is DATA_GAP_STOP (`G8_activity_public_readout_decision_v1.md`).

**Return condition:** (a) open erythroid MPRA/caQTL covering rare Alu/SVA; OR (b) EGA unlock for erythroblast eQTL + rare-variant plan; OR (c) new L0 claim for **common** Alu CTCF SNPs × blood eQTL with fresh panel freeze before any peek.

### 2026-07-21 — Further desk analysis on GSM4873113 after INCONCLUSIVE Stage-3 G4a WT contact

**Rejected because:** PAUSE_PIN 2026-07-21 explicitly states "no new desk analysis unlocked by INCONCLUSIVE panel verdict." Single-replicate data exhausted at all pre-registered anchors and resolutions; A754 tol=0 downgrade (PASS→FAIL) makes threshold re-exploration post-hoc fishing.

**Return condition:** (a) human signs B0 → wet-lab path opens; OR (b) user explicitly authorises a new pre-registered claim on an independent public HUDEP-2 Hi-C / Micro-C dataset (not GSM4873113).

### 2026-07-21 — Seeking alternative threshold or background definition to rescue A754 10 kb PASS

**Rejected because:** The sensitivity side-car (tol=0) was already the pre-authorized post-analysis advisory. Changing thresholds or background definitions further to recover a PASS is p-hacking on a pre-registered result.

**Return condition:** New independent dataset only, new pre-registration before any data access.
