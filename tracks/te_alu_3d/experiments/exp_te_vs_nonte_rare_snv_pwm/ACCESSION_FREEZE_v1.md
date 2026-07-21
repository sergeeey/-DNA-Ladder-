# ACCESSION_FREEZE_v1 — C-E1 TE vs non-TE rare-SNV PWM

| Role | Source | Accession / path |
|------|--------|------------------|
| Rare SNVs | gnomAD GraphQL r4 | region queries GRCh38 chr11 CTCF neighborhoods |
| TE (Alu/SVA) | UCSC rmsk | `repeatmasker_chr11_alu_sva.bed` (pilot_scaffold) |
| CTCF peaks (geography) | ChIP-Atlas HUDEP-2 | `ctcf_HUDEP2_peaks.bed` (SRX5821035) |
| Mappability | Hoffman lab | `k100.Umap.MultiTrackMappability.bw` |
| Scorer | pilot_scaffold | `ctcf_pwm_delta_v1.1` |
| Sequence | UCSC API | hg38 `getData/sequence` tiles |

**Excluded:** HBB chr11:5.2–5.3 Mb; HO_A/B/C geography chr11:64–68 Mb (SEALED).  
Frozen 2026-07-21 with claim T0; analysis after fetch.
