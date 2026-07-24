# Stage-3 Architecture Independent-Source Replication — G4c Decision v1

**Claim:** `G4c_stage3_architecture_replic_CLAIM_v1.md`
**Freeze:** `stage3_architecture_anchor_freeze_v1.json` (frozen 2026-07-21T11:58:09.194626+00:00)
**Eligibility freeze:** `G4c_stage3_architecture_replic_eligibility_v1.json`
**Preflight:** `G4c_stage3_architecture_replic_preflight_v1.json`
  (status: OK; run_at: 2026-07-21T12:51:47.721732+00:00)
**Analysis run:** 2026-07-21T14:28:18.435217+00:00
**Samples:** GSE201820 noIAAdiff (differentiated) + noIAAundiff (undifferentiated)
  CTCF-AID HUDEP-2, noIAA (active CTCF), clones C16+C3 merged, hg19, KR norm
**Primary bg_tol_bins:** 0 (exact-distance background)
**Panel verdict:** `REPLICATION_INCONCLUSIVE`

---

## No-upgrade invariant

G4c verdict `REPLICATION_INCONCLUSIVE` does **NOT** change the G4a panel verdict (INCONCLUSIVE).
Stage-3 slot assignments remain LOCKED (registry, 2026-07-15).

---

## Panel summary

| Slot | Candidate | Variant | Cross-sample verdict |
|------|-----------|---------|---------------------|
| ARCH_01 | A754 | chr11:75445532:G:A | REPLICATION_UNSUPPORTED |
| ARCH_02 | A518 | chr11:518575:C:A | REPLICATION_INCONCLUSIVE |

---

## Slot details

### ARCH_01 — A754 (chr11:75445532:G:A)

**Slot cross-sample verdict:** `REPLICATION_UNSUPPORTED`

**Nearest protein-coding TSS (pre-registered):** ENSG00000149243 (KLHL35), distance 12329 bp, strand -1

#### noIAAdiff (differentiated)

**Slot-sample outcome:** `UNSUPPORTED`

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| score (tol=0, primary) | `FAIL` |
| primary_obs | 23.641285 |
| primary_oe | 1.2661301 |
| bg_n (tol=0) | 99 |
| enrich_mean | 1.077492741397466 |
| obs_percentile | 0.6464646464646465 |
| focal_row_nonzero | 92 |
| 25 kb | — | — |
| score (tol=0, primary) | `FAIL` |
| primary_obs | 81.49981 |
| primary_oe | 1.3401595 |
| bg_n (tol=0) | 39 |
| enrich_mean | 1.0435628152422116 |
| obs_percentile | 0.6666666666666666 |
| focal_row_nonzero | 41 |

Informational (tol=1, excluded from verdict):

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| primary_obs | 23.641285 |
| bg_n (tol=1, info) | 299 |
| enrich_mean | 0.5470617106235112 |
| obs_percentile | 0.5451505016722408 |
| 25 kb | — | — |
| primary_obs | 81.49981 |
| bg_n (tol=1, info) | 119 |
| enrich_mean | 0.6114437900808135 |
| obs_percentile | 0.5462184873949579 |

#### noIAAundiff (undifferentiated)

**Slot-sample outcome:** `UNSUPPORTED`

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| score (tol=0, primary) | `FAIL` |
| primary_obs | 29.99468 |
| primary_oe | 1.3019589 |
| bg_n (tol=0) | 99 |
| enrich_mean | 1.0749206426778006 |
| obs_percentile | 0.6666666666666666 |
| focal_row_nonzero | 96 |
| 25 kb | — | — |
| score (tol=0, primary) | `FAIL` |
| primary_obs | 91.49811 |
| primary_oe | 1.1510831 |
| bg_n (tol=0) | 39 |
| enrich_mean | 0.8849978882487457 |
| obs_percentile | 0.15384615384615385 |
| focal_row_nonzero | 41 |

Informational (tol=1, excluded from verdict):

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| primary_obs | 29.99468 |
| bg_n (tol=1, info) | 299 |
| enrich_mean | 0.6505913215685365 |
| obs_percentile | 0.5518394648829431 |
| 25 kb | — | — |
| primary_obs | 91.49811 |
| bg_n (tol=1, info) | 119 |
| enrich_mean | 0.6110046993083692 |
| obs_percentile | 0.3697478991596639 |

### ARCH_02 — A518 (chr11:518575:C:A)

**Slot cross-sample verdict:** `REPLICATION_INCONCLUSIVE`

**Nearest protein-coding TSS (pre-registered):** ENSG00000023191 (RNH1), distance 11180 bp, strand -1

#### noIAAdiff (differentiated)

**Slot-sample outcome:** `INCONCLUSIVE`

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| score (tol=0, primary) | `FAIL` |
| primary_obs | 27.850475 |
| primary_oe | 1.491557 |
| bg_n (tol=0) | 82 |
| enrich_mean | 0.8253553300005966 |
| obs_percentile | 0.2073170731707317 |
| focal_row_nonzero | 80 |
| 25 kb | — | — |
| error | `same_bin_guard_violation` |
| message | HARD-FAIL: E_mid_bin == P_mid_bin == 500000 at binsize=25000. bg_tol_bins=0 diagonal background is undefined; computation blocked. |

