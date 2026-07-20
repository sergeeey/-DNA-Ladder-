# Deep Research Report v1.0 — Next desk experiment slate (TE / 3D track)

**Report version:** 1.0  
**Date:** 2026-07-20  
**Track:** `tracks/te_alu_3d`  
**Inspection commit (report authored against):** `c048650`  
**Note:** Current `master` may be newer after C-A1 scaffold / freeze PRs; do not treat `c048650` as HEAD after merge.  
**Decision:** `VALIDATE_DESK` for **C-A1**  
**Hard constraints:** no wet-lab · no oligo order · holdout SEALED · no C1 E/P lock edits · no GO signature shopping · no closed SE/LLPS re-runs · HBB TE enrichment STOPPED

---

## 1. Executive verdict

Twelve desk-compatible candidates (**C-A1 … C-L1**) were scored for the next DNA Ladder desk experiment that does **not** reopen C1 wet-lab, does **not** unseal holdout, and does **not** overlap closed SE/LLPS or HBB-enrichment claims.

| Rank by raw final_score | ID | Final | Role |
|-------------------------|----|-------|------|
| 1 | **C-B1** | **7.47** | Highest score — **not** selected |
| 2 | C-H1 | 7.12 | Park (Micro-C data dependency) |
| 3 | **C-A1** | **7.06** | **RECOMMENDED → `VALIDATE_DESK`** |

**Why recommend C-A1 despite C-B1 = 7.47 > C-A1 = 7.06:**  
Selection rule is **not** max raw score. Maximize **identifiability × kill-speed** subject to `final_score ≥ 7.0`. C-A1 has a cleaner Descriptive L0 estimand and a ≈2 h MAPQ≥30 falsifier; C-B1 mixes TE-anchor enrichment with an AlphaGenome allele-prior overlay (slower kill, higher C1-adjacent bleed risk).

**Recorded decision:** `VALIDATE_DESK` → Standard-tier preregistration  
`tracks/te_alu_3d/experiments/exp_te_loop_assay_discordance_chia_vs_hic/`.

**Stop condition:** Если bedpe processed loop calls для Pol II ChIA-PET K562 недоступны в processed form (только raw FASTQ) → status `BLOCKED_DATA`; demote C-A1 and consider C-B1 or C-K1.

**Decision recorded:** `VALIDATE_DESK` for C-A1 (recommended over higher-scoring C-B1 due to cheaper kill-test / clearer estimand).

---

## 2. Scope, constraints, and repository state

### In scope
- Desk-only public ENCODE (and related public) **processed** loop calls
- Descriptive L0 question on TE-subfamily enrichment in assay-discordant loops
- Pre-registered MCID / falsification before any primary OR analysis

### Forbidden
- Wet-lab, oligo order, transfection, Capture-C bait order
- Unsealing or scoring holdout
- Editing C1 locked E/P or GO signature packs
- Causal language (“TE causes loops”, “discordance proves biology”)
- Re-running closed SE vs typical-enhancer directions
- Reviving HBB Alu/SVA enrichment

### Repository state at inspection
- **Commit inspected for this report:** `c048650` (merge of historical-brief v1.1 work)
- **Post-report scaffold** may land on newer `master` (C-A1 experiment folder, T0 probe JSON, accession freeze). Re-pin HEAD in Changelog when merging; do not rewrite history of this report’s inspection pin.

---

## 3. Closed directions (do not reopen)

| Direction / experiment | Verdict | Why closed |
|------------------------|---------|------------|
| BRD4/MED1 SE vs promoter ChIP (matched H3K27ac) | REJECT | Matched control falsifies SE-favoring claim |
| ClinVar VUS rarer inside SE (frequency) | REJECT | Effect ≈0 |
| SE vs typical Gnocchi constraint | REJECT | Sign flips; below MCID |
| ClinVar VUS SE vs matched typical | REJECT | Effect ≈0; convergent null |
| Missing heritability via SE membership (meta) | CLOSED | Pipeline OK; estimands converge on null |
| R-loop (DRIP) SE vs typical K562 | REJECT | Wrong direction; n-driven p |
| G4 (BG4) SE vs typical K562+HepG2 | REJECT | Wrong direction both lines |
| Continuous SE-size vs Gnocchi/R-loop/G4 | REJECT-with-signal | Real but below MCID |
| HBB TE / motif enrichment confirmatory | STOPPED | Development-set only; not confirmatory |
| C1 wet-lab GO / oligo order | NO-GO / UNSIGNED | Desk retain ≠ wet proof; holdout SEALED |
| C1 E/P lock shopping from new desk scores | FORBIDDEN | Freeze pack locked |

