# Matched Control Specification (v0.2 — redesign v2)

**Freeze ref:** `pilot_redesign_v2.md`  
**Supersedes:** draft v0.1 single-estimand matching

## Goal

For each TE-overlapping test variant, build control sets that answer **named estimands**, not a single mixed question.

## Control hierarchy

| Level | Pool | Question | Role (current N) |
|-------|------|----------|------------------|
| **A** | Matched non-TE | TE vs rest of genome? | Primary (when powered) |
| **B** | Same TE family, non-candidate | Site vs ordinary Alu/SVA? | Diagnostic |
| **C** | Same subfamily + approx. age | Beyond lineage/composition? | Diagnostic |
| **D** | Same locus / TAD | Local chromatin? | Diagnostic |

`k=20` per test variant per level when pool allows; else log `undermatched` and do not promote to confirmatory inference.

## Estimand-specific matching

### Estimand T — Total TE effect

Match (C_technical):

| Variable | Binning |
|----------|---------|
| `gc_content` | ±2% |
| `mappability` | Same decile |
| `chromosome` | Same chr |
| `variant_type` / length | Exact class |
| `distance_to_gene_tss` | Optional log bins |

**Do not match** `distance_to_nearest_ctcf`.

### Estimand C — CTCF-conditional

All of Estimand T **plus**:

| Variable | Binning |
|----------|---------|
| `distance_to_nearest_ctcf` | Log-scale bins |
| `chromhmm_state` | Preferred exact state |

## Algorithm

```text
1. Build pools:
   A: gnomAD/ClinVar QC-pass, NOT in Alu/SVA
   B: QC-pass inside same TE family, not in test set
   C: subset of B with same subfamily (+ age proxy if available)
   D: subset of A or B in same TAD/locus window (cell-type matched)
2. For each estimand ∈ {T, C}:
     for variant v in test_set:
       candidates = pool_A ∩ match(estimand_vars)
       if |candidates| < 20: relax per logged tier
       sample 20; store match_tier
3. Emit diagnostic manifests for B–D (may be sparse)
4. Balance table: SMD < 0.1 on matched vars for that estimand
```

## Permutation null (primary)

```text
shuffle labels within matched set
OR within strata:
  TE class × subfamily × map_bin × GC_bin
  × CTCF_bin          # Estimand C only
  × locus/TAD block   # if Control D used
n_perm = 10,000
```

Global chromosome-wide shuffle = **software negative control only**.

## Outputs

- `control_manifest_T.csv` / `control_manifest_C.csv`
- `control_manifest_B.csv` … (diagnostic)
- `balance_table_{T,C}.csv`
- `undermatched_log.json`

## Open Decisions (must close before confirmatory)

- [ ] Subfamily / age proxy source
- [ ] TAD caller + cell-type Hi-C for Control D
- [ ] Whether TSS matching stays in C_technical or moves to sensitivity
- [ ] Minimum n to promote B–D to inferential
