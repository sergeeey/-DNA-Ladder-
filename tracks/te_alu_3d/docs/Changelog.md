# Changelog

## 2026-07-21 — C-D1 TE age vs loop reproducibility REJECT

- **C-D1** (`exp_te_age_loop_reproducibility/`): milliDiv tertile vs Pol II↔Hi-C
  repro; primary Δ **−0.0037**; Alu-only **−0.0043** → **REJECT** / FAIL_KILL
- null_results `20260721-te-age-vs-loop-reproducibility.md`; registry → REJECT_CLOSED
- **C-E1** T0 (`exp_te_vs_nonte_rare_snv_pwm/`): claim freeze; **PENDING_FETCH**
  (no genome-wide non-HBB rare-SNV panel on disk; holdout SEALED)
- Wave doc amended; `next_fruit_recommend: C-E1`; holdout/C1/wet untouched

## 2026-07-21 — C-H1 robustness + C-F1/C-G1 BLOCKED_DATA

- **C-H1** sensitivity (`exp_te_derived_pels_gnocchi`): core/LOCO |\Δ|≥0.20; LINE-only
  |\Δ|=0.025 kill → desk **SUPPORT_WITH_CAVEATS** (primary 0.211 unchanged)
- **C-F1** TRUE Mustache↔HiCCUPS TE concordance: `exp_te_loop_caller_concordance/`
  T0 → **BLOCKED_DATA** (no Mustache K562 GRCh38 bedpe; HiCCUPS ENCFF693XIL ok)
- **C-G1** T0 RAD21 vs CTCF ChIA TE odds: `exp_rad21_vs_ctcf_chia_te_odds/` →
  **BLOCKED_DATA** (CTCF `ENCFF118PBQ` ok; RAD21 no GRCh38 loop bedpe)
- Wave: `09_outputs/prospective/AUTONOMOUS_DESK_WAVE_2026-07-21.md`
- Registry: C-F1/C-G1/C-H1 updated; `next_fruit_recommend: C-D1`
- Holdout/C1/wet untouched

## 2026-07-20 — C-L1 L1HS@CTCF REJECT + autonomous wave STOP

- True **C-L1** (NOT cross-cell): `exp_l1hs_ctcf_loop_anchors/`
- Unit = CTCF peak on vs off Hi-C anchor; L1HS 5′UTR (2 kb); match chrom/length/umap
- K562 OR **0.143** / HCT116 **0.200**; umap kill; null_results REJECT
- Wave summary `09_outputs/prospective/AUTONOMOUS_DESK_WAVE_2026-07-20.md`; `next_fruit_recommend: PAUSE_HUMAN`

## 2026-07-20 — C-H1 TE-pELS Gnocchi SUPPORT + C-I1 Micro-C BLOCKED_DATA

- True **C-H1** (NOT Micro-C): se_llps `exp_te_derived_pels_gnocchi` → **SUPPORT** |\Delta|=0.211
- True **C-I1** (Deep Research original Micro-C C-H1): `exp_microc_vs_hic_alu_anchors`
  T0 ENCODE+4DN → **BLOCKED_DATA** (no processed Micro-C loop bedpe; pairs/hic/mcool only)
- Registry remapped; `next_fruit_recommend: C-L1`; AluJo NC parked as C-A1 control
- Holdout/C1/wet untouched

## 2026-07-20 — C-A2 SVA_F dELS switching → REJECT (FAIL_KILL)

- True **C-A2** (NOT ChIA-PET): `experiments/exp_sva_f_ccre_state_switching/`
- Claim: OR(switcher|SVA_F dELS) ≥ 1.4 vs matched non-TE; kill OR&lt;1.1 on ≥2 panels
- Match-before-outcomes: chrom/length/GC/TSS + held-out SK-N-SH baseline; k=5; seed 20260720
- Data: SCREEN Registry-V3 + 10 ENCODE v3 Full-class beds (single CTS matrix 404 → panel OK)
- Primary Fisher OR **0.489** (CI 0.243–0.985); odd 0.655 / even 0.411 — both kill
- null_results REJECT filed; registry C-A2 → `REJECT_CLOSED`; next fruit **C-H1** (else C-L1)
- ChIA-PET alias remains PARKED as `C-K1-CTCF-chia-fallback`; holdout/C1/wet untouched

## 2026-07-20 — C-K1 PLAC vs Hi-C Alu anchors → BLOCKED_DATA

- Standard-tier prereg: `experiments/exp_plac_vs_hic_alu_anchors/` (claim/controls/notes)
- Claim: H3K4me3 PLAC-seq AluSz OR ≥ 1.5 vs matched Hi-C (≥1 cell; prefer GM12878);
  falsify OR < 1.1 after umap ≥ 0.3; distinct from C-A1 Pol II ChIA-PET discordance
