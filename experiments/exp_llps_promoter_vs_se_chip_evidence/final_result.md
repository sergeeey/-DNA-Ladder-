---
experiment: exp_llps_promoter_vs_se_chip_evidence
closed_at: 2026-07-10
status: CLOSED
final_verdict: NO REPORTABLE GENERAL SE-SPECIFIC BRD4/MED1 SIGNAL
publication_status: DO_NOT_PROMOTE
wet_lab_status: NO_GO
reopen_condition: new independently processed, quality-matched datasets or a substantially stronger matched-control design
---

# Final Result — BRD4/MED1 occupancy at super-enhancers

## Final question

After replacing the original weak comparator (super-enhancers versus broad genomic background) with an activity-filtered H3K27ac-positive comparator, is there reproducible evidence that BRD4 or MED1 has a super-enhancer-specific occupancy preference across available ENCODE cell lines?

## Final evidence

| Cell line | Factor | SE / H3K27ac-active non-SE peak-density ratio | Final interpretation |
|---|---:|---:|---|
| K562 | BRD4 | 1.048 | No meaningful SE preference |
| HepG2 | BRD4 | 0.809 | No SE preference; direction reverses |
| K562 | MED1 | 1.788 | Exploratory K562-specific signal |
| HepG2 | MED1 | 0.733 | Does not replicate; direction reverses |

## Final verdict

1. **The original general claim does not survive the stronger comparator.** Most of the apparent enrichment was driven by comparing active regulatory chromatin with a largely inactive genomic background.
2. **BRD4 is closed as negative for the tested claim.** Neither K562 nor HepG2 supports a reproducible SE-specific preference after the activity-filtered comparison.
3. **MED1 is closed as inconsistent, not positive.** K562 retains a sizeable ratio (1.788), but HepG2 reverses direction (0.733). A one-cell-line signal without replication is not a general finding.
4. **No LLPS or condensate mechanism was tested.** ChIP-seq peak occupancy cannot establish phase separation, dynamic condensates, causality, or enhancer-to-promoter spatial organization.
5. **No wet-lab escalation is justified from this result.** The available evidence does not clear a computational go/no-go threshold for experimental validation.

## Data boundary

The ENCODE inventory review performed during this analysis found no additional valid third cell line for a like-for-like BRD4 or MED1 replication. The available released datasets used here therefore exhaust the directly comparable ENCODE scope identified in the session. This is a boundary of the current evidence, not proof that other usable datasets cannot exist in GEO or future releases.

## Residual hypothesis retained, but not promoted

The K562 MED1 ratio of 1.788 is retained only as an **exploratory cell-context-specific anomaly**. It must not be cited as evidence of a general MED1 super-enhancer preference. Reopening it would require:

- independently processed raw data with comparable replicate and peak-calling standards;
- true enhancer controls excluding promoter-proximal H3K27ac regions;
- matching by H3K27ac intensity, accessibility, region length, mappability, copy number, and TSS distance;
- signal-level analysis rather than peak-midpoint counts;
- uncertainty estimation by chromosome/region bootstrap;
- replication in at least one additional biologically and technically comparable cell system.

## Methodological conclusion

The primary surviving value of this experiment is methodological rather than biological:

> Enrichment against the whole genome is not an adequate control for active chromatin proteins. A positive result remains provisional until it survives a genuinely comparable negative control.

The experiment is therefore **closed**. The full historical path remains preserved in `claim.md`, `decision.md`, and `results_matched_control.json`; this file is the canonical final disposition.