---

## 4. Novelty maps (three directions)

### Direction A — 3C assay parameters vs loop recovery
**Frontier prior:** Akgol Oksuz et al. 2021 *Nat Methods* (DOI 10.1038/s41592-021-01248-7) — cross-link / fragmentation drive loop vs compartment recovery (Hi-C / Micro-C / Hi-C 3.0).  
**Gap:** Does **not** stratify **cross-assay discordance** by **TE subfamily** with mappability-matched nulls.  
**DNA Ladder angle:** C-A1 / C-F1 / C-H1 / C-K1 sit in this gap without claiming protocol superiority.

### Direction B — TE anchors in 3D / architecture catalogs
**Frontier prior:** ENCODE/4DN loop catalogs; CTCF/cohesin ChIA-PET topology literature; Alu/SVA at regulatory contacts anecdotally discussed.  
**Gap:** Honest, pre-registered **subfamily OR** on **discordant** vs shared anchors with explicit MAPQ kill — not allele-level C1 stories.  
**DNA Ladder angle:** C-A1 primary; C-C1 / C-D1 / C-G1 / C-J1 adjacent.

### Direction C — Rare TE-SNV / activity priors (prospective panel continuity)
**Frontier prior:** Track’s own C1/Stage-1–3 panel, AlphaGenome priors, PWM exploratory — wet path UNSIGNED.  
**Gap / risk:** Easy to accidentally reopen C1 E/P or holdout.  
**DNA Ladder angle:** C-B1 / C-E1 / C-L1 touch this map; **park** behind C-A1 unless BLOCKED_DATA.

---

## 5. Scoring formula

Axes scored 0–10 (higher = better for desk promotion):

| Axis | Code | Meaning |
|------|------|---------|
| Novelty (honest) | N | Not frontier-duplicate without reformulation |
| Feasibility (desk) | F | Runnable with public processed files this month |
| Identifiability | I | Single clear estimand; allowed claim language |
| Kill-speed | K | Hours to honest REJECT |
| Data readiness | D | Processed bedpe/loops likely (not FASTQ-only) |
| Track fit | T | TE/3D continuity without wet GO / SE reopen |

\[
\mathrm{final\_score} = 0.15N + 0.15F + 0.25I + 0.20K + 0.15D + 0.10T
\]

Rounded to 2 decimals.

**Promotion rule:** among candidates with `final_score ≥ 7.0`, choose max of \((I \times K)\); break ties by D; never auto-pick max raw score alone.

---

## 6. Full candidate table (C-A1 … C-L1)