- T0 probe ENCODE+4DN (`scripts/t0_probe_plac_vs_hic.py` → `data/t0_accession_probe.json`):
  ENCODE PLAC-seq assay **404**; K562/GM12878 4DN PLAC = pairs/hic/mcool only; near-miss
  H3K4me3 ChIA-PET `ENCSR000FDF` hg19 TSV + multi-assay union bedpe **rejected**
- Decision **`BLOCKED_DATA`** (OR not computed); next fruit was queued as C-A2 (later filled
  as true SVA_F dELS switching, not ChIA-PET)
- Registry C-K1 → `BLOCKED_DATA`; holdout/C1/wet untouched

## 2026-07-20 — Next fruit C-B1 started (topology/CRISPR under se_llps; TE AluY+AG still parked)

- Standing order after C-A1 close: open **C-B1** as Predictive topology-community ΔAUC over SE
  for CRISPR E–G (K562) at `tracks/se_llps/experiments/exp_topology_community_crispr_eg/`
- Registry AluY@CTCF+RAD21+AG candidate renamed in notes to **C-B1-TE-AluY-AG** (still PARKED)
- TE track: no new OR analysis; holdout/C1/wet untouched

## 2026-07-20 — C-A1 desk CLOSED → INCONCLUSIVE_CROSS_CELL

- T6 caller-swap: Mustache N/A on ENCODE; DELTA `ENCFF657QKE` AluSz OR **0.913**
  (vs HiCCUPS 0.908) → FAIL robust; intact localizer sens. OR ≈ 1.107 (not primary)
- Optional robustness: PLAC-seq H3K4me3 **SKIPPED** (no cheap K562 processed bedpe);
  chrom block-bootstrap note from T3 (CI 0.866–0.958)
- Figures: `results/figures/or_forest_cross_cell.{svg,png}`, `umap_sensitivity_k562.{svg,png}`
- Terminal decision `INCONCLUSIVE_CROSS_CELL`; null_results **INCONCLUSIVE** filed
  `null_results/20260720-te-chia-vs-hic-alusz-anchor-discordance.md` + INDEX track `te_alu_3d`
- Repro stub `workflow/README.md`; `draft_abstract.md`; `NEXT_FRUIT_NOTE.md` → recommend C-B1
- Registry C-A1 → `INCONCLUSIVE_CLOSED`; PAUSE / Deep Research note updated
- Holdout/C1/wet untouched; C-B1 analysis **not** started

## 2026-07-20 — C-A1 T5b HCT116 replication → still INCONCLUSIVE_REPLICATION

- Freeze HCT116: Pol II `ENCFF322FOT` (`ENCSR035PVZ`) + Hi-C HiCCUPS `ENCFF060QTI`
  (`ENCSR123UVP`, untreated RAD21-AID) + CTCF `ENCFF463FGL` (`ENCSR240PRQ`)
  → `ACCESSION_FREEZE_replication_HCT116_v1.md` (RAD21/CTCF ChIA-PET rejected as Pol II
  substitutes; auxin-treated `ENCFF522WVV` rejected)
- Same AluSz pipeline as K562/GM12878 → OR **1.280** (Woolf CI 1.162–1.410) → mid-zone
  `INCONCLUSIVE_REPLICATION`; CTCF gate **PASS** (OR ≈ 8.35)
- Optional umap≥0.3 → OR **1.281** (still mid-zone)
- Three-cell synthesis: K562 FAIL (0.91/0.90) vs GM12878 1.252 + HCT116 1.280 — sign
  inconsistent, but falsify arm (replication < 1.15) **not** met → **null_results/ not filed**
- Arts: `results/replication_hct116_OR_CI.{json,md}`,
  `results/replication_hct116_umap_sensitivity.{json,md}`; script `--celltype HCT116`
- decision/claim/data_manifest/Tasktracker updated; holdout/C1/wet untouched

## 2026-07-20 — C-A1 T4 umap + T5 GM12878 → INCONCLUSIVE_REPLICATION

- T4: Hoffman Umap k100; MAPQ=N/A on processed bedpe; mean umap ≥0.3 / ≥0.5 sensitivity
  → AluSz OR **0.898** / **0.894** (still < 1.1) — strengthens K562 FAIL
- T5: freeze GM12878 Pol II `ENCFF913VWM` + Hi-C `ENCFF781ASD` + CTCF `ENCFF796WRU`
  (`ACCESSION_FREEZE_replication_v1.md`); same AluSz pipeline → OR **1.252** (CI 1.172–1.339)
  → `INCONCLUSIVE_REPLICATION`; CTCF gate PASS (OR ≈ 10.74)
