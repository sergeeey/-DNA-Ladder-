# Branch A panel — provisional freeze v1 (NO wet-lab GO)

**Date:** 2026-07-15  
**Status:** `PROVISIONAL_PANEL_FROZEN`  
**Not:** G9 · not transfection · not library order  

## Gate stack

| Gate | Status |
|------|--------|
| Claim/E/P lock | LOCKED |
| G4a | PASS_DESK |
| P1-system | PASS_DESK |
| G4b protocol | PROTOCOL_DESK_FROZEN |
| G5 PE path | DESK shortlist exists; order FORBIDDEN |
| Wet-lab GO | **NO-GO** |

## Panel

| ID | Allele / role | Endpoint priority |
|----|---------------|-------------------|
| C1 | chr11:62753923 A>G test | G4b contact primary; activity secondary |
| C2 | same-site A>T control | activity / specificity |
| P1-system | 3′HS1 del reference (literature + local Hi-C) | assay-chain |
| P1-local | planted CTCF near P (`62673547-62673691`) or E (`62379961-62380183`) — confirm HUDEP-2 CTCF first | sensitivity |
| N3 | matched neutral KEEP | specificity |
| N_repl | replace dropped N1/N2 later | specificity |

## Primary claims allowed now

1. Sequence/activity (M3) candidate — CONDITIONAL GO for reporter planning.  
2. HUDEP-2 locked E–P contact exists (G4a desk).  
3. HUDEP-2 Hi-C detects known architectural break (P1 desk).  
4. Provisional architecture **panel design** for future G4b.

## Forbidden until G4b PASS

> C1 disrupts the enhancer–promoter loop in HUDEP-2.

## Exit to wet-lab (checklist)

```text
[ ] PE candidate externally validated + off-target desk
[ ] P1-local design confirmed in HUDEP-2 CTCF
[ ] Capture-C bait oligo set quoted (no order until GO)
[ ] MCID accepted or amended in writing
[ ] Explicit wet-lab GO note signed
```

Until then: **NO_GO_FOR_WET_LAB**.
