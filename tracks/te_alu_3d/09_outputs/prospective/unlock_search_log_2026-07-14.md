# Unlock search log — 2026-07-14 (priority-corrected)

**Authority shift applied:** G4a WT contact + architecture P1 = critical; ARCHCODE = technical/exploratory only.

## Decision status

```text
architecture freeze:          NO-GO
C1 activity investigation:    CONDITIONAL GO
ARCHCODE comparison:          EXPLORATORY GO
G4a (WT Contact E–P):         NOT ESTABLISHED (dataset CANDIDATE)
G4b (allele ΔContact):        NOT TESTED (public Hi-C cannot open)
P1 architecture control:      CANDIDATE (3′HS1 edit series)
```

## Stream 1 — HUDEP-2 WT contact (G4a)

| Resource | Role | Build | G4a ready? |
|----------|------|-------|------------|
| **GSE160422 / GSM4873113** WT HUDEP-2 genome-wide Hi-C `.hic` | Primary G4a candidate for locked E–P / C1 locus | **hg19** | Pending download + locus inspection |
| GSE160422 Capture Hi-C GSM4873116–3118 | β-globin-targeted; **not** assumed C1 coverage | hg19 | Use for P1 locus, not C1 |
| GSE201820 HUDEP-2 Hi-C (CTCF-AID) | Alternate genome-wide | TBD | Secondary if GSE160422 insufficient |
| K562 ENCFF693XIL loops | Proxy only | GRCh38 | **Not** G4a |

**Local download path:** `D:\DNK - 2\data\HUDEP2_GSE160422\`  
**First file:** `GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic` (~6.6–6.8 GB)

### G4a PASS requires (still)

```text
HUDEP-2 AND hg19 coords from liftOver
AND locked E/P (C1_claim_freeze_pack_v1)
AND Contact > local background
AND not a single noisy pixel
AND coverage at lifted C1 window
```

### Lifted Juicebox window (DO NOT use GRCh38)

See `c1_ep_liftover_hg19.yaml`:

| ID | GRCh38 | hg19 |
|----|--------|------|
| C1 | chr11:62753923 | **chr11:62521395** |
| E  | chr11:62390000-62395000 | **chr11:62157472-62162472** |
| P  | chr11:62690000-62695000 | **chr11:62457472-62462472** |

Suggested Juicebox view (hg19): approx `chr11:62,150,000-62,550,000` spanning E–C1–P.

## Stream 2 — Architecture P1

| Resource | Role |
|----------|------|
| GSM4873113 WT vs GSM4873114 3′HS1-del (B6) vs GSM4873115 3′HS1-inv (A2) genome-wide Hi-C | **P1-system** candidate in HUDEP-2 |
| GSM4873116–3118 Capture Hi-C | High-res P1 at **β-globin**, not C1 |
| SuperSeries GSE160425 / paper eLife 70557 | Provenance |

**P1 PASS (system-level) still needs after download:**

```text
edit verified in paper AND
CTCF/cohesin occupancy change (CUT&RUN in series) AND
contact change in predicted direction AND
assay detects effect reproducibly
```

Expression desirable, not required for technical architecture P1.

**P1-local planted** near C1 CTCF remains desirable if Branch A advances — 3′HS1 is distant-locus system control.

## Stream 3 — ARCHCODE

Local checkout: `C:\Users\sboi\ARCHCODE_review`  
Commit: `55186d96b66f71105490e0f8d766e16228d29ad0`  
Import smoke: OK (`src/archcode`)  
Label: **exploratory physics-based scorer** — see `archcode_technical_admission_2026-07-14.md`  
**Not** independent replication; **not** SCIENTIFIC_VALIDATION_PASS.

## Ordering (information value)

```text
1. Claim/E/P freeze          DONE (C1_claim_freeze_pack_v1.md)
2. Parallel G4a + P1 data    IN PROGRESS (GSM4873113 downloading)
3. ARCHCODE TECHNICAL        NOTED (not blocking)
4. If G4a FAIL → stop architecture freeze
5. If G4a PASS but P1 weak → design planted local P1
6. Only then wet-lab panel
```

## Forbidden while searching

- Renaming E/P after viewing a convenient contact
- Claiming G4a from “Hi-C exists on chr11”
- Using Capture Hi-C as C1 coverage without bait check
- Pasting GRCh38 coords into hg19 `.hic`