- Arts: `results/sensitivity_mappability.{json,md}`, `results/replication_gm12878_OR_CI.{json,md}`
- `null_results/` **not filed** (replication OR not < 1.15); primary TE remains AluSz
- Scripts/tests: `t4_mappability_sensitivity.py`, `t5_replication_celltype.py`, `test_t4_t5_unit.py`
- decision/claim/controls/data_manifest updated; holdout/C1/wet untouched

## 2026-07-20 — C-A1 T3 primary AluSz OR → FAIL_DESK_PRIMARY

- Script: `scripts/t3_primary_alusz_or.py` — merged ≥1 kb anchors; primary TE overlap on fixed 1 kb midpoint windows; Fisher OR + Woolf CI + chrom block-bootstrap; matched-null n_perm=200 (chr+width; GC PENDING)
- Primary AluSz: OR **0.908** (95% CI 0.851–0.967); n anchors Pol II **572808** / Hi-C **17183** → **FAIL_DESK_PRIMARY** (OR < 1.1)
- Arts: `results/primary_result_OR_CI.{tsv,json,md}`, `permutation_null_summary.json`, `exploratory_secondary_TE.tsv` (AluJo≈0.99, SVA_F exploratory)
- MAPQ: `PENDING_MAPPABILITY` (processed bedpe lack MAPQ; umap absent); `null_results/` not filed (claim REJECT needs MAPQ+replication)
- decision/claim/controls + unit tests updated; holdout/C1/wet untouched

## 2026-07-20 — C-A1 T0→T2 download + CTCF gate PASS

- Download scripts: `t1_download_primary_inputs.py` → bedpe `ENCFF511QFN` / `ENCFF693XIL`, CTCF `ENCFF769AUF`, UCSC `rmsk.txt.gz`; checksums in `data/download_checksums.json` + `data_manifest.md`
- T2 positive control: `t2_positive_control_ctcf_gate.py` → Fisher OR **5.12** (95% CI 4.91–5.34) ≥ 2.0 → **PASS** / `PENDING_PRIMARY`
- Arts: `results/positive_control_ctcf_gate.json|.md`; T1 skeleton `results/t1_annotation_skeleton.json` (`EXPLORATORY_PARTIAL`; no primary TE OR)
- CTCF freeze: `ENCFF769AUF` (`ENCSR000AKO`); large binaries gitignored under `data/input/`
- Unit tests: `tests/test_ctcf_gate_unit.py`

## 2026-07-20 — C-A1 report expand + accession freeze

- Expand `DEEP_RESEARCH_REPORT_C_A1_v1.md` to full 16-section Deep Research structure (scores: C-B1 7.47 > C-A1 7.06; C-A1 still recommended)
- Registry scores aligned; inspection commit pin `c048650`
- Freeze primary bedpe: Pol II **`ENCFF511QFN`**, Hi-C **`ENCFF693XIL`** (`ACCESSION_FREEZE_v1.md`)
- claim/data_manifest/decision updated; T0 probe PASS; no OR results; no multi-GB download

## 2026-07-20 — C-A1 VALIDATE_DESK (loop-assay discordance prereg)

- Persist Deep Research Report v1.0 recommending C-A1: `09_outputs/prospective/DEEP_RESEARCH_REPORT_C_A1_v1.md`
- Candidate registry C-A1…C-L1: `09_outputs/prospective/candidate_registry_deep_research_v1.yaml`
- Standard-tier desk experiment: `experiments/exp_te_loop_assay_discordance_chia_vs_hic/` (claim/controls/notes/decision PENDING_T0)
- T0 ENCODE metadata probe (no large downloads): `scripts/t0_probe_encode_accessions.py` → `data/t0_accession_probe.json`
- Explicit: not wet-lab; holdout SEALED; no C1 E/P or GO edits; no oligo order; no SE/HBB claim overlap

## 2026-07-20 — Historical brief v1.1 (publication-ready auditability)

- `PROJECT_HISTORICAL_BRIEF_v1.md` → report_version 1.1: YAML snapshot header + commit pin, claim-status table, status glossary, careful C1 framing (desk retain ≠ wet/biology proof)
- README link text updated to status-brief v1.1
- External review upgrade (~9/10 → publication-ready); wet-lab GO signatures untouched; holdout remains SEALED

## 2026-07-16 — B0 desk closure (still UNSIGNED)