| ID | Title (short) | N | F | I | K | D | T | Final | Rec? |
|----|---------------|---|---|---|---|---|---|-------|------|
| C-B1 | AluY @ convergent CTCF+RAD21 + AG allele-prior (non-holdout) | 9.0 | 7.27 | 6.8 | 6.3 | 7.8 | 9.0 | **7.47** | no |
| C-H1 | Micro-C vs Hi-C TE recovery differential | 8.2 | 6.4 | 7.55 | 7.2 | 5.7 | 7.5 | **7.12** | no |
| C-A1 | TE-subfamily × ChIA-PET vs Hi-C discordance (mappability-matched) | 5.2 | 6.8 | 7.8 | 8.2 | 6.47 | 7.0 | **7.06** | **yes** |
| C-K1 | CTCF ChIA-PET TE-subfamily discordance vs Hi-C (Pol II fallback) | 5.5 | 6.8 | 7.4 | 7.8 | 6.5 | 7.0 | 6.93 | no |
| C-C1 | SVA vs Alu differential Hi-C loop-anchor occupancy | 6.0 | 7.2 | 7.0 | 7.0 | 7.0 | 7.5 | 6.93 | no |
| C-F1 | ChIA-exclusive vs shared loop TE density (unstratified class) | 4.8 | 7.5 | 7.0 | 7.2 | 6.8 | 7.0 | 6.75 | no |
| C-D1 | TE divergence/age bin vs cross-assay loop reproducibility | 6.5 | 6.5 | 6.8 | 6.5 | 6.0 | 7.0 | 6.55 | no |
| C-G1 | RAD21 vs CTCF ChIA-PET TE-anchor odds | 6.2 | 6.0 | 6.8 | 6.5 | 5.5 | 7.0 | 6.35 | no |
| C-E1 | Mappability-matched TE vs non-TE rare-SNV PWM Δ (non-HBB) | 4.0 | 7.5 | 6.0 | 7.0 | 7.5 | 6.0 | 6.35 | no |
| C-I1 | AluJo negative-control calibration of loop FP rate | 3.5 | 7.0 | 6.5 | 7.5 | 7.0 | 5.5 | 6.30 | no |
| C-J1 | TE insertion orientation vs loop-anchor asymmetry | 6.0 | 6.0 | 6.2 | 6.5 | 6.0 | 6.5 | 6.20 | no |
| C-L1 | K562 discordant-TE pattern transfer to GM12878 | 6.8 | 5.5 | 6.5 | 5.5 | 5.5 | 6.5 | 6.04 | no |

Compact registry: `candidate_registry_deep_research_v1.yaml`.

---

## 7. Candidate summaries (all twelve)

### C-A1 — TE-subfamily stratification of Pol II ChIA-PET vs Hi-C loop discordance (K562)
Descriptive OR of pre-registered TE subfamilies among discordant loop anchors vs mappability/GC/length-matched null. Primary kill: MAPQ≥30. **Recommended.**

### C-B1 — AluY at convergent CTCF+RAD21 anchors + AG allele-prior (non-holdout)
Highest raw score. Strong narrative continuity with prospective panel, but estimand mixes architecture enrichment with allele prior → weaker L0 purity and slower kill. **Park.**

### C-C1 — SVA vs Alu differential occupancy of Hi-C loop anchors
Clean TE-class contrast on a single assay; less novel than discordance framing; still desk-feasible.

### C-D1 — TE divergence/age vs cross-assay loop-call reproducibility
Age-bin exposure; needs careful divergence annotation; medium kill-speed.

### C-E1 — Mappability-matched TE vs non-TE rare-SNV PWM Δ (non-HBB)
Close to already-explored PWM/scorer path; novelty low; risk of HBB-adjacent language.

### C-F1 — Pol II ChIA-PET–exclusive loop TE density vs shared (unstratified)
Weaker than C-A1 (no subfamily stratification); useful sensitivity sibling, not primary.

### C-G1 — RAD21 ChIA-PET vs CTCF ChIA-PET TE-anchor odds
Requires two ChIA-PET targets; data readiness lower than Pol II+Hi-C pair.

### C-H1 — Micro-C vs Hi-C TE recovery differential
High novelty (sits on Akgol Oksuz map) but **data dependency** on processed Micro-C loops; second by score, not selected.

### C-I1 — AluJo negative-control calibration of loop-call FP rate
Control methodology, not a primary scientific claim; keep as control inside C-A1.

### C-J1 — TE insertion orientation vs loop-anchor asymmetry
Interesting but noisier exposure definition; medium priority.

### C-K1 — CTCF ChIA-PET TE-subfamily discordance vs Hi-C
**Preferred fallback** if Pol II processed bedpe blocked (`BLOCKED_DATA` branch).

### C-L1 — Cross-cell-line transfer (K562 → GM12878)
Needs second cell line processed pair; defer until C-A1 resolves.

---

## 8. Top-3 cards

### Card 1 — C-B1 (score 7.47) — NOT SELECTED
- **Claim sketch:** AluY enriched at convergent CTCF+RAD21 anchors among non-holdout loci with AG-prior support.  
- **Strength:** Impact, track heat, AG reuse.  
- **Weakness:** Identifiability (I=6.8), kill-speed (K=6.3), C1-bleed risk.  
- **48h kill:** Requires AG path + motif/orientation intersect — not a 2 h MAPQ gate.

