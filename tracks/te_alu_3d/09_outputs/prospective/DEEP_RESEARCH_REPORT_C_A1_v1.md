# Deep Research Report v1.0 — TE / 3D desk candidate slate → C-A1

**Date:** 2026-07-20  
**Track:** `tracks/te_alu_3d`  
**Decision:** `VALIDATE_DESK` for **C-A1**  
**Tier if promoted:** Standard (claim + controls/notes + decision)  
**Hard constraints:** no wet-lab · no oligo order · holdout remains SEALED · no C1 E/P lock edits · no GO signature shopping · no closed SE/LLPS re-runs · HBB TE enrichment remains STOPPED

---

## 1. Executive summary

Twelve desk-compatible candidates (C-A1 … C-L1) were scored for a next DNA Ladder desk experiment that does **not** reopen C1 wet-lab, does **not** unseal holdout, and does **not** overlap closed SE/LLPS or HBB-enrichment claims.

**C-B1** scores highest on raw impact/novelty. **C-A1** is recommended instead: clearer descriptive estimand, cheaper falsification (≈2 h MAPQ≥30 kill-test), and reusable assets (P3 matched-null pattern, ENCODE loop files).

**Recorded decision:** `VALIDATE_DESK` → open Standard-tier preregistration  
`tracks/te_alu_3d/experiments/exp_te_loop_assay_discordance_chia_vs_hic/`.

---

## 2. Scope and non-goals

**In scope**

- Desk-only, public ENCODE (and related public) processed loop calls
- Descriptive L0 question about TE-subfamily enrichment in assay-discordant loops
- Pre-registered MCID / falsification thresholds before any primary analysis

**Out of scope / forbidden**

- Wet-lab, oligo order, transfection, Capture-C bait order
- Unsealing or scoring holdout
- Editing C1 locked E/P coordinates or GO signature packs
- Causal language (“TE causes loop”, “assay discordance proves biology”)
- Re-running closed SE vs typical-enhancer directions
- Claiming HBB Alu/SVA enrichment revival

---

## 3. Scientific problem

Loop catalogs from Pol II ChIA-PET and Hi-C in the same cell line (K562) disagree. Some loops are assay-exclusive. Transposable-element (TE) anchors are a plausible, track-aligned exposure for asking whether **assay discordance itself** is TE-subfamily stratified after mappability matching — without claiming that TEs “create” loops.

This is a **methods-biology / descriptive genomics** question, not a C1 allele story.

---

## 4. Novelty landscape

| Prior art | What it covers | Gap for DNA Ladder |
|-----------|----------------|--------------------|
| Akgol Oksuz et al. 2021 *Nat Methods* (DOI 10.1038/s41592-021-01248-7) | Protocol parameters (cross-link, fragmentation) drive loop vs compartment recovery across Hi-C / Micro-C / Hi-C 3.0 | Does **not** stratify discordant loops by TE subfamily with mappability-matched nulls |
| ENCODE / 4DN loop catalogs | Released bedpe/loop calls for K562 | Treats loops as assay products; TE stratification not the primary claim |
| Closed SE/LLPS track results | SE vs typical enhancer occupancy / G4 / R-loop / constraint | Different exposure; do not reopen |
| HBB TE enrichment (STOPPED) | Rare SNV / motif disruption on HBB development set | Different locus program; do not reopen |
| C1 prospective panel | Allele-level activity / architecture desk | Locked E/P; not this estimand |

**Honest novelty framing for C-A1:** independent TE-subfamily + mappability-matched test of ChIA-PET vs Hi-C **discordance**, not a rediscovery of Akgol Oksuz protocol effects.

---

## 5. Candidate generation method

Candidates were generated under four filters:

1. **Desk-feasible** with public processed files (no raw-only FASTQ campaigns)
2. **Non-overlapping** with SE/LLPS closed set and HBB STOPPED claims
3. **No C1 E/P shopping** and no holdout touch
4. **Killable** — each needs a cheap sensitivity falsifier before expensive work

IDs C-A1 … C-L1 are desk slate IDs (not C1 panel alleles).

---

## 6. Scoring rubric

Final score ∈ [0, 10] = weighted mean of:

| Axis | Weight | Meaning |
|------|--------|---------|
| Identifiability | 0.25 | Estimand clarity; allowed claim language |
| Kill-speed | 0.20 | Hours to honest REJECT |
| Data readiness | 0.20 | Processed public files likely |
| Novelty (honest) | 0.15 | Not frontier-duplicate without reformulation |
| Asset reuse | 0.10 | P3 matched-null, ENCODE patterns, null_results filing |
| Track fit | 0.10 | TE / 3D desk continuity without wet GO |

**Selection rule:** maximize kill-speed × identifiability subject to final_score ≥ 7.0; do **not** auto-pick max raw score.

---

## 7. Candidate registry (C-A1 … C-L1)

| ID | Title | Final score | Recommended |
|----|-------|-------------|-------------|
| C-A1 | TE-subfamily stratification of Pol II ChIA-PET vs Hi-C loop discordance (K562), mappability-matched | 7.6 | **yes** |
| C-B1 | AluY enrichment at convergent CTCF+RAD21 anchors with AG allele-prior overlay (non-holdout) | 8.1 | no |
| C-C1 | SVA vs Alu differential occupancy of Hi-C loop anchors (K562), length-matched | 7.2 | no |
| C-D1 | TE divergence/age bin vs cross-assay loop-call reproducibility | 6.9 | no |
| C-E1 | Mappability-matched TE vs non-TE rare-SNV PWM Δ (genome-wide desk; non-HBB) | 6.4 | no |
| C-F1 | Pol II ChIA-PET–exclusive loop TE density vs Hi-C-shared loops (unstratified TE class) | 7.0 | no |
| C-G1 | RAD21 ChIA-PET vs CTCF ChIA-PET TE-anchor odds (K562) | 6.8 | no |
| C-H1 | Micro-C vs Hi-C TE recovery differential (needs Micro-C processed loops) | 7.4 | no |
| C-I1 | AluJo negative-control calibration of loop-call false-positive rate | 6.2 | no |
| C-J1 | TE insertion orientation vs loop-anchor asymmetry | 6.5 | no |
| C-K1 | CTCF ChIA-PET K562 TE-subfamily discordance vs Hi-C (fallback if Pol II bedpe blocked) | 7.3 | no |
| C-L1 | Cross-cell-line transfer: K562 discordant-TE pattern vs GM12878 | 6.7 | no |

Compact machine registry: `candidate_registry_deep_research_v1.yaml`.

---

## 8. Deep dive — C-A1 (recommended)

**Scientific question.** Among K562 chromatin loops, is membership in the Pol II ChIA-PET–vs–Hi-C discordant set enriched for specific TE subfamilies relative to a mappability-, length-, and GC-matched null?

**L0:** Descriptive.

**Primary estimand.** Odds ratio (OR) of TE-subfamily *s* among discordant loop anchors vs matched-null anchors.

**Exposure.** TE subfamily label at loop anchor (RepeatMasker / equivalent public TE annotation), after MAPQ / mappability gates.

**Outcome.** Discordant vs shared loop class (ChIA-PET-only / Hi-C-only / both).

**MCID.** OR ≥ 1.3 for at least one pre-registered subfamily family (AluY / AluS / AluJ / SVA / L1 — finalize list at T0).

**Falsification.** OR < 1.1 after MAPQ≥30 filter + independent replicate file (or independent ENCODE experiment) → REJECT.

**Why cheap to kill.** If MAPQ≥30 collapses the OR below 1.1, stop within a short desk session — no wet path, no holdout.

---

## 9. Deep dive — C-B1 (higher score, not recommended now)

C-B1 combines architecture-anchor biology with an AlphaGenome allele prior. Raw score is higher (impact + narrative continuity with prospective panel), but:

1. Estimand mixes descriptive TE enrichment with allele-prior overlay → weaker L0 purity
2. Kill-test requires AG credential path + motif/anchor intersection → slower than MAPQ gate
3. Higher risk of accidental C1-adjacent shopping despite “non-holdout” wording

**Decision:** park C-B1; do not preregister until C-A1 resolves or is BLOCKED_DATA.

---

## 10. Kill-test design (C-A1)

| Stage | Action | Stop if |
|-------|--------|---------|
| T0 | Verify ENCODE accessions; require **processed** bedpe/loops (not FASTQ-only) | Only raw → `BLOCKED_DATA`; consider C-B1 or C-K1 |
| T1 | MAPQ≥30 / high-mappability sensitivity | OR < 1.1 → REJECT |
| T2 | Replication file / second experiment | Effect unstable → INCONCLUSIVE or REJECT per prereg |
| T3 | Matched-null covariates (mappability, GC, length, chr) | Effect explained by covariates → REJECT |

