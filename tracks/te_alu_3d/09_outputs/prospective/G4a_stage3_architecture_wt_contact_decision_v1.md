# Stage-3 Architecture WT Contact — Decision v1

**Claim:** `G4a_stage3_architecture_wt_contact_CLAIM_v1.md`  
**Freeze:** `stage3_architecture_anchor_freeze_v1.json` (frozen 2026-07-21T11:58:09.194626+00:00)  
**Analysis run:** 2026-07-21T11:58:16.170750+00:00  
**Sample:** GSE160422 GSM4873113 (WT HUDEP-2 genome-wide Hi-C), KR norm  
**Panel verdict:** `INCONCLUSIVE`

---

## Panel summary

| Slot | Candidate | Variant | Outcome |
|------|-----------|---------|---------|
| ARCH_01 | A754 | chr11:75445532:G:A | PARTIAL |
| ARCH_02 | A518 | chr11:518575:C:A | INCONCLUSIVE |


---

## Slot details

### ARCH_01 — A754 (chr11:75445532:G:A)

**Slot outcome:** `PARTIAL`  
**Score 10 kb:** `PASS`  
**Score 25 kb:** `FAIL`  

**Nearest protein-coding TSS (pre-registered):** ENSG00000149243 (KLHL35), distance 12329 bp, strand -1

#### Metrics 10 kb

| metric | value |
|--------|-------|
| primary_obs | 73.85924 |
| primary_oe | 1.6989803 |
| bg_n | 299 |
| enrich_mean | 1.6666560872629799 |
| obs_percentile | 0.9632107023411371 |
| focal_row_nonzero | 90 |

#### Metrics 25 kb

| metric | value |
|--------|-------|
| primary_obs | 191.03401 |
| primary_oe | 1.5165274 |
| bg_n | 119 |
| enrich_mean | 1.2239670184291687 |
| obs_percentile | 0.6638655462184874 |
| focal_row_nonzero | 41 |

### ARCH_02 — A518 (chr11:518575:C:A)

**Slot outcome:** `INCONCLUSIVE`  
**Score 10 kb:** `FAIL`  
**Score 25 kb:** `UNRESOLVED_SAME_BIN`  

**Nearest protein-coding TSS (pre-registered):** ENSG00000023191 (RNH1), distance 11180 bp, strand -1

#### Metrics 10 kb

| metric | value |
|--------|-------|
| primary_obs | 88.683716 |
| primary_oe | 2.039987 |
| bg_n | 248 |
| enrich_mean | 1.390233416646591 |
| obs_percentile | 0.8911290322580645 |
| focal_row_nonzero | 78 |

#### Metrics 25 kb

| metric | value |
|--------|-------|
| primary_obs | 325.06668 |
| primary_oe | 1.7750962 |
| bg_n | 66 |
| enrich_mean | 1.1371694217595338 |
| obs_percentile | 0.7272727272727273 |
| focal_row_nonzero | 34 |
| audit_note | diagonal target_dist=0; metrics not interpretable as between-anchor enrichment |


---

## Interpretation constraints (pre-registered)

- This analysis tests Contact(anchor_ctcf, anchor_tss) in WT HUDEP-2 at pre-registered anchors.
- **NOT CLAIMED:** enhancer–promoter contact, target-gene identity, allele effect, expression
  change, regulation, or pathogenicity.
- G4b allele ΔContact: **NOT TESTED** (desk-only).
- Wet-lab: **NO-GO** (B0 UNSIGNED as of 2026-07-21; user confirmed desk-only).
- Outcome does not change Stage-3 slot assignments (see registry, locked 2026-07-15).

## Caveats

- Post-analysis correction: a same-bin E/P pair is `UNRESOLVED_SAME_BIN`,
  not FAIL (`CLAIM v1`, integrity amendment §8).
- Without that correction, A518 would have been labelled UNSUPPORTED; the
  panel verdict would still have remained INCONCLUSIVE.
- A518 25 kb metrics use `target_dist=0` diagonal background and are shown
  only for audit; they are not interpretable as between-anchor enrichment.
- `bg_tol_bins=1` mixes 0/1/2-bin distances when anchors are one bin apart.
  This inherited near-diagonal background is conservative but heterogeneous.
- Single WT replicate (.hic file); no independent replicate Hi-C available for this
  specific combination of sample + method + reference.
- KR normalization; VC sensitivity not repeated for Stage-3 (robustness established
  at G4a Stage-2 for the same .hic file, see `G4a_multisample_kill_test_v1.md`).
- hg19 coordinates derived from GRCh38 via Ensembl REST; small rounding differences
  at bin boundaries are possible.
- Architecture candidates; contact evidence alone does not confirm causal role.
