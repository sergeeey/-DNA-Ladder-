# Controls — exp_te_orientation_loop_asymmetry (C-J1)

**Status:** PREREGISTERED 2026-07-21 — before primary |Δ_orient|  
**Parent claim:** `claim.md`

## Design controls

| Control | Rule |
|---------|------|
| Loop geometry | Keep bedpe **pairs**; left = genomic 5′ anchor, right = 3′ |
| Unit | Fixed 1 kb midpoints after pad ≥1 kb (equalizes span) |
| TE class | Primary = SINE∪LINE∪LTR; sensitivity = Alu family |
| Strand rule | Max bp-overlap TE; ties → earliest start; ignore `strand` not in `{+,-}` |
| Assay | Frozen Hi-C HiCCUPS `ENCFF693XIL` only (same C-A1/C-D1 K562) |
| Asymmetry | Left vs right **pooled TE-hit windows** (not loop-matched pairs for primary) |

## Sensitivity (pre-registered)

1. **Alu-only** |Δ_orient| — if n_left ≥ 200 and n_right ≥ 200 else SKIP + note.
2. **Both-TE opposite-strand fraction** (exploratory) — loops with TE on both ends;
   report |f_opp − 0.5|; not a primary kill gate.

## Matching note

Primary contrast is **within TE-hit anchors** (left vs right genomic side). Length
matching unnecessary at fixed 1 kb windows. No umap gate required for this
orientation Δ (exposure is strand among TE-hits, not TE vs non-TE enrichment).

## Forbidden substitutions

- Do not swap in Mustache / DELTA / Pol II ChIA as primary loop set for this claim
- Do not redefine orientation as CTCF PWM / motif strand post-hoc
- Synthetic / mock loops forbidden

## Checklist

- [x] claim.md written before outcome analysis
- [x] downloads + checksums
- [x] primary |Δ_orient|
- [x] Alu-only sensitivity
- [x] decision filed
