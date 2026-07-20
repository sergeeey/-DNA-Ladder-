# Workflow stub — C-A1 exp_te_loop_assay_discordance_chia_vs_hic

Minimal stage list for desk reproducibility. Large binaries stay in `data/input/` (gitignored).

## Stages

| Stage | Script | Output | Notes |
|-------|--------|--------|-------|
| **T0** | `scripts/t0_probe_encode_accessions.py` | `data/t0_accession_probe.json` | metadata only |
| **T1** | `scripts/t1_download_primary_inputs.py` | bedpe / rmsk / checksums | real ENCODE/UCSC |
| **T1b** | `scripts/t1_annotate_anchors_te_skeleton.py` | `results/t1_annotation_skeleton.json` | no primary OR |
| **T2** | `scripts/t2_positive_control_ctcf_gate.py` | `results/positive_control_ctcf_gate.*` | gate ≥2.0 |
| **T3** | `scripts/t3_primary_alusz_or.py` | `results/primary_result_OR_CI.*` | K562 AluSz |
| **T4** | `scripts/t4_mappability_sensitivity.py` | `results/sensitivity_mappability.*` | umap proxy |
| **T5** | `scripts/t5_replication_celltype.py --celltype GM12878` | `results/replication_gm12878_*` | mid-zone |
| **T5b** | `scripts/t5_replication_celltype.py --celltype HCT116` | `results/replication_hct116_*` | mid-zone |
| **T6** | `scripts/t6_caller_swap_k562.py` | `results/caller_swap_k562.*` | DELTA vs HiCCUPS |

## Freezes

- K562: `ACCESSION_FREEZE_v1.md`
- GM12878: `ACCESSION_FREEZE_replication_v1.md`
- HCT116: `ACCESSION_FREEZE_replication_HCT116_v1.md`

## Tests

```bash
python3 -m pytest tests/ -q
```

## Terminal status

`INCONCLUSIVE_CROSS_CELL` — see `decision.md` and
`null_results/20260720-te-chia-vs-hic-alusz-anchor-discordance.md`.

## Forbidden

Holdout unblind · C1 E/P · wet GO · fake data · causal TE→loop claims.
