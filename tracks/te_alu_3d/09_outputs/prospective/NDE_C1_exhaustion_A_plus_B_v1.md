# Narrow Discovery — C1 dual-track A+B (Engine 4 + Engine 2)

**Date:** 2026-07-15  
**Skill:** `narrow-discovery-engines`  
**Engines run:** **4 Exhaustion Mapping** (primary) · **2 Constraint Relaxation** (design gates)  
**Engines deferred:** 1 Orphan Data · 3 Anomaly-First  
**Scope:** candidate **C1 only** · does **not** reopen enrichment / holdout / PE shopping  
**Status:** `NDE_DESK` · wet-lab still **NO-GO** · oligo order still **FORBIDDEN**

---

## Routing decision (why this, not 1/3)

| Engine | Input available? | Use now? |
|--------|------------------|----------|
| **4** | Finite mechanism set for cis effects at C1 | **YES** — constrains A+B |
| **2** | Frozen assumptions that shape assay design | **YES** — cheap desk gates |
| 1 | Residual model + MCID over a live panel | **NO** — enrichment STOPPED; holdout SEALED; C1 locked |
| 3 | Lab/desk anomaly without cause | **NO** — reserve for post A/B paradox |

`null_results/INDEX.md`: **absent**. Kill map below uses claim-freeze + desk FAIL/STOPPED records instead.

---

# Engine 4 — Exhaustion Mapping

## Step 1 — Solution-space boundaries

**Question:** What cis-acting mechanisms could make C1 (`chr11:62753923 A>G`, AluSz, HUDEP-2) causally relevant?

| ID | Mechanism type | Axis of variation | Theoretical note |
|----|----------------|-------------------|------------------|
| **M1** | Architecture: allele ΔContact(E,P) at **locked** anchors | magnitude / sign / cell-state timing | Requires editable allele + Capture-C/MCC; direction **not** pre-claimed |
| **M2** | Cohesin / insulation without CTCF motif loss | RAD21 Δ vs stable CTCF; local TAD edge | Live if M1 contacts blind but polymer rheology changes |
| **M3** | Sequence/activity (TF / RNAPII / enhancer potency) | autonomous (reporter) vs chromatinized | Primary lean from AG CHIP_TF channels |
| **M4** | Promoter / splice / RNA processing at C1 site | annotation distance to TSS/splice | Low prior: intergenic AluSz; must keep as kill-target |
| **M5** | Edit / assay artifact | PE OT, clone selection, reporter backbone | Always alive until controls kill |
| **M0** | Passenger / no cis effect | — | Default after verified-edit dual null |
| **M_mix** | Joint M1+M3 (or M2+M3) | order / mediation | Distinct from pure M1 or M3 |

**Out of bounds (do not expand here):** genome-wide discovery ranking; ARCHCODE as independent validation; re-shopping E/P after seeing allele data.

**Axes frozen for this map:**

```text
build:        GRCh38 (hic maps often hg19 — lift locked)
cell:         HUDEP-2 preferred
E:            chr11:62390000-62395000
P:            chr11:62690000-62695000
edit path:    PE PD1 (CONDITIONAL_PASS OT) — not a mechanism cell
```

## Step 2 — Already-killed / constrained regions

| Region | Status | What was ruled out (Kill Analysis) | Evidence level |
|--------|--------|------------------------------------|----------------|
| Classic **base editing** for C1 A>G | **KILLED (edit path)** | ABE/CBE window unfit — does **not** kill biology of A>G | desk FAIL (`G5_editability`) |
| Claim «C1 disrupts E–P loop in HUDEP-2» | **FORBIDDEN / untested** | Language prohibited; allele contact **not** measured | claim freeze |
| Enrichment track as discovery engine | **STOPPED** | Population enrichment not used to promote C1 further | project freeze |
| ARCHCODE = independent scientific validation | **KILLED (role)** | Exploratory only; own-project ≠ external proof | archcode note |
| Independent validated 3D scorer | **ABSENT** | Cannot map residual orphans genome-wide | Machine status |
| K562-only planted CTCF as HUDEP-2 P1-local | **mostly KILLED** | E_near PASS; P_strong/P_near/C1_near FAIL vs HUDEP-2 peaks | `P1_local_*` |
| Genome-wide Hi-C as sole G4b readout | **KILLED (assay choice)** | Blind risk at allele scale; Capture-C primary | G4b freeze |
| PE PD1 mm0–2 OT clusters | **largely KILLED (desk)** | CRISPOR 0/0/0; RADIL mm3 remains **watch**, not proven OT | CONDITIONAL_PASS |

