# Controls — exp_te_age_loop_reproducibility (C-D1)

**Status:** PREREGISTERED 2026-07-21 — before primary Δ_repro  
**Parent claim:** `claim.md`

## Design controls

| Control | Rule |
|---------|------|
| Age definition | UCSC rmsk **milliDiv** (parts per thousand vs consensus); min among overlapping TE |
| Tertiles | Computed on TE-hit window milliDiv distribution only (chr1–22,X) |
| TE class | Primary = SINE∪LINE∪LTR; sensitivity = Alu family only (`repFamily` contains `Alu`) |
| Assay pair | Frozen Pol II `ENCFF511QFN` vs Hi-C `ENCFF693XIL` (same as C-A1 K562) |
| Unit | Fixed 1 kb midpoints (equalizes span; C-A1 convention) |
| Non-TE windows | Report overall shared rate for non-TE windows (context only; not primary) |

## Sensitivity (pre-registered)

1. **Alu-only** tertiles (repFamily Alu*) — if n/bin ≥ 200 else SKIP + note.
2. **Class-stratified** Δ within SINE / LINE / LTR separately (exploratory; not primary kill).
3. **Middle tertile** reported for monotonicity check (old ≥ mid ≥ young expected if SUPPORT).

## Matching note

Primary contrast is **within TE-hit windows** (young vs old), not TE vs non-TE.
Length matching unnecessary at fixed 1 kb windows. Class confounding addressed via
Alu-only + class-stratified sensitivities.

## Forbidden substitutions

- Do not swap in Mustache / DELTA / localizer as primary Hi-C caller for this claim
- Do not redefine age as subfamily labels post-hoc without labeling exploratory
- Synthetic / mock loops forbidden

## Checklist

- [x] claim.md written before outcome analysis
- [x] downloads + checksums
- [x] primary Δ_repro
- [x] Alu-only sensitivity
- [x] decision filed
