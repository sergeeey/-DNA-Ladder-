---
experiment: exp_te_loop_assay_discordance_chia_vs_hic
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: FAIL_DESK_PRIMARY
source_report: tracks/te_alu_3d/09_outputs/prospective/DEEP_RESEARCH_REPORT_C_A1_v1.md
candidate_id: C-A1
candidate_final_score: 7.06
decision_gate: VALIDATE_DESK
accession_freeze: ACCESSION_FREEZE_v1.md
---

# Claim: TE-subfamily enrichment among Pol II ChIA-PET vs Hi-C discordant loop anchors in K562 (mappability-matched)

## Status

**FAIL_DESK_PRIMARY** — Standard tier. T2 CTCF gate **PASS** (Fisher OR ≈ 5.12).  
T3 primary AluSz Fisher OR ≈ **0.908** (Woolf 95% CI 0.851–0.967) < 1.1 at single-cell-type
(K562) desk stage. Matched-null run (n_perm=200). MAPQ/`umap` = `PENDING_MAPPABILITY`.  
Full claim **REJECT** still requires MAPQ≥30 + replication — `null_results/` not filed yet.  
**Accessions:** FROZEN in `ACCESSION_FREEZE_v1.md` (downloads + on-disk md5 in `data_manifest.md`).  
Holdout remains SEALED. Wet-lab / oligo order forbidden. C1 E/P locks and GO signature packs
are out of scope for this experiment.

## EstimandOps L0

**Question type:** Descriptive.

Genome-wide in K562, among processed chromatin-loop call sets from Pol II (RNAPII / POLR2A)
ChIA-PET and Hi-C, is membership in the **assay-discordant** loop-anchor set enriched for one
or more pre-registered TE subfamilies relative to a mappability-, length-, and GC-matched null?

Explicitly **not causal**: no perturbation, no DAG claiming TE → loop formation, no allele
edit. Explicitly **not** a C1 E–P contact test.

## Scientific question

Do discordant loop anchors (present in Pol II ChIA-PET calls but not Hi-C, or the reverse)
show TE-subfamily odds ratios that survive mappability matching and a MAPQ≥30 sensitivity
kill-test?

## Frozen claim (pre-results)

Before primary enrichment analysis:

> In K562, at least one pre-registered TE subfamily (from the frozen list finalized before
> OR computation: AluY, AluS, AluJ, SVA, L1 — drop any class with n below a pre-registered
> minimum) has **OR ≥ 1.3** for discordant vs matched-null loop anchors.

**Falsification (pre-registered):** if, after MAPQ≥30 (or equivalent high-mappability gate)
and replication on an independent processed file/biorep, the OR for every tested subfamily is
**< 1.1**, the claim is **REJECT**.

## Primary estimand

- **Universe:** Loop anchors from frozen primary bedpe files (GRCh38).
- **Exposure:** TE subfamily label overlapping the anchor window (public RepeatMasker or
  equivalent; source pinned in `data_manifest.md` after download).
- **Outcome:** Discordance class — ChIA-PET-only / Hi-C-only / shared (both).
- **Comparator:** Matched-null anchors (same covariates; see `controls.md`).
- **Summary measure:** Odds ratio (OR) of subfamily *s* in discordant anchors vs matched null.
- **MCID:** OR ≥ 1.3 for ≥1 pre-registered subfamily.
- **Falsification threshold:** OR < 1.1 after MAPQ≥30 + replication.

## Datasets — FROZEN primary accessions (T0/T1)

See `ACCESSION_FREEZE_v1.md` for full rationale. On-disk md5 recorded in `data_manifest.md`.

| Role | Experiment | Primary file | Assembly | Status |
|------|------------|--------------|----------|--------|
| Pol II ChIA-PET K562 loops | `ENCSR880DSH` | **`ENCFF511QFN`** (bedpe loops; preferred_default; biorep 1) | GRCh38 | **FROZEN + downloaded** |
| Pol II sensitivity bioreps | `ENCSR880DSH` | `ENCFF759YBZ` (rep2), `ENCFF030PMM` (rep3) | GRCh38 | FROZEN (non-primary) |
| Hi-C K562 loops | `ENCSR545YBD` | **`ENCFF693XIL`** (bedpe loops; HiCCUPS merged_loops_30; preferred_default) | GRCh38 | **FROZEN + downloaded** |
| Hi-C alternate | `ENCSR479XDG` | `ENCFF598CLH` (intact localizer; sensitivity only) | GRCh38 | Alternate |
| CTCF peaks (positive gate) | `ENCSR000AKO` | **`ENCFF769AUF`** (conservative IDR; preferred_default) | GRCh38 | **FROZEN + downloaded** |
| Rejected | `ENCSR000BZZ` | — | — | **WRONG** (ESR1 ChIA-PET, not Pol II) |
| Rejected | `ENCSR444WCX` | — | — | **404** |
| TE annotation | UCSC | `rmsk.txt.gz` (hg38) | GRCh38 | downloaded (gitignored) |
| Mappability | — | Umap / ENCODE track | GRCh38 | pending matched-null |

**Hi-C primary rationale:** Prefer ENCODE processed in situ Hi-C loop calls (`ENCFF693XIL`,
HiCCUPS) over intact localizer (`ENCFF598CLH`); matches track’s existing K562 loop proxy and
portal preferred_default.

## Controls

See `controls.md`:

- Positive gate: CTCF-associated loop anchors (sanity recovery, not primary claim)
- Negative: AluJo must not silently become the headline young-TE story without preregistration
- Matched-null covariates: mappability, GC, length, chromosome

## Allowed claim language

- “Discordant loop anchors are enriched / not enriched for TE subfamily *s* (OR=…).”
- “Effect collapses under MAPQ≥30 → consistent with mappability artifact.”
- “Descriptive association in processed public call sets.”

## Forbidden claim language

- Causal: “TE creates / disrupts loops,” “assay discordance proves biological looping.”
- Wet / clinical: any GO, oligo, transfection, disease claim
- C1 shopping: any rewrite of locked E/P or Stage-3 slots from this result
- Holdout: any use of sealed holdout variants
- SE/HBB revival: any claim that reopens closed SE/LLPS directions or STOPPED HBB TE enrichment

## Novelty note

- Does **not** overlap closed SE/LLPS directions or HBB TE enrichment STOPPED claims.
- Difference from Akgol Oksuz et al. 2021 (*Nat Methods*, DOI 10.1038/s41592-021-01248-7):
  that work evaluates **protocol parameters** (cross-link / fragmentation) for loop vs
  compartment recovery across Hi-C / Micro-C / Hi-C 3.0. This experiment asks a **different**
  question: TE-subfamily stratification of **cross-assay discordance** with **mappability
  matching**. A positive result would not rediscover their protocol ranking; a negative
  result would not falsify it.
- Deep Research selected C-A1 (final **7.06**) over higher-scoring C-B1 (**7.47**) for
  identifiability and cheap MAPQ kill-test — see report §1 / §5.

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT wet-lab validation of C1 or any allele.
3. NOT authorization to unseal holdout or order oligos.
4. NOT a license to edit C1 E/P locks or GO packs.
5. NOT a re-opening of SE vs typical-enhancer closed tests.
6. NOT a multi-cell-type / MAPQ-gated REJECT (desk FAIL_DESK_PRIMARY only).
7. NOT enrichment support for AluSz (OR < 1.1 at desk primary).

## Next step

MAPQ/umap sensitivity + independent replication cell type / biorep before claim-level
REJECT or upgrade. Do **not** change primary subfamily post-hoc; do **not** promote
exploratory AluJo / SVA_F.
