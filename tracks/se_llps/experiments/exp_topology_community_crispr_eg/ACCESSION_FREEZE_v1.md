# ACCESSION_FREEZE_v1 — C-B1 topology community vs SE (CRISPR E–G, K562)

**Date:** 2026-07-20  
**Probe:** `data/t0_accession_probe.json` (`t0_status`: **PASS_FREEZE**)  
**Rule:** No primary ΔAUC until this freeze + `ENCODE_R2G_FEATURE_AUDIT_v1.md` are committed.

## Frozen primary inputs

| Role | Accession / URL | Assembly | Notes |
|------|-----------------|----------|-------|
| CRISPR E–G labels (primary) | EngreitzLab `EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz` | GRCh38 | Public GitHub raw; **SHA-256 `d0806eb8a3cfe71066a9a1c88da2f730ccf5d86364bd52ca9bc6ba628744e417`**; n≈10412 K562 pairs; includes `FlowFISH_K562` (+ Gasperini2019, TAPseq) |
| Hi-C loops K562 | **`ENCFF693XIL`** (`ENCSR545YBD`) | GRCh38 | bedpe loops; preferred_default; HiCCUPS merged_loops_30 — same primary Hi-C as C-A1 |
| cCRE nodes (v3 preferred) | SCREEN `https://downloads.wenglab.org/Registry-V3/GRCh38-cCREs.bed` | GRCh38 | HTTP 200; Content-Length **63732631**; Last-Modified Fri, 07 Oct 2022 |
| cCRE K562 portal v3 (supporting) | **`ENCFF210CAN`** (`ENCSR940SYU`, encyclopedia ENCODE v3) | GRCh38 | bed candidate cCREs |
| SE membership baseline | `tracks/se_llps/data/input/k562_super_enhancers_grch38.json` | GRCh38 | Already on disk in track |

## Documented fallbacks (not primary unless v3 blocked at download time)

| Role | Accession | Notes |
|------|-----------|-------|
| cCRE v4 agnostic | `ENCFF420VPZ` (`ENCSR800VNX`, ENCODE v4) | Use only if Registry-V3 fetch fails; record swap in decision.md |
| cCRE v4 K562 | `ENCFF455VKH` (`ENCSR935IVQ`) | Cell-type v4 |
| Hi-C alternate loops | `ENCFF657QKE` (DELTA) | Sensitivity only — not primary community graph |

## Supporting ENCODE Flow-FISH (not the label freeze)

- **239** released Flow-FISH CRISPR screen experiments in K562 (portal search at T0).
- **53** element-quantification files sampled under Flow-FISH assay title.
- Harmonized positives/negatives for the kill-test remain the **ensemble benchmark** above
  (matches ENCODE-rE2G training/eval discipline). Per-locus ENCFF TSVs are auxiliary.

## Reference-only (do not use as primary features)

| Product | Accession | Role |
|---------|-----------|------|
| ENCODE-rE2G K562 predictions | `ENCSR512SWG` | Optional EXPLORATORY ceiling |
| ENCODE-rE2G Extended K562 | `ENCSR621BIJ` | Documents Extended loop features exist on portal |

## Explicitly not frozen / out of scope

- Multi-GB genome-wide rE2G prediction beds (not required for SE vs topology ΔAUC)
- TE annotations / C-A1 discordant sets
- Holdout panel / C1 E–P locks
- AlphaGenome allele priors (registry C-B1-TE)

## Download policy

Large binaries stay gitignored under `data/input/` when fetched in a later session. This freeze
pins **accessions/URLs/checksums only**.