Informational (tol=1, excluded from verdict):

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| primary_obs | 27.850475 |
| bg_n (tol=1, info) | 249 |
| enrich_mean | 0.4568378501133054 |
| obs_percentile | 0.3895582329317269 |
| 25 kb | — | — |
| primary_obs | 350.98355 |
| bg_n (tol=1, info) | 67 |
| enrich_mean | 1.3250326850149796 |
| obs_percentile | 0.6865671641791045 |
| audit | diagonal; metrics informational only |

#### noIAAundiff (undifferentiated)

**Slot-sample outcome:** `INCONCLUSIVE`

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| score (tol=0, primary) | `FAIL` |
| primary_obs | 35.743225 |
| primary_oe | 1.5514822 |
| bg_n (tol=0) | 82 |
| enrich_mean | 0.8651264659829944 |
| obs_percentile | 0.3048780487804878 |
| focal_row_nonzero | 74 |
| 25 kb | — | — |
| error | `same_bin_guard_violation` |
| message | HARD-FAIL: E_mid_bin == P_mid_bin == 500000 at binsize=25000. bg_tol_bins=0 diagonal background is undefined; computation blocked. |

Informational (tol=1, excluded from verdict):

| res | metric | value |
|-----|--------|-------|
| 10 kb | — | — |
| primary_obs | 35.743225 |
| bg_n (tol=1, info) | 248 |
| enrich_mean | 0.5736968410605634 |
| obs_percentile | 0.41935483870967744 |
| 25 kb | — | — |
| primary_obs | 366.13052 |
| bg_n (tol=1, info) | 66 |
| enrich_mean | 1.379733066732775 |
| obs_percentile | 0.7272727272727273 |
| audit | diagonal; metrics informational only |


---

## Dump file hashes

| File | SHA256 (first 16 chars) |
|------|------------------------|
| ARCH_01_A754_noIAAdiff_obs_KR_10kb.txt | e90969766adb8dd3… |
| ARCH_01_A754_noIAAdiff_obs_KR_25kb.txt | 6e90d41f765fb394… |
| ARCH_01_A754_noIAAdiff_oe_KR_10kb.txt | 48711845f31ebf41… |
| ARCH_01_A754_noIAAdiff_oe_KR_25kb.txt | 53041aed941299c2… |
| ARCH_01_A754_noIAAundiff_obs_KR_10kb.txt | e82b8bdec6e65264… |
| ARCH_01_A754_noIAAundiff_obs_KR_25kb.txt | 88dfc67c088e032e… |
| ARCH_01_A754_noIAAundiff_oe_KR_10kb.txt | d952cc3cbebe83e8… |
| ARCH_01_A754_noIAAundiff_oe_KR_25kb.txt | 83511bf255723f86… |
| ARCH_02_A518_noIAAdiff_obs_KR_10kb.txt | edf7ae2a6130e841… |
| ARCH_02_A518_noIAAdiff_obs_KR_25kb.txt | 3220419dcc38c661… |
| ARCH_02_A518_noIAAdiff_oe_KR_10kb.txt | 7bcc7aa92e4c2192… |
| ARCH_02_A518_noIAAdiff_oe_KR_25kb.txt | 67b316bdd1fb1dd3… |
| ARCH_02_A518_noIAAundiff_obs_KR_10kb.txt | e7ae7072743deb1b… |
| ARCH_02_A518_noIAAundiff_obs_KR_25kb.txt | 5927eb073b75c39a… |
| ARCH_02_A518_noIAAundiff_oe_KR_10kb.txt | 0c6417674ec66dad… |
| ARCH_02_A518_noIAAundiff_oe_KR_25kb.txt | 923f90b82b3bb188… |

---

## Interpretation constraints (pre-registered)

- This analysis tests Contact(anchor_ctcf, anchor_tss) in CTCF-AID HUDEP-2 noIAA cells.
- **NOT CLAIMED:** enhancer–promoter contact, target-gene identity, allele effect,
  expression change, regulation, or pathogenicity.
- G4b allele ΔContact: **NOT TESTED**.
- Wet-lab: **NO-GO** (B0 UNSIGNED as of 2026-07-21; user confirmed desk-only).
- tol=1 informational output is labelled as such and **excluded from the verdict**.
- Outcome does not change Stage-3 slot assignments.

## Caveats

- Background-direction wording in the locked G4a/G4c claims is corrected by
  `G4_stage3_background_direction_ERRATUM_v1.md`; tol=1 inflated, rather than
  compressed, A754 enrichment in the parent matrix.
- bg_tol_bins=0 (exact-distance only): bg_n may be lower than tol=1 baseline.
  If bg_n < 20, score is INSUFFICIENT_BG regardless of signal.
- A518 at 25 kb (ARCH_02): E and P map to the same 25 kb bin (UNRESOLVED_SAME_BIN);
  this is expected from the frozen anchor geometry, same as in G4a.
- Remote .hic access via juicer_tools: dump performance depends on NCBI FTP bandwidth.
- CTCF-AID noIAA ≠ WT Hi-C: chromatin state may differ from GSM4873113.
  A replicated contact in both is stronger independent evidence; a difference is
  informative about condition-dependence, not about anchor correctness.
- KR normalisation; VC not repeated for G4c.
- hg19 coordinates from frozen G4a anchors (Ensembl REST, release 116).
