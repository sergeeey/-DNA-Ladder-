# Project — DNA_TE_3DGenome_Context

## Research question (Track A)

Do rare SNVs inside Alu/SVA show higher **predicted CTCF-motif disruption** than matched non-TE controls after QC?

**Not claimed yet:** confirmed 3D contact / expression / disease effect.  
**Out of scope:** Track B / MWPM until rescue trajectories exist.

## Status

`CURRENT CLAIM STOPPED` · Package A hypothesis closure · HBB = **development set**  
C-A1 desk (`exp_te_loop_assay_discordance_chia_vs_hic`): T3 AluSz OR **0.908** → `FAIL_DESK_PRIMARY` (PENDING_MAPPABILITY; replication pending)

## Operational snapshot

```text
T (total):        NOT SUPPORTED (HBB/HUDEP-2, v1.1)
C (conditional):  NOT SUPPORTED (HBB/HUDEP-2, v1.1)
Cluster (TE):     NOT SUPPORTED (perm_p≈0.48; N_eff≈17 copies)
Scorer bench:     PASS (ctcf_pwm_delta_v1.1 exploratory only)
ARCHCODE admit:   TECHNICAL_PARTIAL / EXPLORATORY (repo local; not scientific validation)
2nd scorer admit: AVAILABLE (AlphaGenome smoke PASS; not CONFIRMATORY_FROZEN)
R4 shortlist:     C1–C3; C1/C2 = shared M3 program
G5 desk:          SpCas9 BE FAIL → PE if ever; wet-lab STOPPED
G6 desk:          N3 KEEP; N1/N2 DROP after GC+ATAC match
Claim freeze:     C1_claim_freeze_pack_v1 (E/P locked; architecture language FORBIDDEN)
G4a candidate:    GSE160422 GSM4873113 → **PASS_DESK**
P1 candidate:     3′HS1 WT/del/inv → **PASS_DESK** (OE HS1–HS5 DEL/WT≈0.34)
Status:           G4b PROTOCOL_DESK_FROZEN; PE CONDITIONAL_PASS; wet-lab NO-GO
Scale:            SCALE_PROTOCOL_prospective_panel_v1 — scale process, not C1 claim
C1 role:          TEMPLATE_DEV (desk template); panel registry SLOTS_OPEN
Holdout:          SEALED — unscored
RDR Router:       next = Stage-1 desk-screen 20–30 via GATE_CARDs (non-holdout)
MWPM:             not tested
```

## Governing docs

| Doc | Path |
|-----|------|
| Scale protocol (panel) | `09_outputs/prospective/SCALE_PROTOCOL_prospective_panel_v1.md` |
| Panel registry | `09_outputs/prospective/prospective_panel_registry_v1.yaml` |
| RDR Router v1 | `07_methods/rdr_router_v1.md` |
| Unblind protocol draft | `07_methods/unblind_protocol_draft_v1.md` |
| G4 contact desk-pass | `09_outputs/prospective/G4_contact_desk_pass_v1.md` |
| AG R4 shortlist | `09_outputs/prospective/ag_cultivation_r4_shortlist.md` |
| G3/G4 R4 desk | `09_outputs/prospective/G3G4_r4_shortlist_desk_pass_v1.md` |
| G2 R4 shortlist | `09_outputs/prospective/g2_r4_shortlist.md` |
| C1 channel unpack | `09_outputs/prospective/c1_chip_tf_channel_unpack.md` |
| C1/C2 compare | `09_outputs/prospective/c1_c2_channel_compare.md` |
| G5 editability desk | `09_outputs/prospective/G5_editability_desk_pass_v1.md` |
| G6 control panel desk | `09_outputs/prospective/G6_control_panel_desk_pass_v1.md` |
| G6 matching amendment | `09_outputs/prospective/g6_matching_amendment.md` |
| Pause pin | `09_outputs/prospective/PAUSE_PIN_2026-07-14.md` |
| C1 claim freeze | `09_outputs/prospective/C1_claim_freeze_pack_v1.md` |
| Unlock search log | `09_outputs/prospective/unlock_search_log_2026-07-14.md` |
| GSE160422 manifest | `09_outputs/prospective/GSE160422_download_manifest.md` |
| G4a/P1 protocol | `09_outputs/prospective/G4a_P1_inspection_protocol_GSE160422.md` |
| C1/E/P hg19 lift | `09_outputs/prospective/c1_ep_liftover_hg19.yaml` |
| ARCHCODE technical | `09_outputs/prospective/archcode_technical_admission_2026-07-14.md` |
| Queue A/B/C (2026-07-14) | `09_outputs/prospective/queue_*_2026-07-14.md` |
| K562 proxy Hi-C | `pilot_scaffold/data/hic_proxy/` |
| Hypothesis registry v1 | `00_research_question/hypothesis_registry_v1.md` |
| Closure report (plain) | `09_outputs/hypothesis_closure_report_2026-07-13.md` |
| Scientific freeze v1 | `07_methods/scientific_freeze_v1.md` |
| Redesign v2 | `07_methods/pilot_redesign_v2.md` |
| Scorer benchmark | `07_methods/scorer_benchmark_spec.md` |
| CTCF DAG | `07_methods/dag_distance_to_ctcf.md` |
| Holdout plan | `07_methods/holdout_plan.md` |
| Hypothesis cultivation pass | `07_methods/hypothesis_cultivation_pass_architecture_variant.md` |
| ARCHCODE-PROSPECTIVE framework | `07_methods/archcode_prospective_framework.md` |
| Second scorer type | `07_methods/second_scorer_type_spec.md` |
| Cultivation desk-pass | `09_outputs/prospective/cultivation_desk_pass_v1.md` |
| Competitor ensemble (Arm A/B) | `07_methods/competitor_baseline_ensemble.md` |
| Score freeze | `pilot_scaffold/score_freeze.yaml` |

## Kill-first

Pipeline: AlphaGenome alternate primary **AVAILABLE** (smoke). Next bottleneck:
**G4a** inspection of HUDEP-2 WT Hi-C at locked E–P (after GSM4873113 completes)
and **P1** 3′HS1 system control — **not** holdout unblind, **not** PWM promotion,
**not** ARCHCODE-as-proof.

## Hypothesis maturity

The enrichment claim remains stopped. A separate prospective architecture-variant
line is `IMMATURE_HYPOTHESIS`: it must pass leakage-free candidate qualification
before any wet-lab GO decision.

`ARCHCODE-PROSPECTIVE` framework status: **FRAMEWORK_ONLY** (universe + baselines +
G1 audit + G3–G9 empty templates). No primary scorer, no candidate freeze, no wet-lab GO.
