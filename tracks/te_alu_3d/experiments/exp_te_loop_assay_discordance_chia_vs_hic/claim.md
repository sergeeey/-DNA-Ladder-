---
experiment: exp_te_loop_assay_discordance_chia_vs_hic
date: 2026-07-20
ladder_tier: Standard
question_type: Descriptive
status: PREREGISTERED_DESK
source_report: tracks/te_alu_3d/09_outputs/prospective/DEEP_RESEARCH_REPORT_C_A1_v1.md
candidate_id: C-A1
decision_gate: VALIDATE_DESK
---

# Claim: TE-subfamily enrichment among Pol II ChIA-PET vs Hi-C discordant loop anchors in K562 (mappability-matched)

## Status

**PREREGISTERED_DESK** — Standard tier. No primary analysis results yet. Accessions marked
**VERIFY** until T0 probe JSON is reviewed. Holdout remains SEALED. Wet-lab / oligo order
forbidden. C1 E/P locks and GO signature packs are out of scope for this experiment.

## EstimandOps L0

**Question type:** Descriptive.

Genome-wide in K562, among processed chromatin-loop call sets from Pol II (POLR2A) ChIA-PET
and Hi-C, is membership in the **assay-discordant** loop-anchor set enriched for one or more
pre-registered TE subfamilies relative to a mappability-, length-, and GC-matched null?

Explicitly **not causal**: no perturbation, no DAG claiming TE → loop formation, no allele
edit. Explicitly **not** a C1 E–P contact test.

## Scientific question

Do discordant loop anchors (present in Pol II ChIA-PET calls but not Hi-C, or the reverse)
show TE-subfamily odds ratios that survive mappability matching and a MAPQ≥30 sensitivity
kill-test?

## Frozen claim (pre-results)

After T0 accession verify and before primary enrichment analysis:

> In K562, at least one pre-registered TE subfamily (from the frozen list finalized at T0:
> AluY, AluS, AluJ, SVA, L1 — drop any class with n below a pre-registered minimum) has
> **OR ≥ 1.3** for discordant vs matched-null loop anchors.

**Falsification (pre-registered):** if, after MAPQ≥30 (or equivalent high-mappability gate)
and replication on an independent processed file/experiment, the OR for every tested
subfamily is **< 1.1**, the claim is **REJECT**.

## Primary estimand

- **Universe:** Loop anchors from released, processed Pol II ChIA-PET and Hi-C loop call sets
  in K562 (assembly frozen at T0; prefer GRCh38 if both assays provide it).
- **Exposure:** TE subfamily label overlapping the anchor window (public RepeatMasker or
  equivalent; source pinned in `data_manifest.md` after download).
- **Outcome:** Discordance class — ChIA-PET-only / Hi-C-only / shared (both).
- **Comparator:** Matched-null anchors (same covariates; see `controls.md`).
- **Summary measure:** Odds ratio (OR) of subfamily *s* in discordant anchors vs matched null.
- **MCID:** OR ≥ 1.3 for ≥1 pre-registered subfamily.
- **Falsification threshold:** OR < 1.1 after MAPQ≥30 + replication.

## Datasets (VERIFY at T0 — do not invent biology)

| Role | Candidate / note | Status |
|------|------------------|--------|
| Pol II ChIA-PET K562 loops | **T0 verified:** `ENCSR880DSH` bedpe `ENCFF759YBZ` / `ENCFF511QFN` / `ENCFF030PMM` (GRCh38). **Do not** use `ENCSR000BZZ` (ESR1) | T0_OK — download pending |
| Hi-C K562 loops | **T0 verified:** e.g. `ENCFF693XIL` (`ENCSR545YBD`); `ENCFF598CLH`/`ENCFF256ZMD` (`ENCSR479XDG`) | T0_OK — download pending |
| Invalid placeholder | `ENCSR444WCX` | **Missing (404)** — discarded |
| TE annotation | Public RMSK (assembly-matched GRCh38) | VERIFY / pin at download |
| Mappability | Umap or ENCODE mappability track, assembly-matched | VERIFY / pin at download |

T0 script: `scripts/t0_probe_encode_accessions.py` → `data/t0_accession_probe.json`.

Large binaries are **not** downloaded by T0 (metadata only). Real downloads require
`data_manifest.md` md5 entries.

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

## What this does NOT mean

1. NOT causal TE → loop mechanism.
2. NOT wet-lab validation of C1 or any allele.
3. NOT authorization to unseal holdout or order oligos.
4. NOT a license to edit C1 E/P locks or GO packs.
5. NOT a re-opening of SE vs typical-enhancer closed tests.

## Next step

Run / review T0 accession probe. If Pol II ChIA-PET K562 lacks processed bedpe/loops
(FASTQ-only) → `BLOCKED_DATA` and demote per report §16 (consider C-B1 or C-K1).
