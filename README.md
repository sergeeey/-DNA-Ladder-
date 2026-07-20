# DNA Ladder

Falsification-first testing of hypotheses about DNA's open questions on **real public data**.

This repository is a **monorepo with clear tracks**: each research program lives under `tracks/<name>/`, while shared governance and negative results stay at the repo root.

## Tracks

| Track | Path | One-line focus |
|---|---|---|
| **SE / LLPS** | [`tracks/se_llps/`](tracks/se_llps/) | Super-enhancers, LLPS coactivators, G4/R-loop/constraint tests (mostly nulls) |
| **TE / Alu–3D** | [`tracks/te_alu_3d/`](tracks/te_alu_3d/) | Rare Alu/SVA SNVs vs 3D contacts & activity (C1 desk template + scale protocol) |

Shared across tracks:

- [`null_results/`](null_results/) — REJECT / INCONCLUSIVE / CLOSED filings (all tracks)
- [`CLAUDE.md`](CLAUDE.md) — prime directive + protocol
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to add experiments without breaking the ladder
- [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) — open directions (historical + current)
- [`PROJECT_HISTORICAL_BRIEF_v1.md`](PROJECT_HISTORICAL_BRIEF_v1.md) — historical & scientific status brief v1.1 (both tracks; claim table; wet-lab NO-GO)

## Why tracks (variant B)

- One repo → one place for collaboration, Issues, and `null_results` memory.
- Hard boundaries → SE/LLPS scripts do not accidentally reshape TE claims (and vice versa).
- Publishable desk artifacts for TE without shipping huge `.hic` / sealed holdout dumps.

## Quick start

```bash
git clone https://github.com/sergeeey/-DNA-Ladder-.git
cd -- -DNA-Ladder-   # or whatever local folder name you use
```

Pick a track and read its `README.md`. Large input files are **not** committed — see each track's `DATA.md`.

## Protocol (short)

1. L0 gate (Descriptive / Predictive / Causal)
2. Novelty check (`null_results/` + literature)
3. Pre-register `claim.md` before results
4. Real public data only
5. File honest verdicts in `null_results/` when REJECT / INCONCLUSIVE

## License / collaboration

Open for experiment and critique. Prefer PRs that stay inside one track unless the change is shared governance.
