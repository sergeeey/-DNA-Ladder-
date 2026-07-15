# Track: TE / Alu–3D genome context

Desk track for **rare Alu/SVA SNVs vs 3D contacts and activity**, with candidate C1 as a **development template** (not wet-lab proof).

Locked E/P windows, sealed holdout, and scale protocol live in the prospective pack — start here:

- [`09_outputs/prospective/HANDOFF_PLAIN_LANGUAGE.md`](09_outputs/prospective/HANDOFF_PLAIN_LANGUAGE.md)
- [`09_outputs/prospective/SCALE_PROTOCOL_prospective_panel_v1.md`](09_outputs/prospective/SCALE_PROTOCOL_prospective_panel_v1.md)
- [`09_outputs/prospective/WORK_REPORT_C1_desk_2026-07-15.md`](09_outputs/prospective/WORK_REPORT_C1_desk_2026-07-15.md)

## Hard constraints (do not “helpfully” violate)

- Holdout remains **SEALED** — raw holdout files are **not** in this public track
- Enrichment discovery **STOPPED**; do not shop new E/P for C1
- Wet-lab / oligos **NO-GO** until human GO signature
- Stage-3 advancement **LOCKED** (C1 excluded from Stage-3 slots)
- Scale the **process**, not “prove C1”

## Layout

```
tracks/te_alu_3d/
  docs/                 methods & protocol notes
  07_methods/           methods YAML / text
  09_outputs/prospective/  claims, GO drafts, stage-1/2 packs, kill-sprint
  pilot_scaffold/       runnable desk scripts + small data subsets
  README.md
  DATA.md               how to obtain large local-only files
  .env.example          AlphaGenome key placeholder (optional)
```

## Local secrets

Copy `.env.example` → `.env` under this track (or under `pilot_scaffold/`) and set `ALPHAGENOME_API_KEY`. Never commit `.env`.

```bash
# example smoke (requires key + network)
cd tracks/te_alu_3d/pilot_scaffold
python adapters/alphagenome_adapter.py --smoke
```

## Status snapshot (desk)

- G4a multi-sample → `PASS_DESK_ROBUST` (see kill-test notes)
- PE / CRISPOR: CONDITIONAL_PASS; OT watch RADIL
- Stage-1 frozen ~13 slots; Stage-2 8-allele reporter FASTA desk-ready in original local tree (FASTA may be re-added via PR if size OK)
- Saturation mutagenesis: allele-lean retained under AG budget rules

Large Hi-C (GSE160422 `*.hic`) and juicer tools stay **outside** git — see `DATA.md`.
