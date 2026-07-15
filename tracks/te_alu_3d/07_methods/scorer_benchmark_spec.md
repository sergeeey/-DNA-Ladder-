# Scorer Benchmark Spec — Track A

**Gate:** must PASS before confirmatory biological run.  
**Applies to:** `ctcf_pwm_delta_v1`, future ARCHCODE, any primary scorer.

---

## Goal

Show the scorer:

1. Separates positive vs negative controls  
2. Has correct **allele direction** (disrupting alt scores higher than ref-preserving)  
3. Is not driven only by GC / peak-distance artifacts  

---

## Control sets (build before holdout)

| Set | Definition | Expected |
|-----|------------|----------|
| **P1** | Synthetic edits destroying strong CTCF consensus in HUDEP-2 peak summits | high disruption |
| **P2** | Known/literature CTCF-disrupting alleles (if any in scope) | high |
| **N1** | Variants outside motif core (±PWM flank) in same peaks | low |
| **N2** | Synonymous / weak transitions far from peaks (>5 kb) | low |
| **S1** | Strand / orientation flip of same motif | consistent Δ magnitude |
| **S2** | Ref↔Alt reversal | score sign flips appropriately |

Minimal file layout:

```text
pilot_scaffold/data/benchmark/
  positive_controls.tsv
  negative_controls.tsv
  sanity_reversal.tsv
  expected_outcomes.yaml
```

---

## Pass criteria (pre-registered)

```yaml
scorer_benchmark_gate:
  metric: auROC_or_ranksum
  positive_vs_negative:
    min_auROC: 0.75
    # OR median(P) - median(N) > 0 with block-perm p < 0.01 on benchmark only
  direction_reversal:
    fraction_correct_sign: >= 0.9
  peak_summit_monotonicity:
    required: exploratory_report_only
  fail_action: STOP_biological_enrichment_runs
```

---

## ARCHCODE-specific extras

Document before freeze:

- training corpora / labels  
- genome build  
- leakage check vs HBB development variants  
- independent locus benchmark (not HBB)  

---

## Output

```text
09_outputs/pilot_chr11/benchmark/
  scorer_benchmark_report.json
  pass_fail.txt
```

Status values: `PASS` | `FAIL` | `NOT_RUN`.
