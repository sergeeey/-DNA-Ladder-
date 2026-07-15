# Track: SE / LLPS

Falsification tests around super-enhancers (SE), coactivator LLPS (BRD4/MED1), G4, R-loops, and germline constraint / ClinVar VUS density.

Most directions in this track have already **converged on REJECT** — see repo-root [`null_results/`](../../null_results/).

## Layout

```
tracks/se_llps/
  experiments/exp_<slug>/   claim.md, decision.md, results.json
  scripts/                  fetch + analysis (ROOT = this track dir)
  tests/                    verifiers
  data/input/               cached public extracts (see DATA.md)
  README.md
  DATA.md
```

## Run tests

From this track directory (or repo root with path):

```bash
cd tracks/se_llps
python -m pytest tests/ -q
# or run individual verify_*.py scripts
```

## Path note (post-monorepo move)

Scripts resolve `ROOT = Path(__file__).resolve().parent.parent`, which is now `tracks/se_llps/` (not the old repo root). Paths like `ROOT/data/input/...` are unchanged relative to the track.
