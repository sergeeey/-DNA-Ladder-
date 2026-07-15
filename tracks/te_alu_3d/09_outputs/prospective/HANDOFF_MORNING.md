# Pre-morning handoff for returning human

**Autonomous job:** `overnight_orchestrator.ps1` (terminal background)  
**Live log:** `09_outputs/prospective/overnight_orchestrator_log.txt`  
**Final summary (when job finishes):** `09_outputs/prospective/MORNING_STATUS_2026-07-15.md`

## Read first (≤5 min)

1. This file  
2. `MORNING_STATUS_2026-07-15.md` (appears after downloads finish)  
3. `G4a_gsm4873113_desk_pass_v1.md` — already PASS_DESK  
4. `P1_3primeHS1_desk_pass_v1.md` — verdict after Capture/edit Hi-C land  

## Fixed scientific state overnight

```text
C1 language: activity candidate; architecture unconfirmed for allele effect
G4a: PASS_DESK
G4b: draft only
Architecture freeze: NO-GO until P1 desk
Wet-lab: NO-GO
Holdout: SEALED
```

## If orchestrator still running when you return

Check sizes:

```powershell
Get-ChildItem "D:\DNK - 2\data\HUDEP2_GSE160422\*.hic" |
  Select-Object Name, @{N='GB';E={[math]::Round($_.Length/1GB,2)}}
Get-Content "D:\DNK - 2\DNA_TE_3DGenome_Context\09_outputs\prospective\overnight_orchestrator_log.txt" -Tail 40
```

Resume is safe (`curl -C -`). Re-run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\DNK - 2\DNA_TE_3DGenome_Context\pilot_scaffold\scripts\overnight_orchestrator.ps1"
```

## Suggested morning decision tree

```text
P1 PASS_DESK
  → review G4b draft + bait windows
  → still NO wet GO (need PE + MCID)
P1 lean / inconclusive
  → keep Branch B; optional Capture depth check
P1 FAIL local but paper strong
  → P1_LITERATURE_GROUNDED; insist on planted local P1
```
