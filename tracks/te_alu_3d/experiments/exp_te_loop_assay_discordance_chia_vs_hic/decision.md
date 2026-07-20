# Decision — exp_te_loop_assay_discordance_chia_vs_hic (C-A1)

**Date:** 2026-07-20  
**Status:** `INCONCLUSIVE_CROSS_CELL` (desk **CLOSED**)  
**null_results:** `null_results/20260720-te-chia-vs-hic-alusz-anchor-discordance.md` (**INCONCLUSIVE**)

## Verdict

**Terminal desk status: `INCONCLUSIVE_CROSS_CELL`.**

Frozen primary claim (K562 AluSz OR ≥ 1.3 with replication support) **FAILED**.  
Full biological **REJECT** of “assay blind-spot TE enrichment” is **not** clean across cells
(GM12878 / HCT116 land in 1.15–1.3 mid-zone, not < 1.15 / opposite).  
Caller-swap (HiCCUPS → DELTA) **does not** reverse K562 FAIL → still file **INCONCLUSIVE**,
not REJECT.

| Arm | AluSz Fisher OR | Woolf 95% CI | Gate |
|-----|-----------------|--------------|------|
| K562 desk (T3, HiCCUPS `ENCFF693XIL`) | **0.908** | 0.851–0.967 | `FAIL_DESK_PRIMARY` |
| K562 umap ≥ 0.3 (T4) | **0.898** | 0.842–0.957 | strengthens FAIL |
| K562 DELTA caller-swap (T6, `ENCFF657QKE`) | **0.913** | 0.846–0.985 | FAIL robust |
| K562 intact localizer sens. (`ENCFF256ZMD`) | **1.107** | 1.055–1.161 | mid / assay-swap only |
| GM12878 replication (T5) | **1.252** | 1.172–1.339 | mid-zone |
| HCT116 replication (T5b) | **1.280** | 1.162–1.410 | mid-zone |
| HCT116 umap ≥ 0.3 | **1.281** | — | still mid-zone |

**Claim thresholds (honest):**

- **Support** needs primary OR ≥ 1.3 **and** replication ≥ 1.15 same direction → **FAIL**
  (K562 primary OR < 1.1; replications < 1.3).
- **Falsify / REJECT** needs OR < 1.1 after mappability **and** replication OR < 1.15 or
  opposite → arm (a) met; arm (b) **not** (GM12878 1.252; HCT116 1.280).

## What WAS tested

1. Descriptive AluSz OR for Pol II ChIA-PET vs Hi-C loop anchors (1 kb midpoint windows),
   K562 primary + GM12878 + HCT116 replication.
2. CTCF positive-control gates (all tested cells **PASS**).
3. Umap ≥ 0.3 MAPQ-proxy kill-test (K562; optional HCT116).
4. Hi-C caller-swap: HiCCUPS vs DELTA on same K562 experiment; Mustache unavailable on ENCODE.
5. Chromosome block-bootstrap CI on K562 primary (existing T3).

## What FAILED

- K562 primary enrichment claim (OR ≥ 1.3): **FAIL** (OR ≈ 0.91; umap and DELTA strengthen).
- Cross-cell sign consistency: K562 depletion vs mild elevation in GM12878/HCT116.

## What is NOT rejected globally

- Mild mid-zone AluSz elevation in lymphoblastoid (GM12878) and colon (HCT116) lines is
  **not** falsified to OR < 1.15; do not claim global absence of assay-discordance TE signal.

## Forbidden overclaim language

- Do **not** say TE “drives,” creates, or disrupts loops.
- Do **not** claim wet-lab readiness, holdout unblind, or C1 E/P edits.
- Do **not** rebrand mid-zone OR as SUPPORT or switch primary TE post-hoc.
- Do **not** treat intact-localizer OR ≈ 1.11 as rescue of K562 HiCCUPS primary.

## Gate checklist (closed)

| Gate | Status |
|------|--------|
| T0–T2 accession + CTCF K562 | DONE / PASS |
| T3 primary AluSz | `FAIL_DESK_PRIMARY` |
| T4 umap | strengthens FAIL |
| T5 / T5b replication | mid-zone both cells |
| T6 caller-swap DELTA | FAIL robust |
| Figures | `results/figures/` |
| null_results | **FILED INCONCLUSIVE** |
| Holdout / wet / C1 | SEALED / FORBIDDEN |

## What this does NOT mean

1. Not causal TE → loop proof  
2. Not C1 validation  
3. Not holdout license  
4. Not SE/HBB claim revival  
5. Not claim-level REJECT of all TE–discordance association across cell types  
6. Not enrichment SUPPORT at MCID  
7. Not authorization to promote exploratory AluJo / SVA_F  
8. Not proof that GM12878/HCT116 mild elevation is biological

## Arts

- `results/caller_swap_k562.json|.md`
- `results/figures/or_forest_cross_cell.{svg,png}`
- `results/figures/umap_sensitivity_k562.{svg,png}`
- `results/optional_robustness_notes.md`
- `workflow/README.md`, `draft_abstract.md`, `NEXT_FRUIT_NOTE.md`
- `null_results/20260720-te-chia-vs-hic-alusz-anchor-discordance.md`