Positive gate: CTCF-associated loop anchors should show expected recovery (sanity, not primary claim).  
Negative gate: AluJo (old/inactive Alu) should not drive a primary “young TE” story without pre-registration.

---

## 11. Data plan and accession hygiene

**Do not invent biology.** Candidate accessions in early notes (`ENCSR000BZZ`, `ENCSR444WCX`) must be verified:

- `ENCSR000BZZ` exists but is **ESR1** ChIA-PET, not Pol II — wrong target for C-A1
- `ENCSR444WCX` — expect invalid / 404; replace via T0 search

**T0 must search** for:

- Pol II / POLR2A ChIA-PET K562 **processed** loops/bedpe
- Hi-C (in situ / intact) K562 **processed** loops/bedpe

Script: `experiments/exp_te_loop_assay_discordance_chia_vs_hic/scripts/t0_probe_encode_accessions.py`  
Output: `.../data/t0_accession_probe.json` (metadata only; no large downloads).

---

## 12. Preregistration draft (Standard tier)

Expand into experiment folder (this report’s promotion target):

- **Status:** `PREREGISTERED_DESK`
- **L0:** Descriptive
- **Frozen claim:** Discordant Pol II ChIA-PET vs Hi-C loop anchors in K562 are enriched for ≥1 pre-registered TE subfamily after mappability matching (OR≥1.3); falsified if OR<1.1 under MAPQ≥30 + replication
- **Universe:** Released K562 loop anchors from verified ChIA-PET + Hi-C processed call sets
- **Datasets:** accessions **VERIFY** at T0 (mark TBD until probe JSON committed)
- **Controls:** positive CTCF gate; negative AluJo; matched-null covariates
- **Language:** descriptive enrichment only — NOT causal; NOT wet; NOT holdout; NOT C1 E/P
- **Novelty:** TE-subfamily stratification + mappability matching vs Akgol Oksuz 2021 protocol-parameter focus; no SE/HBB overlap

Full arts: `claim.md`, `controls.md`, `notes.md`, `decision.md` (PENDING_T0).

---

## 13. Risk register (summary)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Pol II ChIA-PET only raw FASTQ | High | Stop → `BLOCKED_DATA`; demote to C-K1/C-B1 |
| Wrong accession (ESR1 / 404) | High | T0 verify; never hard-code unverified IDs into analysis |
| Mappability confounding TE signal | High | Matched-null + MAPQ≥30 kill |
| Accidental C1 / holdout bleed | High | Explicit forbids in claim; no allele lists from sealed sets |
| Causal overclaim | Medium | Allowed/forbidden language table |
| Genome build mix (hg19/GRCh38) | Medium | Freeze assembly at T0 before intersect |
| Large file download creep | Medium | Metadata-only probe; manifest md5 after real fetch |

---

## 14. Reusable assets

- P3 matched-null panel pattern (`P3_matched_null_*`) — covariate matching discipline
- ENCODE REST fetch patterns from `se_llps` scripts (metadata → small JSON)
- `null_results/` filing format for REJECT/INCONCLUSIVE
- Track docs: Tasktracker / Changelog append-only updates

---

## 15. What this report does NOT mean

1. Does **not** validate C1 biology or unlock wet-lab GO  
2. Does **not** claim TEs cause chromatin loops  
3. Does **not** reopen SE/LLPS closed experiments  
4. Does **not** revive HBB TE enrichment  
5. Does **not** authorize oligo order or holdout unseal  
6. Does **not** treat unverified ENCFF/ENCSR IDs as analysis inputs  

---

## 16. Decision record and stop conditions

**Promote:** C-A1 → Standard-tier desk preregistration (`VALIDATE_DESK`).

**Do not promote now:** C-B1 (higher score, worse kill/identifiability tradeoff).

**Park:** C-C1 … C-L1 as registry alternatives; C-K1 is the preferred data-availability fallback if Pol II processed loops are missing.

**Stop condition:** Если bedpe processed loop calls для Pol II ChIA-PET K562 недоступны в processed form (только raw FASTQ) → status `BLOCKED_DATA`; demote C-A1 and consider C-B1 or C-K1.

**Decision recorded:** `VALIDATE_DESK` for C-A1 (recommended over higher-scoring C-B1 due to cheaper kill-test / clearer estimand).
