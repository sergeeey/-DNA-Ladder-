# Contributing to DNA Ladder

## Tracks first

Put new work under the matching track:

- Super-enhancer / LLPS / G4 / R-loop / heritability → `tracks/se_llps/`
- Alu/SVA rare SNV vs 3D/activity (C1 / prospective panel) → `tracks/te_alu_3d/`
- Shared rejects / meta-closures → `null_results/` at **repo root**

Do not mix track data directories. If a hypothesis spans tracks, open an Issue and agree on a home track first.

## Experiment folder contract (`se_llps`)

```
tracks/se_llps/experiments/exp_<slug>/
  claim.md      # pre-registered
  decision.md   # PASS / REJECT / INCONCLUSIVE + what it does NOT mean
  results.json  # numeric evidence
```

Scripts live in `tracks/se_llps/scripts/`; verifiers in `tracks/se_llps/tests/`.

## TE desk contract (`te_alu_3d`)

- Claims and GO notes: `09_outputs/prospective/`
- Runnable desk code: `pilot_scaffold/`
- Do **not** commit `.env`, API keys, sealed holdout VCFs/TSVs, or full `.hic` matrices
- Do **not** open the holdout or reshape Stage-3 after reporter results without a written human GO

## Null results

Every REJECT / INCONCLUSIVE / CLOSED must get a short filing under `null_results/` and a row in `null_results/INDEX.md`. Include “what this does NOT mean”.

## What not to commit

- `.env`, keys, credentials notes with local paths that imply a live key is in-repo
- `*.hic`, juicer `.jar`, clinvar/rmsk full dumps, holdout raw files
- `__pycache__`, large OT dumps, Capture-C bait quote blobs unless they are small text

See root `.gitignore` and each track's `DATA.md`.

## PR hygiene

1. One track per PR when possible
2. Point to `claim.md` / decision artifact
3. Say whether the result updates `null_results/`
4. Keep secrets out of the diff
