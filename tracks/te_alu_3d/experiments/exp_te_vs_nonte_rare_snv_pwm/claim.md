---
experiment: exp_te_vs_nonte_rare_snv_pwm
date: 2026-07-21
ladder_tier: Standard
question_type: Descriptive
status: REJECT_CLOSED
candidate_id: C-E1
candidate_alias: C-E1-te-vs-nonte-rare-snv-pwm
source: Deep Research registry — mappability-matched TE vs non-TE rare-SNV PWM Δ (non-HBB)
decision_gate: FAIL_KILL
---

# Claim: Mappability-matched TE vs non-TE rare-SNV PWM Δ (non-HBB desk)

## Status

**REJECT** (`FAIL_KILL`) — 2026-07-21. Primary Cliff's δ = **0.033** (< 0.05 kill)
after umap-quartile matching on chr11 CTCF-neighborhood rare SNVs (non-HBB, non-HO).

T0 freeze held: claim written before PWM Δ; fetch + match-before-PWM then primary.

## EstimandOps L0

**Question type:** Descriptive.

Among **rare SNVs** (AF ≤ 0.001) outside the HBB development window and outside the
**SEALED** holdout (`HO_A/B/C`), after **mappability matching** (Hoffman umap k100
quartile), is the distribution of exploratory CTCF PWM Δ (`ctcf_pwm_delta_v1.1`)
shifted for TE-overlapping (Alu/SVA) variants vs matched non-TE variants by
Cliff's δ ≥ **0.20**?

Explicitly **not** confirmatory ARCHCODE. Explicitly **not** HBB enrichment reopen.
Explicitly **not** holdout unblind. Explicitly **not** wet / C1 E/P.

## Novelty (Gate 0)

Track A HBB dual-estimand enrichment is **STOPPED / NOT_SUPPORTED**. C-E1 is an
honest reformulation: **non-HBB desk**, mappability-matched TE vs non-TE, same
exploratory PWM — independent window set, not HBB re-analysis.

## Frozen claim (pre-results)

> Cliff's δ (TE − non-TE) on |PWM Δ| ≥ **0.20** after umap-quartile matching.

**Falsify:** |δ| < **0.05** after matching → **REJECT**.  
Gray 0.05 ≤ |δ| < 0.20 → **INCONCLUSIVE**.

## Primary estimand

| Element | Definition |
|---------|------------|
| Universe | Rare SNVs AF≤0.001; exclude chr11:5.2–5.3 Mb (HBB) and sealed HO windows |
| Exposure | Overlap Alu/SVA rmsk vs matched non-TE |
| Match | chrom + umap quartile (+ length/GC if cheap) before PWM attach |
| Outcome | \|ctcf_pwm_delta_v1.1\| |
| SUPPORT | Cliff's δ ≥ 0.20 |
| Kill | \|δ\| < 0.05 |

## Desk scope note

Project forbids bulk gnomAD. Primary desk universe = **chr11 CTCF±250 bp**
neighborhoods (HUDEP-2 peaks), GraphQL window slices — not full-genome VCF.
Same exclusion and matching rules as frozen claim.

## Datasets — final

| Role | Source | Status |
|------|--------|--------|
| Scorer | `pilot_scaffold/ctcf_pwm_scorer.py` v1.1 | USED |
| Non-HBB rare SNV panel | gnomAD GraphQL r4 | FETCHED (55 849 SNVs) |
| Umap k100 | Hoffman bigWig | FETCHED (gitignored) |
| TE | UCSC rmsk Alu/SVA chr11 | USED |
| Holdout | HO_A/B/C | SEALED — excluded |
| HBB gnomAD | development | excluded from primary |

## Forbidden

- Scoring sealed holdout for enrichment
- Using HBB window as primary universe
- Wet / C1 / pathogenicity language
- Promoting PWM to confirmatory
- Post-hoc scorer swap after seeing δ
