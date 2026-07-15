# Queue A attempt — primary admission (2026-07-14)

**Router:** R3/R4  
**Result:** `FAIL` / confirmatory primary **UNAVAILABLE**

## Environment check

```text
ARCHCODE binary:        absent (score_freeze.primary_model.binary_path=null)
ALPHAGENOME_API_KEY:    unset
GOOGLE_API_KEY:         unset
ALPHAGENOME_CHECKPOINT: unset
```

## Gate outputs

| Gate | Verdict |
|------|---------|
| `archcode_admission_gate.py` | FAIL |
| `alphagenome_adapter.py --smoke` | FAIL (`no_credentials_or_checkpoint`) |
| `second_scorer_admission_gate` (all types) | FAIL |
| overall confirmatory primary | **UNAVAILABLE** |

Artifacts refreshed under `09_outputs/pilot_chr11/` (`archcode_admission.json`, `alphagenome_smoke.json`, `second_scorer_admission.json`).

## Unblock recipe (human)

```text
1. Place ARCHCODE binary + set version/hash in score_freeze.yaml
   OR export ALPHAGENOME_API_KEY / ALPHAGENOME_CHECKPOINT
2. Re-run smoke until PASS
3. Re-run admission gate until AVAILABLE
4. Then ranking / G3–G9 may proceed (Router R4)
```

**Do not** promote PWM v1.1. **Do not** score sealed holdout.