- Backbone desk nominate: Promega E8411 (`B0_backbone_desk_nominate_v1.md`)
- Insert-verify + Sanger primers; B-min hash spotcheck; PO draft; transfection day card
- A1 ready pack UNSIGNED; A2 Capture HELD; holdout SEALED reminder; HUDEP-2 RNA ABSENT note
- Oligo order / wet-lab still FORBIDDEN until human GO signature

## 2026-07-15 — Kill-sprint P1/P2/P5

- G4a multi-sample → **PASS_DESK_ROBUST** (3113/3114/3115 + VC); kills none
- C1 satmut 301bp: PWM all + AG top100 → C1 rank 1; **ALLELE_LEAN_RETAINED**
- Reporter robustness technical OK; R1 length-AG pending
- Report: `KILL_SPRINT_RESULTS_v1.md`

## 2026-07-15 — Stage-2 reporter panel DESK READY (8 alleles)

- REF/ALT windows 301/1kb/2kb for C1,C2,C3,A114,ARCH754,ARCH518,N3,W1
- Arts: `STAGE2_REPORTER_PANEL_v1.md`, `stage2_reporter_panel_v1.json`, `Stage2_oligo_checklist_v1.md`
- FASTA: `pilot_scaffold/data/cultivation/stage2_reporters/` — ORDER FORBIDDEN
- Stage-3 slots unchanged (LOCKED)

## 2026-07-15 — AlphaGenome key PERSISTED (user accepted risk)

- `.env` gitignored; user explicit accept — agents must auto-load, not re-ask
- `load_project_env.py` wired into AG adapter, contact-Δ, R4, C1 unpack, rescore
- Note: `CREDENTIALS_LOCAL_ACCEPTED.md`

## 2026-07-15 — AlphaGenome key restored + Stage-1 full AG rescore

- Ключ был в чате 2026-07-14; в новой сессии не подхватился (не писался в repo by design)
- Восстановлен в gitignored `.env`; adapter читает `.env` через setdefault
- Doscore 16 missing alleles → **16/16 SCORED**; Stage-3 слоты **не** пересобраны (LOCKED)
- Script: `rescore_stage1_ag_missing.py`

## 2026-07-15 — Stage-1 desk-screen COMPLETE (curated + Stage-3 LOCKED)

- Pool n=28 non-holdout Alu/SVA SNV; frozen curated panel n=13
- Stage-3 slots LOCKED (arch×2, C3 convergence, W1 disagreement, N3 negative); C1 = TEMPLATE_DEV only
- Arts: `STAGE1_RESULTS_2026-07-15.md`, `stage1_desk_screen_v1.json/.tsv`, updated `prospective_panel_registry_v1.yaml`
- Caveat: no AG API this run; G2 dist=0 bug fixed; PWM exploratory

## 2026-07-15 — Scale protocol: prospective panel (process, not C1 proof)

- `SCALE_PROTOCOL_prospective_panel_v1.md` — G0–G8, Stage1–3 funnel, pre-registered Stage-3 slots, novelty scenarios A–D
- `prospective_panel_registry_v1.yaml` — C1 = TEMPLATE_DEV; empty ACT/ARCH/NEG/POS slots
- `templates/GATE_CARD_panel_admission_v1.md` — per-variant gate card
- Explicit: scale the validation process; C1 is template, not confirmatory panel seed by default

## 2026-07-15 — Work report C1 desk

- `09_outputs/prospective/WORK_REPORT_C1_desk_2026-07-15.md` — сводный отчёт desk-кампании A+B

## 2026-07-15 — OT amplicon primers + locked-P TSS desk

- `OT_amplicon_primer_panel_desk_v1.md` + `ot_amplicon_primers_desk_v1.json` (C1, RADIL, KDM2B, RPAP2, UPF3A)
- Locked P: no TSS inside; nearest **LRRN4CL**; body overlap **BSCL2** / HNRNPUL2-BSCL2
- Script: `pilot_scaffold/tools/design_ot_amplicon_primers_v1.py` — order still forbidden

## 2026-07-15 — GO-note draft + B oligo checklist + Capture-C quote

- `GO_note_draft_C1_B_first_v1.md` — UNSIGNED; B0→A1→A2; OT panel slots (RADIL/KDM2B/…)
- `BranchB_oligo_checklist_v1.md` — B-min first + escalation; order still forbidden
- `CaptureC_bait_quote_sheet_v1.md` — locked E/P quote-only

## 2026-07-15 — NDE Engine 4+2 for C1 A+B

- `09_outputs/prospective/NDE_C1_exhaustion_A_plus_B_v1.md`
- Exhaustion: alive high-prior {M3, M1, M0}; A/B differentiating matrix; Engine 1/3 deferred
- Constraint relaxations ranked: B independent of PE → reporter escalation → OT panel

