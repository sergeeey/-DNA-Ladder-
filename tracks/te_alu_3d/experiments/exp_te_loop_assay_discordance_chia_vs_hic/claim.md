---
experiment: exp_te_loop_assay_discordance_chia_vs_hic
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: INCONCLUSIVE_REPLICATION
source_report: tracks/te_alu_3d/09_outputs/prospective/DEEP_RESEARCH_REPORT_C_A1_v1.md
candidate_id: C-A1
candidate_final_score: 7.06
decision_gate: VALIDATE_DESK
accession_freeze: ACCESSION_FREEZE_v1.md
replication_freeze: ACCESSION_FREEZE_replication_v1.md
replication_freeze_hct116: ACCESSION_FREEZE_replication_HCT116_v1.md
---

# Claim: TE-subfamily enrichment among Pol II ChIA-PET vs Hi-C discordant loop anchors in K562 (mappability-matched)

## Status

**INCONCLUSIVE_REPLICATION** — Standard tier. Three-cell synthesis
(`FAIL_INCONSISTENT` sign across cells; not claim REJECT).  
T2 CTCF gate **PASS** (Fisher OR ≈ 5.12).  
T3 primary AluSz Fisher OR ≈ **0.908** (Woolf 95% CI 0.851–0.967) < 1.1 at K562 desk.  
T4 umap≥0.3 (MAPQ=N/A proxy) OR ≈ **0.898** — strengthens FAIL.  
T5 GM12878 replication AluSz OR ≈ **1.252** (CI 1.172–1.339) → mid-zone.  
T5b HCT116 replication AluSz OR ≈ **1.280** (CI 1.162–1.410) → mid-zone;
CTCF gate PASS (OR ≈ 8.35); optional umap≥0.3 OR ≈ **1.281**.  
**null_results/ not filed** — falsification needs umap-gated OR < 1.1 **and** replication
OR < 1.15 or opposite; both GM12878 and HCT116 ≥ 1.15.  
**Accessions:** K562 `ACCESSION_FREEZE_v1.md`; GM12878
`ACCESSION_FREEZE_replication_v1.md`; HCT116
`ACCESSION_FREEZE_replication_HCT116_v1.md`. Holdout SEALED. Wet/oligo forbidden.

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
| Mappability | Hoffman Umap | `k100.Umap.MultiTrackMappability.bw` | GRCh38 | downloaded (gitignored); T4 done |
| Pol II ChIA-PET GM12878 (replication) | `ENCSR905HWW` | **`ENCFF913VWM`** | GRCh38 | **FROZEN + downloaded** |
| Hi-C GM12878 (replication) | `ENCSR410MDC` | **`ENCFF781ASD`** (HiCCUPS merged_loops_30) | GRCh38 | **FROZEN + downloaded** |
| CTCF GM12878 (replication gate) | `ENCSR000DZN` | **`ENCFF796WRU`** | GRCh38 | **FROZEN + downloaded** |
| Pol II ChIA-PET HCT116 (replication) | `ENCSR035PVZ` | **`ENCFF322FOT`** | GRCh38 | **FROZEN + downloaded** |
| Hi-C HCT116 (replication) | `ENCSR123UVP` | **`ENCFF060QTI`** (HiCCUPS merged_loops_30) | GRCh38 | **FROZEN + downloaded** |
| CTCF HCT116 (replication gate) | `ENCSR240PRQ` | **`ENCFF463FGL`** | GRCh38 | **FROZEN + downloaded** |

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
6. NOT a finalized claim-level REJECT (GM12878 **and** HCT116 replication OR mid-zone,
   not < 1.15).
7. NOT enrichment support for AluSz at MCID (K562 OR < 1.1; GM12878/HCT116 OR < 1.3).
8. NOT a license to switch primary TE because replication cells ≠ K562 sign.

## Next step

Honest stop: leave as `INCONCLUSIVE_REPLICATION` with documented cross-cell inconsistency
(K562 depletion vs GM12878/HCT116 mid-zone elevation). Do **not** change primary
subfamily post-hoc; do **not** promote exploratory AluJo / SVA_F; do **not** file
`null_results/` until both falsification arms are met; do **not** wet/holdout/C1.
