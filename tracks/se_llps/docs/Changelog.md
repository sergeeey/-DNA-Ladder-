# Changelog — se_llps

## 2026-07-21 — C-H1 robustness → SUPPORT_WITH_CAVEATS

- Sensitivity battery: `scripts/run_c_h1_sensitivity.py` → `results/sensitivity_result.json`
- Core (alt seed / no-TSS / GC-q5 / blacklist / odd-even / LOCO-min \|\Δ\|=0.202) all ≥0.15
- TE class split: SINE 0.251 / LTR 0.358 SUPPORT; **LINE 0.025** kill → **SUPPORT_WITH_CAVEATS**
- Second Gnocchi build UNAVAILABLE (404); no wet/pathogenicity language
- Primary SUPPORT \|\Δ\|=0.211 unchanged

## 2026-07-20 — C-H1 TE-derived pELS Gnocchi → SUPPORT

- True **C-H1** (NOT Micro-C): `experiments/exp_te_derived_pels_gnocchi/`
- Claim: |\Delta mean Gnocchi Z| ≥ 0.15 TE-derived vs GC/length/TSS-matched non-TE pELS; kill |\Delta|<0.05
- Data: Registry-V3 pELS + rmsk TE + hg38.2bit + GENCODE TSS + Gnocchi QC 1kb (1 984 900 rows)
- Primary |\Delta| = **0.211** (Δ=−0.211; CI [−0.239, −0.183]); Cliff's δ=−0.064; n=30 962 pairs with coverage
- **SUPPORT**; distinct from closed SE-vs-typical Gnocchi REJECT; next fruit C-I1 (Micro-C) → BLOCKED_DATA → C-L1
- Artifacts: `results/{matching_lock,primary_result}.json`; scripts + unit tests

## 2026-07-20 — C-B1 kill-test FAIL_KILL / REJECT (ΔAUC −0.0073)

- Redesigned baseline locked before fit: `log10_distance + activity_els (ENCFF210CAN pELS/dELS) + SE`
- Topology: enh/prom loop degree, shared community size, min loop-span rank from `ENCFF693XIL`
- Label: ensemble `Regulated==TRUE`; split train≠chr20–22 / test=chr20–22
- Primary: AUC 0.8806 → 0.8733; **ΔAUC −0.0073** → **FAIL_KILL** / **REJECT**
- Positive control: distance-alone AUC **0.8796** PASS; shuffle-null mean ΔAUC ≈ 0.009
- Artifacts: `results/kill_test_chr_holdout.{json,md}`; script `scripts/kill_test_chr_holdout.py` + unit tests
- Null: `null_results/20260720-topology-community-crispr-eg-delta-auc.md`

## 2026-07-20 — C-B1 opened: topology community vs SE for CRISPR E–G (prereg + T0 + rE2G audit)

- New experiment: `experiments/exp_topology_community_crispr_eg/` (Standard tier, L0 Predictive)
- Prereg: `claim.md`, `controls.md`, `notes.md`, `decision.md` (`PENDING_KILL_TEST`)
- Novelty explicit vs closed SE→LLPS/VUS/Gnocchi/R-loop/G4 and vs C-A1 INCONCLUSIVE_CROSS_CELL
- ID note: registry TE AluY+AG C-B1 parked as `C-B1-TE-AluY-AG`; this desk fills C-B1 slot with topology/CRISPR estimand per standing order
- Adversarial audit: `ENCODE_R2G_FEATURE_AUDIT_v1.md` → **SURVIVES_WITH_REDESIGN** (rE2G already has contact + Extended Hi-C loop/PET/TAD features)
- T0: `scripts/t0_probe_encode_accessions.py` → `data/t0_accession_probe.json` (**PASS_FREEZE**)
- Freeze: CRISPR ensemble SHA-256 `d0806eb8…e417`; Hi-C loops **`ENCFF693XIL`**; cCRE v3 SCREEN Registry-V3 + portal **`ENCFF210CAN`**