## 2026-07-15 — Plain-language handoff saved

- `09_outputs/prospective/HANDOFF_PLAIN_LANGUAGE.md` — статус C1 PE / ветки A–C без жаргона

## 2026-07-15 — CRISPOR genome-wide OT for PE PD1

- CRISPOR hg38 batch `aurVfmrzWeRL946FQvDv`: PD1 MIT **69**, CFD **89**, OT 0/0/0/6/115
- Exon watchlist includes **RADIL** (mm3); on-target intron:ZBTB3
- Verdict **CONDITIONAL_PASS**; oligo order still blocked pending ngRNA OT + GO
- Arts: `G5_PE_OT_CRISPOR_PD1_v1.md`, `crispor_c1/`

## 2026-07-15 — Sequential desk: PE validate → HUDEP-2 CTCF → Branch B reporter

- PrimeDesign CLI external redesign PASS; PD1 spacer matches heuristic; neighborhood OT only (genome-wide pending)
- HUDEP-2 CTCF peaks (GSM2805379/GSM3671075): planted P1 → P-side `chr11:62694751-62695044` (GRCh38)
- Branch B reporter windows + FASTA (301 bp / 1 kb / 2 kb); nearest genes ZBTB3/POLR2G…
- Arts: `G5_PE_validation_external_C1_v1.md`, `P1_local_HUDEP2_CTCF_confirm_v1.md`, `BranchB_reporter_design_v1.md`

## 2026-07-15 — G4b protocol freeze + PE shortlist + provisional panel

- `G4b_protocol_freeze_v1.md`: estimand, baits, MCID (|ΔContact|≥25% WT or |ΔOE|≥0.5)
- `G5_PE_shortlist_C1_desk_v1.md`: 24 PE geometries; top +strand spacer `CGTCCGATAAGCCCTGCCCC`
- `BranchA_panel_freeze_provisional_v1.md`; claim pack + PAUSE_PIN updated
- Wet-lab still NO-GO; no guide ordering

## 2026-07-15 — Overnight complete: G4a+P1 desk PASS

- All GSM4873113–3118 `.hic` downloaded + SHA256
- P1-system PASS_DESK: OE HS1–HS5 DEL/WT ≈ 0.34; HBB–OR52A1 OE up ≈ 1.57×
- Architecture freeze → provisional language only; wet-lab still NO-GO
- Report: `MORNING_STATUS_2026-07-15.md`

## 2026-07-14 night — Autonomous overnight

- Single orchestrator: Capture→GW downloads, auto P1 desk, checksums, morning report
- Arts: `overnight_orchestrator.ps1`, `AUTONOMOUS_OVERNIGHT_PLAN.md`, `G4b_protocol_draft_v1.md`, `BranchA_panel_skeleton_NOGO.md`
- Competing curl jobs killed to protect resume integrity

## 2026-07-14 — Non-stop pipeline after G4a PASS

- Started Capture + edit Hi-C downloads (GSM4873114–3118); sequential curl resume
- P1 desk script + watcher: `run_p1_3primeHS1_desk.py`, `watch_p1_and_analyze.ps1`
- Branch A live board + Branch B activity continuum + planted P1 design + PE desk stub
- WT β-globin dump: HS1–HS5 OE≈3.23 (anchor contact present in GSM4873113)

## 2026-07-14 — G4a desk PASS (GSM4873113)

- Local juicer_tools dump KR observed/OE at locked E–P (hg19)
- Enrichment ~3.4× (10 kb) / ~2.5× (25 kb) vs same-distance background; OE≥2.1
- Verdict `PASS_DESK`; architecture freeze still NO-GO until P1
- Arts: `G4a_gsm4873113_desk_pass_v1.md`, `G4a_gsm4873113_metrics.json`, `g4a_dumps/`

## 2026-07-14 — Priority correction + GSE160422 unlock path

