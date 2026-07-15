# Queue C — paused / blocked until credentials

**Date:** 2026-07-14  
**Router pin:** R3 desk-only while primary UNAVAILABLE  

## DONE in this session

| Queue | Result |
|-------|--------|
| A admission attempt | FAIL — no ARCHCODE / AlphaGenome |
| B proxy Hi-C L-HO_* | PROXY_PARTIAL — K562 loops/domains on disk |
| Prior desk G4 / unblind draft | already present |

## PAUSED (do not start until A → AVAILABLE)

```text
- holdout scoring / unblind execution
- allele shortlist freeze (≤3) + G3–G9 fill
- Arm A/B ensemble on real allele scores
- wet-lab GO / edit design execution
- PWM promotion to confirmatory
- HBB enrichment re-run
- 3D disruption claims
```

## Resume checklist (human)

```text
[ ] Set ALPHAGENOME_API_KEY or place ARCHCODE binary + hashes
[ ] python adapters/alphagenome_adapter.py --smoke   # expect PASS
[ ] python second_scorer_admission_gate.py --type ... # expect AVAILABLE
[ ] Then resume R4: ranking on non-holdout OR unblind protocol GO
```

Until then: **STOP spending cycles on confirmatory or lab paths.**  
Optional only: replace K562 proxy with HUDEP-2 genome-wide map *if* one is published.
