# DAG note — role of distance-to-CTCF

**Estimands:** T (total) vs C (CTCF-conditional) — see `scientific_freeze_v1.md`.  
**Primary estimand:** **T**. C is secondary / diagnostic.

---

## Possible roles of `D = distance_to_CTCF`

| Role | Implication for matching on D |
|------|-------------------------------|
| **Confounder** | Must control for unbiased total sequence→score effect |
| **Mediator** | Controlling D blocks part of TE→architecture path; kills T-interpretation if treated as total |
| **Collider / selection** | Conditioning can induce spurious associations |
| **Proxy for scorer input** | PWM scorer uses peak/motif proximity → matching on D can create mechanical outcome dependence |

For current PWM stand-in, D is at least a **proxy for scorer input** and may be a **mediator** on the scientific path TE → CTCF context → disruption.

---

## Interpretation rules (frozen)

```text
T fails, C unresolved (current HBB run):
  → do NOT conclude "conditional biology is stronger"
  → diagnose: negative confounding vs mediator vs scorer dependence vs clustering

T is PRIMARY for enrichment claims.
C may motivate follow-up but cannot replace T via post-hoc switch.
Loss of C does not auto-kill T; loss of T does not auto-promote C.
```

---

## Required diagnostics before interpreting C > T

1. Covariate balance T vs C (SMD tables)  
2. TE vs non-TE distribution of D (before matching)  
3. Score vs D correlation within arms  
4. Effective N by TE instance / peak / 10 kb block  
5. Sensitivity: C with D-binned strata only (no continuous match)  

Written conclusion on D’s DAG role must precede confirmatory holdout analysis.