**Important:** none of the above kills **M1** biology. G4a only shows **WT** Contact(E,P) exists.

## Step 3 — Exhaustion map (mechanism × status)

```text
M3      ALIVE_PRIMARY     AG lean + Branch B designed; allele effect NOT tested
M1      ALIVE_CONDITIONAL G4a WT contact PASS_DESK; G4b NOT TESTED
M2      ALIVE_UNKNOWN     no RAD21 / allele insulation readout planned as primary
M4      ALIVE_LOW_PRIOR   annotation kill pending (TSS/splice check desk)
M5      ALIVE_ALWAYS      OT (RADIL…) + neutrals + mock-edit required if wet
M0      ALIVE_DEFAULT     residual after verified edit + B− + A−
M_mix   ALIVE             needs patterned A/B outcomes (see matrix)
```

**Alive region after desk kills (≤3 high-prior cis classes):**

```text
focused field for dual-track:  { M3, M1, M0 }
with mandatory competitors:    { M2 (secondary), M4 (desk kill), M5 (controls) }
```

Termination condition of Engine 4: **met** for handoff — ≤3 primary types → A+B are the tournament field, not a new discovery pass.

## Step 4 — Differentiating outcome matrix (what A and B kill)

Definitions (desk MCIDs):

```text
B+ : |log2(ALT/REF)| ≥ 0.5 reproducible (≥2 reps)   [BranchB_reporter]
B− : activity null under B-min; escalate 1 kb/2 kb before biological B− claim
A+ : edit verified AND |ΔContact| ≥ MCID (|Δ|≥25% WT or |ΔOE|≥0.5) reproducible
A− : edit verified AND below MCID (assay not blind: P1-local or documented transfer)
```

Assay-blind / failed-edit rows are ** inconclusive** — do not update mechanism map.

| B | A | Update map |
|---|---|------------|
| **+** | **−** | **M3↑**; **M1 at locked E–P ↓/killed** (for this estimand); M_mix→weak; consider M2 only if secondary CTCF/RAD21 moves |
| **−** | **+** | **M1↑**; autonomous short-window M3 ↓; keep chromatinized M3 speculative; M0↓ |
| **+** | **+** | **M_mix or M3-led with secondary contact**; do **not** claim loop disruption without mediation design; expression/occupancy next |
| **−** | **−** | **M1 & autonomous M3 ↓** for current assays → elevate **M0** or **M2/M4**; optional expand reporter / insulation panel **once**, no E/P shopping |
| fail edit / OT mess | any | **M5** dominates interpretation until cleaned |

### Interpreting Branch order (desk recommendation)

```text
Preferred information order (cost):
  1) B-min REF vs ALT          → cheap M3 probe (no genome edit required)
  2) PE + verify + OT panel   → unlocks A; shared with future endogenous RNA-seq
  3) G4b Capture-C ΔContact    → M1 probe

If B+ strong and budget tight: A still required before any architecture claim.
If B− after escalation: A remains the only path to keep M1 alive.
```

### Forbidden inference (even after outcomes)

```text
FORBIDDEN: "C1 disrupts enhancer–promoter loop in HUDEP-2"
  until A+ AND language revisit after G4b PASS with locked anchors.

OK after B+: sequence/activity-effect supported in reporter context
OK after A+: allele ΔContact ≥ MCID at locked E–P (architecture estimand PASS)
OK after B−A+: architecture-sensitive effect without short autonomous activity
```

---

# Engine 2 — Constraint Relaxation (minimal, one-at-a-time)

## Step 1 — Assumption inventory

**(a) Known true (do not relax for discovery):**

- C1 coordinate / alleles locked  
- Locked E and P windows (search)  
- G4a WT Contact(E,P) desk-detected  
- P1-system 3′HS1 assay-chain PASS_DESK  
- PE PD1 spacer + preferred PE3 ngRNA desk-frozen  
- wet-lab NO-GO until GO note  

**(b) Believed, not verified:**

