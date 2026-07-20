# Changelog — se_llps

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
