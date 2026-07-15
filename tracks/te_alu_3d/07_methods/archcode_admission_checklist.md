# ARCHCODE admission checklist

**Gate:** all boxes required before `score_freeze.status → CONFIRMATORY_FROZEN`.  
**Current:** ARCHCODE **absent** in workspace → gate **FAIL** (expected).

## Required

- [ ] Binary path set in `pilot_scaffold/score_freeze.yaml` → `primary_model.binary_path`
- [ ] `available_in_workspace: true`
- [ ] Version string recorded
- [ ] SHA256 of binary recorded as `binary_hash` (matches file on disk)
- [ ] Config hash + input schema version recorded
- [ ] Training corpora / label sources documented (no silent ClinVar-only leakage)
- [ ] Genome build = GRCh38
- [ ] Leakage check: HBB development variants **not** used to tune thresholds
- [ ] Independent locus benchmark PASS (`scorer_benchmark_spec.md`) — not HBB
- [ ] Exploratory PWM (`ctcf_pwm_delta_v1.1`) remains **non-confirmatory**

## Alternative path (no ARCHCODE)

Register a **second scorer type** (not PWM-v1.1 retune), pass the same benchmark gate, then freeze as primary.

## Forbidden

- Promoting HBB PWM re-score to confirmatory
- Unblinding holdout solely because PWM bench PASS
