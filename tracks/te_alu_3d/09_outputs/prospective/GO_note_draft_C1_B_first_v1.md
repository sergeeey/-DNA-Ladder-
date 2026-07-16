# GO-note DRAFT — C1 dual-track (B-first)

**Date:** 2026-07-15 (rev 2026-07-16 — B0 ready pack)  
**Doc type:** wet-lab authorization **template**  
**Current machine status:**

```text
authorization_state:  UNSIGNED_DRAFT
ready_pack:           GO_B0_READY_PACK_v1.md
recommended:          authorize [B0] only
oligo_order:          FORBIDDEN
transfection / PE:    FORBIDDEN
Capture-C wet:        FORBIDDEN
holdout:              SEALED
E/P anchors:          LOCKED — no shopping
```

This file is **not** a GO. It becomes GO only when the signature block below is completed.

Constrains: `NDE_C1_exhaustion_A_plus_B_v1.md`, `C1_claim_freeze_pack_v1.md`.

---

## Intent (frozen recommendation)

```text
Phase B0  — activity reporter (no genome edit)     ← authorize first
Phase A1  — PE edit + verify + OT panel            ← separate GO or addendum
Phase A2  — Capture-C / MCC ΔContact(E,P)          ← only after A1 edit PASS
```

NDE logic: M3 probe without PE; A is independent M1 probe after verified allele.

---

## Phase B0 — what a future GO would authorize

| Item | Spec |
|------|------|
| Aim | REF(A) vs ALT(G) autonomous activity at C1 |
| Constructs | **B-min 301 bp** first (`c1_reporter_minimal_301bp_{REF,ALT}.fa`) |
| Escalation | If B-min null → B-1kb → B-2kb **before** biological B− |
| Backbone | minimal promoter + insert + luc/FP (lab chooses; freeze before order) |
| Cells | HUDEP-2 preferred; K562 allowed as first-pass with demoted claim |
| Controls | empty backbone; optional scramble; optional C2 A>T later |
| MCID | \|log2(ALT/REF)\| ≥ 0.5 in ≥2 independent transfections |
| Mechanism update | B+ → M3↑; does **not** speak to loops |

**Not authorized by B0 alone:** pegRNA, ngRNA, Capture-C baits, NGS OT panel (OT needed only if PE).

---

## Phase A1 — PE addendum (separate checkbox)

Authorize only if Phase B0 GO already signed **or** explicit joint GO chosen.

| Item | Spec |
|------|------|
| Edit | `chr11:62753923 A>G` via PE |
| peg spacer / PAM | `CGTCCGATAAGCCCTGCCCC` / `CGG` (PD1) |
| PE3 ngRNA (primary) | `GTTCTAAGGTTAGGCCGAGG` (MIT91; nick −46) |
| Alternate ngRNA | `CCGAGGTGGGCGGAGCTAAT` (MIT90; −60) |
| PBS / RTT | as PrimeDesign PD1 row (13 / 16) — freeze oligo sheet at order time |
| On-target verify | amplicon-NGS; desk default ≥70% intended allele in scored samples |
| OT amplicon panel (minimum) | see table below — **required** before interpreting A |

### OT amplicon panel (pre-wet plan)

| Priority | Locus | Why | GRCh38 (CRISPOR guide hit) |
|---------:|-------|-----|----------------------------|
| 0 | **C1 on-target** | edit verify | chr11:62753923 |
| 1 | **RADIL exon** | mm3, CFD≈0.37 | chr7:4805549-4805571 (−) |
| 2 | **KDM2B intron** | highest CFD OT ≈0.40 | chr12:121534383-121534405 (−) |
| 3 | **RPAP2 exon** | mm4 exon | chr1:92388950-92388972 (−) |
| 4 | **UPF3A intron** | recurrent OT neighborhood | chr13:114290198-114290220 (−) |
| 5 | TEX40 / PHF12 / PRKG1 | exon mm4 watch | as in `G5_PE_OT_CRISPOR_PD1_v1.md` |

Primers: **desk candidates ready** — `OT_amplicon_primer_panel_desk_v1.md` + `ot_amplicon_primers_desk_v1.json`.  
Still require Primer-BLAST + Phase A1 signature before order. Watchlist ≠ proven OT.

---

## Phase A2 — Capture-C (after A1)

| Item | Spec |
|------|------|
| Estimand | ΔContact(E,P) C1 vs WT; MCID \|Δ\|≥25% WT or \|ΔOE\|≥0.5 |
| Baits | locked E + P only — `G4b_bait_windows_locked.yaml` |
| Assay | Capture-C primary; MCC escalate if blind |
| Blindness control | P1-local CTCF (P-side preferred) or documented P1-system transfer |
| Forbidden claim | «C1 disrupts E–P loop in HUDEP-2» until A2 PASS language revisit |

Quote sheet: `CaptureC_bait_quote_sheet_v1.md` (pricing only).

---

## Hard stops (any phase)

```text
- No E/P coordinate shopping after viewing allele maps
- No holdout unblind
- No ARCHCODE as independent validation
- No oligo PO without signed GO version matching ordered SKUs
- Single primary wet aim per GO (NDE Engine 2 minimal relaxation)
```

---

## Signature block (blank = NO-GO)

```yaml
go_version: DRAFT_v1          # set to GO_B0_v1 when signing B0
authorized_phases: []         # set to [B0] for recommended first wet step
signer_name: null
signer_role: null
date_signed: null
budget_cap_usd: null
partner_lab: null
backbone_id: null             # required before oligo PO
notes: null
```

**Machine read:** if `date_signed` is null → **NO-GO**.

To sign: fill the block above **or** reply in chat:

`B0 | signer_name=… | signer_role=… | backbone_id=… | budget_cap_usd=… | partner_lab=…`

---

## Linked

- `GO_B0_READY_PACK_v1.md` · `GO_A1_READY_PACK_v1.md` · `A2_CAPTURE_HELD_v1.md`  
- `B0_backbone_desk_nominate_v1.md` · `B0_PO_draft_v1.md` · `B0_insert_verify_primers_desk_v1.md`  
- `B0_transfection_day_card_v1.md` · `HOLDOUT_REMAIN_SEALED_v1.md`  
- `NDE_C1_exhaustion_A_plus_B_v1.md`  
- `BranchB_oligo_checklist_v1.md`  
- `CaptureC_bait_quote_sheet_v1.md`  
- `G5_PE_OT_CRISPOR_PD1_v1.md`  
- `G4b_protocol_freeze_v1.md`  
- `HANDOFF_PLAIN_LANGUAGE.md`  
