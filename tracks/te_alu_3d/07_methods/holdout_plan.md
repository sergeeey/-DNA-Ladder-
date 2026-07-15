# Confirmatory Holdout Plan — Track A

**HBB/HUDEP-2 role:** exploratory development + calibration (labels viewed).  
**Confirmatory:** pre-registered erythroid holdout, labels hidden until freezes signed.

---

## Holdout requirements

| Requirement | Spec |
|-------------|------|
| Cell context | Erythroid (HUDEP-2 or primary erythroblast) — KC0 PASS |
| CTCF peaks | Same cell type as scoring context |
| Locus | **Non-HBB** chr11 block(s) or multi-locus erythroid panel |
| Variant class | Rare SNVs in Alu/SVA (same as development; TE MEIs separate track) |
| Independent TE instances | Target ≥ 50 unique TE copies post-QC (not just N_SNV) |
| Labels | Hidden until `scientific_freeze` + `score_freeze` confirmatory |
| Scorer | Benchmark PASS; primary frozen; one primary estimand = **T** |

---

## Proposed candidates (pick one before unblinding)

**SEALED** in `holdout_manifest.yaml` (2026-07-13):

| ID | Window | Rationale |
|----|--------|-----------|
| HO_A | chr11:65–66 Mb | top HUDEP-2 CTCF density |
| HO_B | chr11:67–68 Mb | second dense bin |
| HO_C | chr11:64–65 Mb | panel diversity |

HBB (5.2–5.3 Mb) explicitly excluded. `unblind_authorized: false` until protocol note.

---

## Analysis template (confirmatory)

```text
1. KC0 pass
2. QC gates 1–4
3. Control A matching for estimand T (primary)
4. Report C as secondary only
5. Block permutation + cluster-aware effective N
6. Enrichment claim ONLY if:
   - scientific_freeze satisfied
   - score_freeze status == FROZEN (ARCHCODE or validated primary)
   - scorer_benchmark == PASS
   - primary estimand T passes perm + direction gates
```

---

## Explicitly forbidden

- Promoting HBB re-analysis to confirmatory after ARCHCODE drop-in alone  
- Switching primary estimand to C because p is smaller  
- Calling PWM/ARCHCODE output “3D disruption” without binding/contact/expression layers  
