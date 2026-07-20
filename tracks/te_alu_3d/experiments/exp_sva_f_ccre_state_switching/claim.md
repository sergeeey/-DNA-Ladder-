---
experiment: exp_sva_f_ccre_state_switching
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: REJECT
candidate_id: C-A2
candidate_alias: C-A2-sva-f-dels-switching
source: Deep Research standing order — TRUE C-A2 (NOT ChIA-PET / NOT C-K1-CTCF-chia-fallback)
decision_gate: FAIL_KILL
null_results: null_results/20260720-sva-f-dels-state-switching.md
---

# Claim: SVA_F-derived dELS active↔inactive switching vs matched non-TE dELS

## Status

**REJECT** (`FAIL_KILL`) — Standard tier; desk **CLOSED**.  
Primary Fisher OR ≈ **0.489** (CI 0.243–0.985) ≪ MCID 1.4; odd+even panels both OR &lt; 1.1.
Matching covariates and switcher definition were frozen **before** switching-outcome
analysis (see `results/matching_lock.json`). ChIA-PET AluSz discordance remains **out of
scope** (parked as `C-K1-CTCF-chia-fallback`).

## EstimandOps L0

**Question type:** Descriptive.

Among ENCODE SCREEN / encyclopedia **dELS** cCREs (GRCh38), is membership in the
**SVA_F-overlapping** set associated with higher odds of being a cross-cell-type **switcher**
(active in some biosamples, inactive in others) than a **1:k matched non-TE dELS** null,
matched on GC / length / distance-to-TSS / baseline signal **before** switcher labels are
computed?

Explicitly **not causal**. Explicitly **not** enhancer↔silencer mechanism language beyond
the operational active/inactive rule below. Explicitly **not** C-A1 / C-K1 loop-assay claims.

## Frozen claim (pre-results)

> OR(switcher | SVA_F-overlapping dELS) ≥ **1.4** vs 1:k matched non-TE dELS across the
> frozen ENCODE v3 Full-classification cell-type panel.

**Falsification (pre-registered):** OR **< 1.1** in **≥2** independent cell-type sub-panels
(odd-index vs even-index biosamples from the frozen ordered panel) → claim **REJECT**
(`FAIL_KILL`).

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | Registry dELS cCREs (SCREEN Registry-V3 `GRCh38-cCREs.bed`, class contains `dELS`) |
| Exposure | ≥1 bp overlap with RepeatMasker `repName=SVA_F` (UCSC hg38 `rmsk`) |
| Comparator | Non-TE dELS: no overlap with RepeatMasker TE classes `{SINE,LINE,LTR,DNA,Retroposon}` |
| Matching | 1:k (k=5) on chrom + length_bin + gc_bin + tss_dist_bin + baseline_signal; **before** outcomes |
| Outcome | Binary **switcher** (definition below) |
| Summary | Fisher OR + Woolf 95% CI (SVA_F vs matched non-TE) |
| MCID (SUPPORT) | OR ≥ 1.4 |
| Kill | OR < 1.1 in ≥2 independent sub-panels |

## Switcher definition (ONE pre-specified)

Let \(N\) = number of frozen **switching-panel** biosamples (held-out baseline biosample
excluded; see `controls.md`). Let \(A\) = count of biosamples where the cCRE is **active**.

**Active** in biosample \(C\): ENCODE cell-type cCRE bed column 10 (classification) equals
`dELS` or starts with `dELS,` (e.g. `dELS,CTCF-bound`). Column 11 must be
`All-data/Full-classification`. All other labels → **inactive**.

**Switcher** iff \(A \ge 1\) **and** \((N - A) \ge 3\)  
(i.e. active in ≥1 and inactive in ≥3 cell types).

Not used as primary: variance of activity; “active in 1–3 of N” alone; enhancer↔silencer
ChIP state beyond this SCREEN rule.

## Datasets (T0 freeze targets)

| Role | Source | Notes |
|------|--------|-------|
| Agnostic cCRE registry | SCREEN Registry-V3 `https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.bed` | dELS filter |
| Cell-type activity | ENCODE encyclopedia **v3 current** Full-classification beds (frozen list in `ACCESSION_FREEZE_v1.md`) | No single SCREEN multi-cell matrix file; panel of processed beds |
| TE | UCSC hg38 `rmsk.txt.gz` | `SVA_F`; non-TE = no TE-class overlap |
| TSS | GENCODE v47 basic protein-coding gene TSS (GRCh38) | distance-to-TSS |
| Sequence / GC | UCSC hg38.2bit (or chrom FASTA) | GC% for matching |
| Baseline signal | Held-out biosample **SK-N-SH** `ENCFF948UCK` binary active (dELS*) | Matching only; **excluded** from switching \(N\) |

If Registry-V3 or ≥8 Full-classification cell-type beds cannot be obtained → terminal
`BLOCKED_DATA` (still merge prereg); recommend next fruit **C-H1** or **C-L1**.

## Allowed claim language

- “SVA_F dELS switcher Fisher OR = … vs matched non-TE (descriptive SCREEN states).”
- “REJECT / FAIL_KILL: OR < 1.1 on ≥2 sub-panels.”
- “BLOCKED_DATA: SCREEN multi-cell panel unavailable.”

## Forbidden claim language

- Causal SVA_F → enhancer switching mechanism
- Substituting ChIA-PET / Hi-C AluSz discordance as this C-A2
- Using switcher labels or switching-panel activity inside the matching step
- Reopening C-A1 / C-K1 / SE nulls / wet / holdout / C1 E/P

## Novelty note

- Distinct from parked `C-K1-CTCF-chia-fallback` (CTCF ChIA-PET vs Hi-C AluSz).
- Distinct from C-A1 Pol II ChIA-PET discordance and C-K1 PLAC BLOCKED_DATA.
- Desk tests a regulatory-state switching estimand on public SCREEN/ENCODE cCRE
  annotations + RepeatMasker SVA_F.

## What this does NOT mean

1. NOT proof that SVA_F “causes” enhancer silencing.  
2. NOT a claim about sequence-editability or disease.  
3. NOT wet / holdout / C1 license.