| # | Assumption | If FALSE → new solution class | Testability (&lt;4 h desk?) |
|---|------------|-------------------------------|----------------------------|
| B1 | 301 bp suffices to show autonomous M3 | escalate B-1kb / B-2kb before biological B− | YES — sequences already on disk |
| B2 | Architecture effect **equals** ΔContact(locked E–P) | add insulation / P1-local CTCF occupancy as secondary M2 path | PARTIAL — peaks nominated; no wet |
| B3 | HUDEP-2 reporter ≈ erythroid cis activity | allow K562 first-pass but demote claim | YES — design only |
| B4 | P gene at locked P is the relevant TSS | nominate HUDEP-2 TSS before expression claims | YES — annotation/desk RNA tracks |
| B5 | RADIL (and panel OT) do not confound A | mandatory OT amplicon in any wet GO | YES — primer desk design |

**(c) Inherited without local check:**

| # | Assumption | If FALSE | Testability |
|---|------------|----------|-------------|
| C1 | AluSz TE context is mechanistically required | SNV-only synthetic insert without TE flanks as control | speculative (revival: after B+) |
| C2 | Capture-C sensitivity transfers from 3′HS1 scale to C1 | MCC escalation rule (already in G4b) | not &lt;4 h wet; already coded as escalation |
| C3 | PE required to learn M3 | reporter alone can kill/support M3 without PE | YES — Branch B independence |

## Step 2–4 — Ranked relaxations for A+B design (execute order)

| Rank | Relaxation | Action before any oligo GO | Revival / kill rule |
|------|------------|----------------------------|---------------------|
| **1** | C3: PE not required for M3 | Treat **Branch B** as independent; GO-note may authorize B without A | If B inconclusive → optional PE later |
| **2** | B1: 301 bp may be blind | Freeze **escalation ladder** B-min → 1 kb → 2 kb before claiming B− | Biological B− only after ladder |
| **3** | B5: OT may confound | Draft OT amplicon panel: C1 on-target + **RADIL** + KDM2B (+…) in GO-note | No A interpretation without OT plan |
| **4** | B2: M1≠only ΔContact | Keep Capture-C primary; schedule **optional** P1-local CTCF/RAD21 only if A−B− or A weird | Do not expand primary estimand |
| **5** | B4: wrong gene | Desk TSS nomination before endogenous RNA claims | Expression claims gated |
| **hold** | C1 Alu necessity | No synthesis of TE-stripped controls until B+ | speculative branch |

**Minimal relaxation rule:** when writing GO-note, pick **one** primary wet aim (B-first vs A-coupled). Do not authorize multi-assumption wet jumps (e.g. new anchors + new reporter length + new cell) in one GO.

---

## Deferred engines — trigger cards

### Engine 1 (Orphan Data) — do **not** run until

```text
revival: open residual panel with defined MCID outside sealed holdout
OR: post-wet cohort of edits with quantitative residuals vs M3-primary model
```

### Engine 3 (Anomaly-First) — run only if

```text
anomaly examples:
  - B+ huge AND A− with verified non-blind assay
  - A+ AND B− after full reporter escalation
  - edit verified, both A− B−, but endogenous gene Δ large
  - RADIL (or OT) edited when on-target clean

Then: anomaly → cause list → differentiating test — not post-hoc story.
```

---

## Outputs → next desk artifacts (still no order)

1. **GO-note draft** constrained by this map: B-first recommended; A optional second; OT panel mandatory if PE.  
2. **Branch B oligo checklist** with escalation ladder (B1).  
3. **Capture-C bait quote sheet** (A) — quote only.  
4. Optional: HUDEP-2 TSS nomination desk (B4).

## Machine summary

```text
NDE Engine4:              DONE — alive high-prior {M3, M1, M0}
NDE Engine2:              DONE — top relaxations C3, B1, B5
dual-track logic:         A and B are differentiators, not parallel “more data”
architecture claim:       still FORBIDDEN until G4b A+
wet-lab / oligos:         NO-GO / FORBIDDEN
holdout:                  SEALED
E/P anchors:              LOCKED (no shopping)
```

## Linked

- `C1_claim_freeze_pack_v1.md`  
- `G4b_protocol_freeze_v1.md`  
- `BranchB_reporter_design_v1.md`  
- `G5_PE_OT_CRISPOR_PD1_v1.md`  
- `HANDOFF_PLAIN_LANGUAGE.md`  
- `PAUSE_PIN_2026-07-14.md`  
