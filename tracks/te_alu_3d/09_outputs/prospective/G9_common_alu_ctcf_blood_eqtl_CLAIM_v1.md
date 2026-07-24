# G9 — Common Alu/SVA × CTCF-peak SNPs vs blood cis-eQTL — CLAIM v1

**Pre-registration date:** 2026-07-23  
**L0 gate:** Descriptive  
**Status:** LOCKED — written before panel freeze hashes and before any eQTL association peek  
**Supersedes:** none (new estimand; not a rescue of G8 rare-panel gap)  
**Related:** `G8_activity_public_readout_decision_v1.md` (DATA_GAP_STOP unlocked this reformulation)

---

## 1. Estimand

**Measure:** Among common SNVs on chr11 (non-holdout), is the fraction with at least one
significant cis-eQTL in GTEx whole-blood gene expression higher for SNVs inside
**Alu/SVA ∩ HUDEP-2 CTCF peak** than for AF-matched SNVs inside **Alu/SVA outside CTCF peaks**?

**Population / data:**

| Role | Source |
|------|--------|
| Variants | gnomAD v4 genomes via GraphQL (same API as R4 cultivation) |
| TE | `pilot_scaffold/data/repeatmasker_chr11_alu_sva.bed` |
| CTCF | `pilot_scaffold/data/ctcf_HUDEP2_peaks.bed` (ChIP-Atlas SRX5821035) |
| Primary eQTL | eQTL Catalogue **QTD000356** — GTEx blood, `quant_method=ge` |
| Replication eQTL | eQTL Catalogue **QTD000373** — Lepik_2017 blood, `quant_method=ge` (only if primary PASS) |

**Estimand type:** Descriptive enrichment of blood cis-eQTL hit-rate.  
**Cell-type caveat (locked):** whole blood ≠ HUDEP-2 erythroblast. Positive result does **not**
imply erythroid architecture or Alu-specific CTCF disruption causality.

**NOT being tested:**

- Rare SNV panel / r4 / Stage-3 A754/A518
- Motif PWM disruption as primary classifier (peak occupancy only)
- Allele-specific Hi-C / contact
- Pathogenicity, regulation, causal language
- Holdout geography

---

## 2. Novelty

| Source | Finding |
|--------|---------|
| G8 | Rare panel × public eQTL = DATA_GAP_STOP; explicitly allowed next move = common-SNP claim |
| `null_results/` | No prior common Alu∩CTCF × blood eQTL enrichment filing |
| Research Library | No Alu×eQTL corpus (LLPS only) |
| Literature | Blood eQTL maps exist; this is an independent descriptive intersection on track chr11 TE×CTCF geography |

---

## 3. Panel freeze rules (before eQTL)

### Geography

- Chromosome: **chr11 only**
- Exclude intervals: HBB `5,200,000–5,300,000` and holdout `64,000,000–68,000,000` (same as R4)
- Holdout paths: never read

### Case definition (`CASE_CTCF_ALU`)

1. SNV (biallelic A/C/G/T) with gnomAD genome AF in **[0.05, 0.50]**
2. Position lies inside a HUDEP-2 CTCF peak (half-open BED: `start < pos ≤ end`)
3. Same position lies inside an Alu/SVA RepeatMasker interval
4. Deduplicate by `chr11:pos:ref:alt`
5. Cap **200**: sort by `pos`, `ref`, `alt`; take first 200

### Control definition (`CTRL_ALU_NONCTCF`)

1. Same AF band **[0.05, 0.50]**
2. Inside Alu/SVA
3. **Not** inside any HUDEP-2 CTCF peak expanded by **±250 bp**
4. Matched to cases by AF decile (seed=`20260722`)
5. `n_ctrl = min(n_case, 200)`

### Freeze artifact

`09_outputs/prospective/g9_common_alu_ctcf_panel_freeze_v1.json` (+ sha256)  
Must contain only genomic IDs, AF, role, TE family, peak coords — **no eQTL fields**.

---

## 4. eQTL hit rule (locked)

For each frozen variant, query eQTL Catalogue API v2:

`GET /eqtl/api/v2/datasets/{dataset_id}/associations?variant=chr11_{pos}_{ref}_{alt}&size=1000`

**Hit** if any returned association has `pvalue ≤ 5e-8` (or `nlog10p ≥ 7.3010`).  
**Miss** if API returns empty list or all p-values above threshold.  
**ERROR** (exclude from denominator) if HTTP failure after retries — report count; if
`n_error / n_queried > 0.10` → panel verdict **INCONCLUSIVE**.

Primary analysis uses **QTD000356 only**.  
Replication **QTD000373** runs **only if** primary decision is PASS.

---

## 5. Decision rule (primary)

Let `p_case = n_hit_case / n_tested_case`, `p_ctrl = n_hit_ctrl / n_tested_ctrl`.  
Test: two-sided Fisher's exact test on 2×2 hit table.

| Verdict | Rule |
|---------|------|
| **PASS** | `p_case > p_ctrl` and Fisher `p ≤ 0.01` and `n_tested_case ≥ 30` and `n_tested_ctrl ≥ 30` |
| **REJECT** | Fisher `p ≤ 0.01` and `p_case ≤ p_ctrl` **or** Fisher `p > 0.01` with both arms ≥30 and `|p_case−p_ctrl| < 0.05` |
| **INCONCLUSIVE** | Otherwise |

Allowed language if PASS: “descriptive enrichment of GTEx whole-blood cis-eQTL hit-rate among
common SNVs in Alu/SVA∩HUDEP-2 CTCF peaks vs Alu outside CTCF on chr11.”  
Forbidden: causal Alu→CTCF→expression; erythroid architecture; Stage-3 upgrade.

---

## 6. Forbidden

- Peeking at eQTL before freeze hash written
- Including rare AF < 0.05
- Reopening Stage-3 Hi-C dumps
- Holdout / oligo / wet GO
- Switching primary dataset post-hoc

---

## 7. Scripts / tests

- `pilot_scaffold/scripts/g9_eqtl_lib.py`
- `pilot_scaffold/scripts/freeze_g9_common_alu_ctcf_panel.py`
- `pilot_scaffold/scripts/run_g9_common_alu_blood_eqtl.py`
- `tests/test_g9_eqtl_lib.py`