- Frozen C1 claim pack: activity primary; architecture language forbidden until G4a/P1
- G4a/P1 candidate = GSE160422/GSE160425 (WT + 3′HS1 del/inv Hi-C); Capture reserved for β-globin P1
- Started download GSM4873113 WT `.hic` → `D:\DNK - 2\data\HUDEP2_GSE160422\`
- LiftOver C1/E/P GRCh38→hg19 (Ensembl REST) → `c1_ep_liftover_hg19.yaml`
- ARCHCODE: local repo TECHNICAL_PARTIAL / EXPLORATORY only (not scientific unlock)
- Arts: `C1_claim_freeze_pack_v1.md`, `unlock_search_log_2026-07-14.md`, `GSE160422_download_manifest.md`, `G4a_P1_inspection_protocol_GSE160422.md`, `archcode_technical_admission_2026-07-14.md`

## 2026-07-14 — G6 matching + PAUSE PIN

- GC + K562 ATAC amendment: N3 KEEP; N1/N2 DROP
- ARCHCODE still ABSENT locally (superseded same-day: repo found, technical only)
- `PAUSE_PIN_2026-07-14.md` — desk ceiling until HUDEP-2 G4 / P1 / ARCHCODE

## 2026-07-14 — G6 control panel desk

- Draft panel: C1–C3 + N1–N3 (AG-low neutrals); architecture P1 deferred
- `panel_frozen: false`; NO_GO_FOR_WET_LAB (G4/G5/G6 incomplete)
- Artifact: `09_outputs/prospective/G6_control_panel_desk_pass_v1.md`

## 2026-07-14 — C2 unpack + G5 draft

- C1/C2 share activity program (9/10 top TF×biosample); both M3-lean
- G5 desk: SpCas9 BE window FAIL (pos 17–18) → prime-edit if ever; wet-lab STOPPED
- Artifacts: `c1_c2_channel_compare.md`, `G5_editability_desk_pass_v1.md`

## 2026-07-14 — C1 CHIP_TF channel unpack

- `run_c1_channel_unpack.py`: C1 Δ dominated by POLR2/GABPB1/RBFOX2; CTCF/RAD21 best ~rank 476/1617
- Lean **M3_activity** → downgrade M1-only freeze path for C1
- Report: `09_outputs/prospective/c1_chip_tf_channel_unpack.md`

## 2026-07-14 — G2 prep: PWM vs AG for C1–C3

- Ensembl fasta for C1/C2 + C3 under `data/cultivation/`
- `run_g2_r4_shortlist.py` → C1/C2 Arm B (AG≫motif); C3 motif≫AG
- Report: `09_outputs/prospective/g2_r4_shortlist.md`

## 2026-07-14 — G3/G4 desk + R4 panel n=12

- Expanded AG cultivation to 12 vars / 6 peaks; shortlist → C1–C3 (`62753923`, `72434037`)
- Desk fill: `G3G4_r4_shortlist_desk_pass_v1.md` (K562 proxy E/P; HUDEP-2 G4 still FAIL)

## 2026-07-14 — R4: AlphaGenome cultivation shortlist (non-holdout)

- `adapters/ag_contact_delta.py` + `run_ag_cultivation_r4.py`
- Scored 6 rare Alu SNVs near HUDEP-2 CTCF outside HBB+HO_*; holdout untouched
- Shortlist ≤3 IMMATURE → `09_outputs/prospective/ag_cultivation_r4_*`

## 2026-07-14 — AlphaGenome smoke PASS → alternate primary AVAILABLE

- Wired live `alphagenome_adapter.py` (CONTACT_MAPS+CHIP_TF); key via env only
- `second_scorer_admission` → **AVAILABLE** (`alphagenome_variant_contact`)
- `score_freeze.alternate_primary` recorded; status still EXPLORATORY_FROZEN
- Added `.gitignore` / `.env.example` (never commit API keys)

## 2026-07-14 — Queue A→B→C executed

- **A:** admission re-run → ARCHCODE/AlphaGenome **FAIL** (no credentials); log `queue_A_admission_attempt_2026-07-14.md`
- **B:** downloaded K562 Hi-C loops/domains (`ENCSR545YBD` / ENCFF693XIL+…) → `data/hic_proxy/`; L-HO_* has proxy loops near HUDEP-2 CTCF (`queue_B_proxy_hic_LHO_2026-07-14.md`)
- **C:** confirmatory/lab paths paused until credentials (`queue_C_paused_until_credentials_2026-07-14.md`)

## 2026-07-14 — Desk research: G4 locus contact + unblind draft

- `09_outputs/prospective/G4_contact_desk_pass_v1.md`: HUDEP-2 CTCF counts in L-HO_*; allele E–P still FAIL; public HUDEP-2 contact gap at 64–68 Mb
- `07_methods/unblind_protocol_draft_v1.md`: DRAFT_ONLY (`unblind_authorized` stays false)
- Holdout fetch status → COMPLETE_SEALED_UNSCORED; cultivation desk-pass linked

## 2026-07-14 — RDR Router v1 (lean ops)

- Added `07_methods/rdr_router_v1.md`: 6 routing rules, E0–E5, I1–I5, stopping matrix
- No GED/EVSI; maps existing freezes/gates — does not reopen claims

## 2026-07-13 — Queue: second scorer path + AG stub + cultivation H3 + holdout resume

- ARCHCODE still absent → `second_scorer_type_spec.md` + `second_scorer_admission_gate.py` → confirmatory primary **UNAVAILABLE** (PWM not promoted)
- AlphaGenome adapter stub: `pilot_scaffold/adapters/alphagenome_adapter.py` (smoke FAIL without credentials)
- Cultivation desk-pass H1→H3: `09_outputs/prospective/cultivation_desk_pass_v1.md` (locus geography only; no alleles)
- Holdout fetch resumed with `allow_gaps=True` (document API holes; still sealed / unscored)

## 2026-07-13 — Package A: hypothesis registry closure

- Created `00_research_question/hypothesis_registry_v1.md` + `09_outputs/hypothesis_registry_v1.yaml`
- Plain-language closure: `09_outputs/hypothesis_closure_report_2026-07-13.md`
- Closed testable-now HBB enrichment as NOT_SUPPORTED/STOPPED; cultivation IMMATURE; confirmatory BLOCKED
- Synced C status to NOT_SUPPORTED in `scientific_freeze_v1.md` / `score_freeze.yaml` notes (supersedes UNRESOLVED)

## 2026-07-13 — Competitor baseline ensemble (Arm A/B)

- Added `07_methods/competitor_baseline_ensemble.md` (AlphaGenome mandatory; enhancer3D=context; UniChrom/Hi-Compass only with validated allele-delta)
- Adopted **Arm A convergence** vs **Arm B principled disagreement**; rejected “lab only if all models agree”
- Templates: `G2b_model_independence_matrix.yaml`, `G2c_ensemble_classification.yaml`
- Wired into prospective framework + cultivation next-step language

## 2026-07-13 — ARCHCODE-PROSPECTIVE leakage-free framework

- Added `07_methods/archcode_prospective_framework.md` + `pilot_scaffold/prospective_config.yaml`
- Modules: `build_prospective_universe.py`, `baseline_scorers.py`, `leakage_audit.py`, `run_prospective_baselines.py`
- Outputs under `09_outputs/prospective/` (universe, baselines, G1 audit, G3–G9 templates)
- Tests: `pilot_scaffold/test_prospective_framework.py`
- Explicitly **not** a scorer validation, holdout unblind, or wet-lab GO

## 2026-07-13 — Hypothesis Cultivation Pass (architecture variant)

- Added `07_methods/hypothesis_cultivation_pass_architecture_variant.md`
- Separates the **Growth Loop** (H1→H6 mechanism maturation) from the existing Kill Loop
- Defines five competing explanations, G1–G9 candidate gates, and `IMMATURE_HYPOTHESIS`
- Does **not** reopen the stopped Track A enrichment claim or authorize wet-lab work

## 2026-07-13 — ARCHCODE admission FAIL + cluster diagnostics

- `archcode_admission_gate.py` → **FAIL** (нет binary/provenance) — confirmatory FORBIDDEN
- Checklist: `07_methods/archcode_admission_checklist.md`
- Cluster-aware diagnostics on HBB v1.1 scores: ~1278 variants → **17 TE clusters** (inflation ≈75×)
- Cluster perm_p: T≈0.48, C≈0.47 (ещё слабее, чем variant-level) — claim остаётся STOPPED
- Output: `09_outputs/pilot_chr11/{archcode_admission.json,cluster_diagnostics.json}`

## 2026-07-13 — HBB development re-score with v1.1

- Re-ran dual estimand T/C on HBB/HUDEP-2 with `ctcf_pwm_delta_v1.1` (fp `54a2ad823a0e6b6f`), n_perm=200
- **T:** median_Δ≈0.65, Δ_MAD≈5.00, perm_p≈0.234 → NOT SUPPORTED
- **C:** median_Δ≈0.68, Δ_MAD≈7.04, perm_p≈0.189 → NOT SUPPORTED (v1.0 “near-sig” gone)
- Numbers **not comparable** to v1.0 (different score map); diagnostics only; claim remains STOPPED
- `score_freeze.yaml`: C `hbb_status` → NOT_SUPPORTED

## 2026-07-13 — Holdout sealed (non-HBB erythroid panel)

- `07_methods/holdout_manifest.yaml`: SEALED; windows HO_A/B/C at chr11:64–66 / 65–66 / 67–68 Mb
- Labels locked (`unblind_authorized: false`); `fetch_holdout_inputs.py` fetch-only
- HBB remains development; confirmatory only after unblind protocol
- `fetch_gnomad_window(..., out_prefix=)` to avoid clobbering HBB slice

## 2026-07-13 — Scorer benchmark gate PASS (v1.1)

- Built planted-motif controls: `data/benchmark/` (P1/N1/N2/S2)
- First raw-genome attempt **FAIL** (peak boost dominated motif Δ) — correct kill
- Fixed score map → `ctcf_pwm_delta_v1.1` (fp `54a2ad823a0e6b6f`)
- Gate: median_P−N=0.68, perm_p≈0.001, direction 22/22; auROC=0.70 (pass via OR clause)
- Outputs: `09_outputs/pilot_chr11/benchmark/{scorer_benchmark_report.json,pass_fail.txt}`
- Caveat: synthetic planted motifs; HBB v1.0 enrichment numbers not comparable without re-score

## 2026-07-13 — Scientific freeze v1 (HBB → development)

- Accepted verdict: T NOT SUPPORTED; C exploratory unresolved; claim STOPPED
- Added `scientific_freeze_v1.md` (primary=T, multiplicity, cluster unit, stop rules)
- `scorer_benchmark_spec.md`, `dag_distance_to_ctcf.md`, `holdout_plan.md`
- `score_freeze.yaml` embeds scientific_freeze; HBB labels marked viewed
- `matching_diagnostics.py` → effective N / TE-copy inflation per estimand
- Endpoint language: predicted CTCF motif disruption ≠ 3D disruption

## 2026-07-13 — Exploratory CTCF-PWM scorer + TSS + freeze

- ARCHCODE not in workspace → `ctcf_pwm_delta_v1` (JASPAR-approx Δ) as exploratory only
- Fetched HBB fasta + Ensembl protein-coding TSS (`fetch_sequence_context.py`)
- `score_freeze.yaml` → **EXPLORATORY_FROZEN** (confirmatory still requires ARCHCODE)
- Dual-track re-run: T Δ_MAD=0.43 perm_p=0.23; C Δ_MAD=1.76 perm_p=0.055 → both BLOCKED
- Do not interpret near-sig C as biology (PWM stand-in + no ARCHCODE)

## 2026-07-13 — Dual-track HBB + HUDEP-2 CTCF + Control C

- `fetch_dual_track_inputs.py`: gnomAD HBB window via GraphQL (39 737 vars); HUDEP-2 CTCF ChIP-Atlas SRX5821035
- KC0: HBB+HUDEP-2 **pass**; config preferred_cell_line=HUDEP-2; genomic_window=HBB
- Control C (same subfamily) wired; TE label now `repName|class/family`
- Dual-track re-run: N=1278 TE rare; KC3 dual present; median Δ=0 (LSSIM stub) → KC1 STOP; enrichment BLOCKED
- Still blocked: score UNFROZEN + LSSIM fallback (no confirmatory)

## 2026-07-13 — Code: dual estimand + block permutation

- `build_matched_controls.py`: estimand T (no CTCF) vs C (+CTCF); Control B same-family diagnostic
- `permutation_test.py`: primary `block_matched`; global shuffle = software control; Δ_MAD; KC0; confirmatory_gate
- `run_pilot.py`: dual T/C pipelines; separate manifests/scores/perm/kill; freeze+fallback gates
- Real re-run (ClinVar N=14): T/C both BLOCKED (perm_p≈0.06); KC0 mismatch; UNFROZEN+LSSIM → exploratory
- Note: under T matching, median Δ flipped positive (+0.10) vs legacy run — still not a claim

## 2026-07-13 — Pilot redesign v2 (frozen)

- Added `07_methods/pilot_redesign_v2.md` (KC0, dual estimand T/C, controls A–D, block perm, KC1 Δ_MAD, score freeze)
- Kill criteria → **v1.2** (KC0; estimand-specific KC2; KC1 biological gate suspended until calibration)
- Matched controls → **v0.2**
- `score_freeze.yaml` + `config.yaml` aligned to redesign
- Governing boundary: Track B / MWPM out of scope
- Interpretation: ClinVar N=14 kill = configuration FAIL, Track A unresolved

## 2026-07-13 — Pilot real run (kill-first)

- Added `vcf_loader.py`, `fetch_chr11_inputs.py`, `run_pilot.py`
- Fetched: ENCODE blacklist, genomicSuperDups chr11, rmsk Alu/SVA chr11 (48 718), ClinVar chr11 (259 912)
- Real run: 14 Alu/SVA ClinVar P/LP post-QC; KC1 + permutation gate **STOP**; enrichment blocked
- HBB window (5.2–5.3 Mb): 0 P/LP∩Alu/SVA → insufficient_n (expected kill)
- Docs: Project.md, Changelog.md, Tasktracker.md

## 2026-07-13 — Pilot scaffold

- Created `pilot_scaffold/` with config, QC, matching, scores, permutation, report template
- Dry-run verified kill-first blocking of enrichment_summary
