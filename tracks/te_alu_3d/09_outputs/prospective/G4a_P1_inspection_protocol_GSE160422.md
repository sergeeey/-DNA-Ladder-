# G4a / P1 inspection protocol — GSE160422 (post-download)

**Prereq:** `C1_claim_freeze_pack_v1.md` locks E/P; do not rechoose after viewing map.

## A. After GSM4873113 completes

1. Verify size ~6.6–6.8 GB and write SHA-256 into `GSE160422_download_manifest.md` + local `checksums_sha256.csv`.
2. Open in Juicebox (local `.hic`).
3. Navigate using **hg19** coords from `c1_ep_liftover_hg19.yaml`:
   - C1: `chr11:62521395`
   - E: `chr11:62157472-62162472`
   - P: `chr11:62457472-62462472`
4. Ask only G4a questions:

```text
coverage present at locked window?
Contact_WT(E,P) > local background?
signal robust across nearby bins (not one pixel)?
normalization/resolution usable for this distance (~0.3 Mb E–P)?
```

5. Record PASS / FAIL / INCONCLUSIVE in this file’s Result section (append).  
   **PASS still does not open G4b** (allele effect needs edit + Capture-C/MCC).

## B. P1 after WT inspection

Download GSM4873114 (del) and GSM4873115 (inv) only when disk allows (~13 GB more).

For **β-globin P1-system** prefer Capture Hi-C GSM4873116–3118 + paper occupancy.

P1 PASS checklist:

```text
P1 edit verified (3′HS1 del/inv)
AND CTCF occupancy changes (CUT&RUN in series)
AND contact changes in predicted direction (WT vs edit)
AND assay detects effect reproducibly
```

## C. Branch gate

| Outcome | Action |
|---------|--------|
| G4a FAIL | architecture freeze remains NO-GO → Branch B activity |
| G4a PASS, P1 weak | design / plan planted local P1 near C1 |
| G4a PASS + P1 PASS | may draft Branch A claim language (still no wet GO until G5/edit/assay) |

## Result (fill later)

```yaml
g4a_gsm4873113:
  status: PASS_DESK
  file_bytes: 7112676977
  sha256: A76017922096842BE6463FEB1D349BE5689EF96267BA51DD14777E94F2585226
  juicebox_window_hg19: "chr11:62157472-62521395 span E–C1–P"
  contact_above_background: true
  notes: >
    juicer_tools dump KR observed/OE; enrichment ~3.4× (10kb) and ~2.5× (25kb)
    vs same-distance local background; OE 3.20 / 2.14; obs percentile ≥0.98.
    Single .hic — no second WT replicate in this pass.
    See G4a_gsm4873113_desk_pass_v1.md
p1_system_3primeHS1:
  status: DOWNLOAD_QUEUED
  del_vs_wt_contact_change: null
  inv_vs_wt_contact_change: null
```
