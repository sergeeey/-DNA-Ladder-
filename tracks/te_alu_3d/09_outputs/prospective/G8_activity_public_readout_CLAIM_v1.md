# G8 — Rare Alu/SVA activity public-readout — CLAIM v1

**Pre-registration date:** 2026-07-22  
**L0 gate:** Descriptive  
**Status:** LOCKED — written before any panel×readout effect lookup  
**Supersedes:** none  
**Related:** `G8_activity_public_readout_data_gate_v1.md`  
**Predecessor branch:** Stage-3 contact CLOSED
(`null_results/20260721-te-alu-stage3-architecture-contact.md`)

---

## 1. Estimand (conditional)

**Only if data gate = PASS:**

**Measure:** enrichment of significant cis activity / expression / accessibility
signals among rare Alu/SVA CTCF-disruption candidates vs matched Alu/SVA
controls in a pre-declared open public map.

**Population:** HUDEP-2 or primary erythroid MPRA / caQTL / eQTL (preferred);
whole-blood eQTL allowed only if gate explicitly upgrades with a written
cell-mismatch caveat and rare-variant coverage proof.

**NOT being tested:**

- Causal regulation or pathogenicity
- Allele-specific Hi-C / 3D contact (Stage-3 closed)
- Wet-lab GO / oligo order
- Holdout variants
- Architecture / enhancer–promoter language

---

## 2. Mandatory sequence (locked)

1. **Data-availability gate** (`G8_activity_public_readout_data_gate_v1.md`)
2. **Novelty check** (Research Library + `null_results/` + literature)
3. If gate ≠ PASS → **STOP** with decision `DATA_GAP_STOP`; **forbid** effect lookup
4. If gate = PASS → freeze readout accession + panel IDs + matched controls → run test
5. Independent replication or honest null filing

---

## 3. Panel (eligibility freeze for this claim)

Primary eligibility set: `r4_panel.json` Alu/SVA rare SNVs (n=12), all AF < 0.01.  
Matched controls: reuse P3 matched-null design principles
(`P3_matched_null_CLAIM_v1.md`) if a PASS gate ever unlocks intersection —
**not executed under DATA_GAP_STOP**.

Stage-3 architecture slots A754/A518: **excluded** (contact branch closed;
no same-data rescue).

Holdout: **SEALED**.

---

## 4. Decision rule (pre-registered)

| Gate outcome | Claim outcome | Effect analysis |
|--------------|---------------|-----------------|
| PASS | Proceed to intersection under a dated analysis pin | Allowed after freeze |
| POWER_FAIL | `DATA_GAP_STOP` | **Forbidden** |
| BLOCKED | `DATA_GAP_STOP` (access) | **Forbidden** until unlock |
| FAIL | `DATA_GAP_STOP` | **Forbidden** |

No peeking at eQTL/MPRA statistics for panel coordinates before gate decision.

---

## 5. Novelty (locked with claim)

| Source | Finding |
|--------|---------|
| `null_results/` | No prior filing for Alu/SVA rare SNV × public MPRA/caQTL/eQTL activity enrichment; Stage-3 contact null is a different estimand |
| Research Library (`D:\Research Library\sources\`) | Corpus is LLPS/transcription condensates only; **no** Alu/SVA×eQTL/MPRA sources indexed |
| Literature (desk, 2026-07-22) | Public blood eQTL maps (GTEx/eQTL Catalogue/eQTLGen/SABR) and locus MPRA exist; **no** open HUDEP-2 genome-wide MPRA of rare Alu/SVA CTCF SNVs identified |

Novelty status for the *intended* estimand: **open gap in public data**, not
“already falsified in-repo.” Running a common-variant blood eQTL enrichment on
a rare panel would be a **non-novel methodological mistake** (power fail), not
an independent replication.

---

## 6. Forbidden paths

- Same-data Stage-3 Hi-C rescue (GSM4873113 / GSE201820 anchors)
- Looking up panel variant p-values “just to see” after POWER_FAIL
- Silent switch to common Alu SNPs without a new CLAIM
- Unblinding holdout; oligo_order; wet purchase

---

## 7. Allowed language if STOP

- “Public erythroid activity readout for this rare panel is unavailable / underpowered”
- “Computational activity branch stopped at data gate”

**Forbidden language:** “variants have no expression effect”; “Alu CTCF hypothesis falsified by eQTL”; “ready for MPRA purchase” (B0 still UNSIGNED).
