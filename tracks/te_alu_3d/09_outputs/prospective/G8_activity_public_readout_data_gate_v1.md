# G8 — Activity public-readout data-availability gate v1

**Date:** 2026-07-22  
**Track:** `tracks/te_alu_3d`  
**L0:** Descriptive (gate only — no effect estimand evaluated)  
**Status:** COMPLETE  
**Related claim:** `G8_activity_public_readout_CLAIM_v1.md`  
**Decision:** `G8_activity_public_readout_decision_v1.md`

---

## Purpose

Before any intersection of Alu/SVA CTCF-disruption candidates with MPRA / caQTL /
eQTL / CRISPR-screen readouts, freeze a **data-availability** verdict. This gate
does **not** look up association p-values or effect sizes for panel variants.

Intended estimand (only if gate PASS): among pre-frozen rare Alu/SVA CTCF-
disruption candidates, is cis activity / expression / accessibility signal
enriched vs matched non-disruption Alu/SVA controls in an erythroid-relevant
public map?

---

## Candidate panel AF snapshot (eligibility, not effects)

Source: `pilot_scaffold/data/cultivation/r4_panel.json` (n=12).

| Metric | Value |
|--------|------:|
| AF == 0 or missing | 5 |
| AF < 0.01 | **12 / 12** |
| AF ≥ 0.01 | **0 / 12** |

Implication: common-variant cis-eQTL / caQTL maps are **structurally underpowered**
for this panel even when open FTP exists. A null overlap would be
**non-informative** (variants not tested), not a biological falsification.

Architecture Stage-3 slots (A754, A518) are **out of scope** for this gate —
Stage-3 contact branch is CLOSED (`null_results/20260721-te-alu-stage3-architecture-contact.md`).

---

## Dataset survey (open public only)

| Class | Candidate resource | Cell / system | Open sumstats? | Covers rare Alu/SVA CTCF SNV panel? | Gate |
|-------|-------------------|---------------|----------------|-------------------------------------|------|
| MPRA genome-wide Alu/SVA | — | HUDEP-2 / erythroid | **None found** | No | **FAIL** |
| satMutMPRA | Kircher GSE126550 (PKLR) | K562 | Partial (locus) | Single locus; not Alu panel | **FAIL** (wrong estimand) |
| Motif-disruption MPRA | Kheradpour GSE33367 | K562 | Historic | 7 motifs; CTCF not among them; not rare Alu | **FAIL** |
| Erythroblast eQTL | BLUEPRINT erythroblast RNA | Erythroblast | **EGA / DAC** | Access-controlled; not used | **BLOCKED** |
| Blood cis-eQTL | eQTL Catalogue GTEx blood QTD000356; eQTLGen; SABR | Whole blood | Yes (FTP/S3) | Common-variant maps; panel all rare | **POWER_FAIL** |
| Immune sc-eQTL | TenK10K Zenodo | Immune (not erythroid) | Yes (large) | Rare tests exist but wrong lineage | **FAIL** (cell mismatch) |
| caQTL erythroid | Aggregated caQTL resources | Mostly non-HUDEP-2 | Mixed | No Alu/SVA rare CTCF panel | **FAIL** |
| CRISPR / PRO-seq | GSE201820 CTCF-AID; BCL11A locus screens | HUDEP-2 | Locus / already used | Not genome-wide Alu SNV panel | **FAIL** |

Searches: GEO/ENCODE/eQTL Catalogue metadata (2026-07-22); no credentialed EGA
fetch; no effect lookup for `r4_panel` coordinates.

---

## Pre-registered gate rule

| Code | Condition | Next action |
|------|-----------|-------------|
| `PASS` | Open erythroid/HUDEP-2 MPRA **or** erythroid caQTL/eQTL with documented rare-variant coverage overlapping ≥50% of panel + matched controls | Proceed to novelty → effect CLAIM → intersection |
| `POWER_FAIL` | Only common-variant blood maps open; panel 100% AF<0.01 | **STOP** — do not look up effects |
| `BLOCKED` | Only EGA/DAC data fits cell type | **STOP** until human unlocks access |
| `FAIL` | No fitting open resource | **STOP** |

**Observed:** `FAIL` on ideal resources + `POWER_FAIL` on open blood eQTL +
`BLOCKED` on BLUEPRINT erythroblast → composite **`DATA_GAP_STOP`**.

---

## Explicit non-goals of this gate

- No p-value / beta / PIP lookup for any panel variant
- No reopen of Stage-3 Hi-C on GSM4873113 / GSE201820 same anchors
- No holdout access; no oligo order; no wet-lab GO
- No silent reformulation to common Alu CTCF SNPs inside this document
  (that would be a **new** L0 claim with a new panel freeze)

---

## Unlock conditions (future)

Any one of:

1. Open HUDEP-2 / primary erythroblast MPRA or caQTL covering Alu/SVA rare SNVs
2. Human-approved EGA access to BLUEPRINT erythroblast eQTL + rare-variant analysis plan
3. New L0 claim for **common** Alu/SVA CTCF-overlapping SNPs × blood eQTL
   (different population; must freeze panel before any effect peek)

---

## Machine summary

```json
{
  "gate_id": "G8_activity_public_readout_data_gate_v1",
  "date": "2026-07-22",
  "composite_verdict": "DATA_GAP_STOP",
  "panel_af_ge_0.01": 0,
  "panel_n": 12,
  "ideal_resource": "FAIL",
  "open_blood_eqtl": "POWER_FAIL",
  "blueprint_erythroblast": "BLOCKED",
  "effect_lookup_performed": false
}
```