### Card 2 — C-H1 (score 7.12) — PARK
- **Claim sketch:** TE recovery differs Micro-C vs Hi-C after matching.  
- **Strength:** Novelty vs Akgol Oksuz gap.  
- **Weakness:** Data readiness (D=5.0) if Micro-C processed loops missing.  
- **Gate:** Only promote if processed Micro-C bedpe verified.

### Card 3 — C-A1 (score 7.06) — SELECTED (`VALIDATE_DESK`)
- **Claim sketch:** Discordant Pol II ChIA-PET vs Hi-C anchors enriched for ≥1 TE subfamily (OR≥1.3) after matching; falsify if OR<1.1 under MAPQ≥30 + replication.  
- **Strength:** I=7.8, K=8.2; ENCODE processed bedpe path.  
- **Weakness:** Novelty moderate (N=5.2) — acceptable under honest reformulation.  
- **48h kill:** MAPQ≥30 sensitivity on discordant set.

---

## 9. Adversarial reviews

### Adversary A — “This is just Akgol Oksuz again”
**Rebuttal:** Akgol Oksuz varies **protocol parameters** within 3C family. C-A1 fixes protocols as given (ENCODE releases) and tests **TE-subfamily × discordance** with matched nulls. Different estimand. Cite DOI 10.1038/s41592-021-01248-7 explicitly in claim novelty note.

### Adversary B — “TE signal is mappability in a costume”
**Rebuttal:** Pre-register MAPQ≥30 / high-mappability kill as **primary falsifier**. If OR collapses <1.1 → REJECT and file `null_results/`. That is a feature, not a bug.

### Adversary C — “You will smuggle C1 / holdout into the universe”
**Rebuttal:** Forbidden language table; no sealed holdout paths; no E/P coordinate edits; experiment folder isolated from Stage-3 slots. Reviewer checklist before any intersect script lands.

### Adversary D — “C-B1 is higher score — you sandbagged”
**Rebuttal:** Rubric §5 promotion rule published **before** selection. Raw max ≠ promote. Document I×K comparison in notes.md.

---

## 10. 48-hour kill-test (YAML)

```yaml
# C-A1 48h kill-test — desk only, no wet, no holdout
kill_test_id: C-A1_48h_MAPQ
candidate: C-A1
window_hours: 48
status: PREREGISTERED
steps:
  - id: T0
    action: Verify processed Pol II ChIA-PET + Hi-C K562 bedpe (metadata)
    pass_if: usable_processed_bedpe_pol2 == yes AND usable_processed_bedpe_hic == yes
    fail_status: BLOCKED_DATA
    on_fail: demote_to [C-K1, C-B1]
  - id: T1_MAPQ
    action: Recompute primary TE-subfamily OR after MAPQ>=30 / high-mappability gate
    reject_if: all_pre_registered_subfamily_OR < 1.1
    mcid_ref: claim.md
  - id: T2_CTCF_GATE
    action: Positive CTCF shared-loop sanity gate
    inconclusive_if: gate_fails_pipeline_sanity
forbidden:
  - download_multi_GB_hic
  - unseal_holdout
  - edit_C1_EP_locks
  - invent_OR_before_analysis
```

---

## 11. Two-week desk plan

| Day | Milestone | Exit |
|-----|-----------|------|
| 0–1 | T0 accession probe + **ACCESSION_FREEZE** | PASS / BLOCKED_DATA |
| 2 | Download **small** bedpe only; fill md5 in `data_manifest.md` | Manifest complete |
| 3 | Pin RMSK + mappability tracks (assembly-matched GRCh38) | Paths recorded |
| 4–5 | Build discordant vs shared anchor tables | Counts only (no TE OR yet) |
| 6 | Freeze matched-null procedure (P3 discipline) | Written + hashed inputs |
| 7–8 | Primary TE-subfamily OR + CI | Results.json draft |
| 9 | MAPQ≥30 kill + CTCF gate | REJECT / PASS_DESK / INCONCLUSIVE |
| 10 | Replication file / second biorep | Stability check |
| 11–12 | decision.md + null_results filing if needed | Honest verdict |
| 13–14 | Buffer / demote to C-K1 if blocked | No wet creep |

---

## 12. Preregistration draft (Standard tier)

