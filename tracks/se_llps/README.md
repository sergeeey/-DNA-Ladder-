# Track: SE / LLPS

Falsification tests around super-enhancers (SE), coactivator LLPS (BRD4/MED1), G4, R-loops, and germline constraint / ClinVar VUS density.

Most enrichment directions in this track have already **converged on REJECT** — see repo-root [`null_results/`](../../null_results/).

**Active (2026-07-20):** `experiments/exp_topology_community_crispr_eg/` — C-B1 Predictive
claim (CRE-community topology ΔAUC over SE membership for CRISPR E–G in K562);
status `PENDING_KILL_TEST` after T0 freeze + ENCODE-rE2G feature audit.

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
