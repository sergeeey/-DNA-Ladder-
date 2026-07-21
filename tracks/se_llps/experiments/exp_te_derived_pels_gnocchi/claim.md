---
experiment: exp_te_derived_pels_gnocchi
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: SUPPORT_WITH_CAVEATS
candidate_id: C-H1
candidate_alias: C-H1-te-derived-pels-gnocchi
source: Standing order — TRUE C-H1 (NOT Micro-C; Micro-C queued as C-I1)
decision_gate: SUPPORT_ABS_DELTA
---

# Claim: TE-derived pELS differ in Gnocchi germline constraint vs matched non-TE pELS

## Status

**SUPPORT_WITH_CAVEATS** — Standard tier; desk **CLOSED** (robustness 2026-07-21).  
Primary |\Delta mean Gnocchi Z| = **0.211** ≥ 0.15 (kill was |\Delta| < 0.05).  
Core sensitivities (alt match / blacklist / chr-holdout) keep |\Δ| ≥ 0.15; **LINE-only**
split |\Δ|=0.025 → kill (SINE/LTR carry the TE-union signal).  
See `decision.md` + `results/sensitivity_result.json`.

## EstimandOps L0

**Question type:** Descriptive.

Among ENCODE SCREEN Registry-V3 **pELS** cCREs (GRCh38), do those with ≥1 bp overlap to
RepeatMasker TE classes show a different mean Gnocchi Z (gnomAD v3.1 non-coding constraint)
than **matched non-TE pELS** (matched on GC / length / distance-to-TSS)?

Explicitly **not causal**. Explicitly **not** the closed SE-vs-typical-enhancer Gnocchi
estimand (`exp_gnocchi_constraint_se_vs_typical_enhancer`, REJECT 2026-07-10). Explicitly
**not** Micro-C vs Hi-C TE recovery (parked / next as **C-I1**).

## Novelty (Gate 0)

- Closed SE Gnocchi REJECT compared **SE-constituent vs typical H3K27ac** (length-only match).
  This universe is **TE-derived pELS vs non-TE pELS** — different exposure, different cCRE
  class, GC+length+TSS matching.
- C-A2 REJECT compared SVA_F **dELS switching** (OR), not constraint Z on pELS.
- Literature: Gnocchi paper reports enhancer-class constraint broadly; no DNA Ladder prior
  on TE-derived **pELS** mean-Δ vs matched non-TE. Honest label: **[UNKNOWN]** independent
  replication / narrower sub-question vs field frontier.

## Frozen claim (pre-results)

> |\Delta mean Gnocchi Z| (TE-derived pELS − matched non-TE pELS) ≥ **0.15**

**Falsification (pre-registered):** |\Delta| < **0.05** → claim **REJECT** (`FAIL_KILL`),
same practical-null scale used for SE-track Gnocchi REJECT interpretation.

Gray zone 0.05 ≤ |\Delta| < 0.15 → **INCONCLUSIVE** / fail-to-support (not SUPPORT; not kill).

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | Registry-V3 cCREs with primary class `pELS` (chr1–22, chrX) |
| Exposure | TE-derived: ≥1 bp overlap with rmsk `repClass ∈ {SINE,LINE,LTR,DNA,Retroposon}` |
| Comparator | Non-TE pELS: zero overlap with those TE classes |
| Matching | 1:1 without replacement on `chrom` + `length_bin` + `gc_bin` + `tss_dist_bin` **before** Gnocchi attach; seed `20260720` |
| Endpoint | Length-weighted mean Gnocchi Z over overlapping QC-passed 1 kb windows (same loader as SE Gnocchi) |
| Primary summary | |\Delta| = \|mean(Z_TE − Z_matched_nonTE)\| on pairs with both sides covered |
| Secondary | Cliff's δ; bootstrap 95% CI on mean Δ; paired permutation p (10 000) |
| SUPPORT | \|\Delta\| ≥ 0.15 |
| Kill / REJECT | \|\Delta\| < 0.05 |

## Datasets

| Role | Source |
|------|--------|
| pELS universe | SCREEN Registry-V3 `GRCh38-cCREs.bed` |
| TE | UCSC hg38 `rmsk.txt.gz` |
| GC | UCSC `hg38.2bit` |
| TSS | GENCODE v47 basic protein-coding gene TSS |
| Constraint | Gnocchi QC 1 kb windows (`constraint_z_genome_1kb.qc.download.txt.gz` → local `gnocchi_constraint_z_genome_1kb_qc.txt.gz`) |

If Gnocchi file cannot be fetched → terminal **`BLOCKED_DATA`**.

## Allowed claim language

- “TE-derived pELS mean Gnocchi Δ = … vs GC/length/TSS-matched non-TE pELS.”
- “REJECT / FAIL_KILL: \|\Delta\| < 0.05.”
- “SUPPORT: \|\Delta\| ≥ 0.15.”

## Forbidden claim language

- Causal TE → constraint / enhancer fitness
- Equating this to SE-vs-typical Gnocchi REJECT or reopening that null
- Substituting Micro-C / Hi-C loop recovery as this C-H1
- Wet-lab / holdout / C1 E/P

## Status

Preregistered before outcome analysis. Decision after `results/primary_result.json`.