Expand in experiment folder (authoritative arts: `claim.md`, `controls.md`, `notes.md`, `decision.md`):

- **Status:** `PREREGISTERED_DESK`
- **L0:** Descriptive
- **Frozen claim:** Discordant Pol II ChIA-PET vs Hi-C loop anchors in K562 are enriched for ≥1 pre-registered TE subfamily after mappability matching (**OR≥1.3**); falsified if **OR<1.1** under MAPQ≥30 + replication
- **Universe / exposure / outcome:** K562 processed loop anchors; TE subfamily; discordance class
- **Controls:** CTCF positive gate; AluJo negative/contrast; matched-null covariates
- **Language:** NOT causal; NOT wet; NOT holdout; NOT C1 E/P shopping
- **Novelty:** TE-subfamily + mappability matching vs Akgol Oksuz protocol-parameter focus; no SE/HBB overlap

---

## 13. Data manifest (report-level; experiment file is authoritative after freeze)

### Rejected / wrong placeholders
| Accession | Status | Action |
|-----------|--------|--------|
| `ENCSR000BZZ` | Exists; target **ESR1** ChIA-PET | **WRONG** for Pol II C-A1 — do not use |
| `ENCSR444WCX` | **404** | Discard |

### T0-verified processed bedpe (metadata; multi-GB not downloaded)
| Role | Experiment | Files | Assembly |
|------|------------|-------|----------|
| Pol II / RNAPII ChIA-PET K562 | `ENCSR880DSH` | `ENCFF511QFN` (rep1, **preferred_default**), `ENCFF759YBZ` (rep2), `ENCFF030PMM` (rep3) | GRCh38 bedpe loops |
| Hi-C K562 loops | `ENCSR545YBD` (in situ) | `ENCFF693XIL` (HiCCUPS merged_loops_30, **preferred_default**) | GRCh38 |
| Hi-C alt | `ENCSR479XDG` (intact) | `ENCFF598CLH` / `ENCFF256ZMD` (localizer) | GRCh38 |

**Primary freeze (see `ACCESSION_FREEZE_v1.md`):** Pol II = `ENCFF511QFN`; Hi-C = `ENCFF693XIL`.

---

## 14. Risk register

| ID | Risk | Sev | Mitigation |
|----|------|-----|------------|
| R1 | Pol II only FASTQ | High | T0 → BLOCKED_DATA → C-K1/C-B1 |
| R2 | Wrong accession (ESR1 / 404) | High | Freeze file; never hard-code placeholders |
| R3 | Mappability confounding | High | MAPQ≥30 primary kill |
| R4 | C1 / holdout bleed | High | Forbidden paths; isolated experiment folder |
| R5 | Causal overclaim | Med | Allowed/forbidden language |
| R6 | hg19/GRCh38 mix | Med | Freeze GRCh38 |
| R7 | Multi-GB download creep | Med | bedpe-only; no `.hic` commit |
| R8 | Score-max politics (C-B1) | Low | Published I×K rule |

---

## 15. What this report does NOT mean

1. Does **not** validate C1 biology or unlock wet-lab GO  
2. Does **not** claim TEs cause chromatin loops  
3. Does **not** reopen SE/LLPS closed experiments  
4. Does **not** revive HBB TE enrichment  
5. Does **not** authorize oligo order or holdout unseal  
6. Does **not** invent enrichment ORs before analysis  
7. Does **not** treat `c048650` as forever HEAD — it is the **inspection** pin only  

---

## 16. Decision record and stop conditions

**Promote:** C-A1 → Standard-tier desk preregistration (`VALIDATE_DESK`).

**Do not promote now:** C-B1 (final 7.47 > C-A1 7.06, but worse identifiability / kill-test tradeoff).

**Park:** C-C1 … C-L1; **C-K1** is preferred data-availability fallback if Pol II processed loops missing; **C-H1** if Micro-C bedpe later verified.

**Stop condition:** Если bedpe processed loop calls для Pol II ChIA-PET K562 недоступны в processed form (только raw FASTQ) → status `BLOCKED_DATA`; demote C-A1 and consider C-B1 or C-K1.

**Decision recorded:** `VALIDATE_DESK` for C-A1 (recommended over higher-scoring C-B1 due to cheaper kill-test / clearer estimand).
