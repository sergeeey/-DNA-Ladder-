# Stage-2 reporter panel — desk v1

**Date:** 2026-07-15  
**Status:** `STAGE2_REPORTER_DESK_READY` · **ORDER FORBIDDEN** · **no transfection**  
**Protocol:** `SCALE_PROTOCOL_prospective_panel_v1.md` Stage 2  
**Sequences:** `D:/DNK - 2/DNA_TE_3DGenome_Context/pilot_scaffold/data/cultivation/stage2_reporters`  
**JSON:** `stage2_reporter_panel_v1.json`

## Goal

REF vs ALT autonomous activity for locked Stage-2 shortlist (8 alleles).
Does **not** freeze Stage-3; does **not** claim loops.

## Constructs

| ID | Variant | Role | Stage3 slot | AG CHIP | AG contact | 301 bp window |
|----|---------|------|:-----------:|--------:|-----------:|--------------|
| C1 | `chr11:62753923:A:G` | TEMPLATE_DEV/activity | no | 0.5408127170767988 | 0.00494472762303693 | `chr11:62753773-62754073` |
| C2 | `chr11:62753923:A:T` | activity_m3 | no | 0.2552076161608109 | 0.002063538513279387 | `chr11:62753773-62754073` |
| C3 | `chr11:72434037:C:T` | activity_m3/convergence_stage3 | yes | 0.27137969258248845 | 0.0016221310278134687 | `chr11:72433887-72434187` |
| A114 | `chr11:114036577:G:C` | activity_m3 | no | 0.16610442228205202 | 0.0015654870575027807 | `chr11:114036427-114036727` |
| ARCH754 | `chr11:75445532:G:A` | architecture_m1/stage3_arch1 | yes | 0.13502105519442772 | 0.0017045619232313974 | `chr11:75445382-75445682` |
| ARCH518 | `chr11:518575:C:A` | architecture_m1/stage3_arch2 | yes | 0.21470037683264 | 0.00183345317574484 | `chr11:518425-518725` |
| N3 | `chr11:108009167:T:C` | matched_negative/stage3_neg | yes | 0.10911584829355216 | 0.0009642947864319597 | `chr11:108009017-108009317` |
| W1 | `chr11:57568168:C:T` | disagreement/stage3 | yes | 0.12971634826471426 | 0.0011541253687547787 | `chr11:57568018-57568318` |

## Window ladder (each allele)

| Window | Length | Rule |
|--------|-------:|------|
| **minimal_301bp** | 301 | start here |
| context_1kb | 1001 | escalate if null/equivocal |
| context_2kb | 2001 | before biological B− |

## MCID

```yaml
mcid: |log2(ALT/REF)| >= 0.5 in >=2 independent transfections
fail: no reproducible direction
```

## Interpretation vs Stage-3

| Outcome | Meaning |
|---------|---------|
| Reporter+ | M3 supported in autonomous window |
| Reporter− after ladder | not activity-null for architecture claim |
| N3 near-null | matching control OK |
| Do not reshuffle Stage-3 slots by reporter beauty | LOCKED |

## Pre-order gate

- [ ] Signed panel or Phase B0 GO
- [ ] Backbone ID frozen
- [ ] Primer-BLAST / synthesis vendor chosen
- [ ] PO SKUs match this checklist

**If unchecked → no oligo PO.**

## Linked

- `STAGE1_RESULTS_2026-07-15.md`
- `prospective_panel_registry_v1.yaml`
- `BranchB_reporter_design_v1.md` (C1 template)
- `GO_note_draft_C1_B_first_v1.md`
