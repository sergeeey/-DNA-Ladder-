---
experiment: exp_llps_ctd_phospho_vs_coactivators
date: 2026-07-08
ladder_tier: Standard
question_type: Descriptive
status: INCONCLUSIVE -- Ser5P ratio window-sensitive (0.841 at 2kb / 0.456 at 5kb), no stable contrast with BRD4/MED1's robust SE-favoring pattern; see decision.md
---

# Claim: Pol II-Ser5P shows a different promoter/super-enhancer density-ratio profile than BRD4/MED1, quantified with the same method as exp_llps_promoter_vs_se_chip_evidence

## Background

Second DNA Ladder experiment. Direct extension of
`experiments/exp_llps_promoter_vs_se_chip_evidence` (BRD4 ratio=0.414, MED1 ratio=0.523,
both SE-favoring) -- reuses the exact same GRCh38 promoter/SE region classification and
density-ratio method, adding one more factor: Pol II phosphorylated at CTD Serine 5
(Pol II-Ser5P), the classic mark of transcription initiation.

## EstimandOps L0

**Question type:** Descriptive.
"Using the same peak-density-ratio method as exp_llps_promoter_vs_se_chip_evidence, does
Pol II-Ser5P (K562, GRCh38) show a promoter-favoring density ratio, in contrast to the
SE-favoring ratios already found for BRD4 and MED1 in the same cell line, same builds, same
super-enhancer call set?"

## Novelty check (mandatory, per falsification-ladder.md Step -3)

Ran via WebSearch before any data work, 2026-07-08:

**The base biological fact is NOT novel -- it is decades-old, foundational molecular biology,**
not something this project can discover: Pol II CTD Serine-5 phosphorylation is well
established to mark transcription initiation and to be enriched at promoters (classic ChIP-seq
literature, e.g. fission-yeast/mammalian CTD phospho-isoform profiling reviewed and confirmed
across multiple independent sources found via WebSearch 2026-07-08 -- this predates the LLPS
condensate literature entirely and is textbook-level knowledge). Running "is Ser5P promoter-
enriched?" as a standalone claim would be the same mistake as ARCHCODE's original Hypothesis B
(BCL11A/Casgevy) -- rediscovering settled biology.

**Reformulated, honest scope:** this experiment does NOT test or claim to discover that
Ser5P is promoter-proximal (already established). It asks a narrower, genuinely
non-redundant question: quantified with THIS project's own density-ratio method (not found
stated this way in the literature searched), how does Ser5P's promoter/SE preference compare
*directly, numerically, in the same dataset* to BRD4/MED1's already-measured SE-favoring
preference? This is a within-project comparative extension (same K562 cell line, same GRCh38
build, same dbSUPER SE call set, same promoter-window definitions, same code) -- it adds one
more calibrated data point to `exp_llps_promoter_vs_se_chip_evidence`'s finding rather than
making an independent discovery claim. If Ser5P comes out promoter-favoring while BRD4/MED1
are SE-favoring, that would be a quantified, reproducible illustration (via ChIP-seq, not
imaging) of the CTD-phosphorylation-switch concept from Guo 2019 / Linhartova 2024
(`Research Library/sources/llps-transcription/`) -- consistent with, not a replication of,
those papers' own (different-methodology) findings.

## L1 Estimand

- **Population:** Pol II-Ser5P ChIP-seq peaks, K562, GRCh38 (`ENCSR000BKR`, file
  `ENCFF053XYZ`, "optimal IDR thresholded peaks", released -- confirmed available via ENCODE
  REST API, 2026-07-08, same selection convention as BRD4/MED1/POLR2A in the first experiment).
- **Exposure/Comparator:** Same promoter-only / SE-only region classification as
  `exp_llps_promoter_vs_se_chip_evidence` (2kb promoter window primary, 5kb sensitivity check;
  reuses `data/input/gencode_tss_grch38.json` and `data/input/k562_super_enhancers_grch38.json`
  as-is, no re-fetch needed).
- **Endpoint:** Peak density (peaks/kb) in promoter-only vs SE-only region space.
- **Summary measure:** Promoter/SE density ratio, identical formula to the first experiment,
  computed by the same `scripts/llps_promoter_vs_se_analysis.py` (Ser5P added as a 4th factor
  alongside BRD4/MED1/POLR2A-total).
- **MCID:** Same as the first experiment (>=1.5 promoter-favoring / <=0.67 SE-favoring /
  between = no clear preference), pre-registered here before running, for direct comparability
  across the two experiments.
- **ICE:** None anticipated.

## What This Does NOT Mean

1. Does NOT claim to discover that Ser5P marks initiation or is promoter-proximal --
   established, cited literature, not this project's finding.
2. Does NOT distinguish LLPS/phase-separation from conventional CTD-phospho-dependent
   recruitment as the mechanism for any observed pattern -- same limitation as the first
   experiment.
3. A promoter-favoring Ser5P result alongside SE-favoring BRD4/MED1 would NOT by itself prove
   the CTD acts as a literal "phase-state switch" (Guo 2019's specific claim, live-cell/in
   vitro) -- it would be consistent with that model via an orthogonal (ChIP-seq) method, not
   independent proof of it.
4. Single cell line (K562), single antibody/experiment per factor -- same generalization
   limits as the first experiment.

## Status

Design-stage. Data availability confirmed (`[VERIFIED-bash]`, ENCODE REST API,
`ENCSR000BKR`/`ENCFF053XYZ`, GRCh38, released). Not yet fetched or analyzed.
