# Tasktracker — se_llps

## Done

- [x] Closed SE / LLPS / VUS / Gnocchi / R-loop / G4 directions (see `null_results/INDEX.md`)
- [x] **C-B1** Standard-tier prereg `experiments/exp_topology_community_crispr_eg/` (Predictive topology community ΔAUC over SE for CRISPR E–G K562)
- [x] C-B1 adversarial gate: `ENCODE_R2G_FEATURE_AUDIT_v1.md` → **SURVIVES_WITH_REDESIGN**
- [x] C-B1 T0 probe + **ACCESSION_FREEZE_v1** (CRISPR ensemble SHA pinned; Hi-C `ENCFF693XIL`; cCRE v3 SCREEN + `ENCFF210CAN`) — status `PENDING_KILL_TEST`

## Next (ordered)

- [ ] C-B1: freeze community feature columns + chromosome folds → run holdout ΔAUC kill-test (REJECT if ΔAUC < 0.02)
- [ ] If REJECT/INCONCLUSIVE: file `null_results/` with “what this does NOT mean”
- [ ] Do **not** reopen closed SE enrichment claims; do **not** start TE AluY+AG under this folder

## Blocked / out of scope

- Causal SE/topology language
- Using ENCODE-rE2G scores as primary features (leakage)
- Wet-lab / holdout unblind / C1 E/P edits
