# Chr11 Pilot Report — {{RUN_ID}}

**Status:** {{STATUS}} | **Track:** {{TRACK}} | **Date:** {{DATE}}

> Pilot mechanics report. Not a biological conclusion.

---

## 1. Hypothesis under test

Pathogenic/rare variants **inside Alu/SVA on chr11** show higher 3D disruption (ARCHCODE/LSSIM) vs matched non-TE controls after QC.

**Kill-first question:** Can we reject the null **before** claiming enrichment?

---

## 2. Scope checklist

- [ ] GRCh38 only  
- [ ] chr11 only  
- [ ] No bulk gnomAD  
- [ ] GM12878 CTCF peaks used  
- [ ] TE families: Alu + SVA  

---

## 3. QC dropout (gates 1–4)

| Gate | Excluded | Reason |
|------|----------|--------|
| G1 blacklist | {{G1_N}} | ENCODE hg38 |
| G2 mappability < {{MAP_THRESH}} | {{G2_N}} | Umap 100mer |
| G3 segdup | {{G3_N}} | genomicSuperDups |
| G4 AF discordance | {{G4_N}} | exome vs genome p < 1e-4 |
| TE not Alu/SVA | {{TE_N}} | family filter |

**Input N:** {{INPUT_N}} → **Passed N:** {{PASSED_N}}  
**KC4 triggered:** {{KC4_TRIGGERED}} — {{KC4_REASON}}

---

## 4. Matched controls (gate 5)

| Metric | Test median | Control median | SMD |
|--------|-------------|----------------|-----|
| GC | {{GC_TEST}} | {{GC_CTRL}} | {{SMD_GC}} |
| Mappability | {{MAP_TEST}} | {{MAP_CTRL}} | {{SMD_MAP}} |
| dist-CTCF | {{CTCF_TEST}} | {{CTCF_CTRL}} | {{SMD_CTCF}} |
| dist-TSS | {{TSS_TEST}} | {{TSS_CTRL}} | {{SMD_TSS}} |

**Match tier distribution:** {{MATCH_TIERS}}  
**Variants with n_controls < 20:** {{UNDERMATCHED_N}}

---

## 5. Permutation test (gate 6) — PRIMARY

| Statistic | Value |
|-----------|-------|
| Observed median Δ (TE − control) | {{OBS_EFFECT}} |
| Wilcoxon p (observed) | {{OBS_P}} |
| Permutation p | {{PERM_P}} |
| n_perm | {{N_PERM}} |

**Permutation gate passed:** {{PERM_GATE}}  

If **NO** → enrichment claims **FORBIDDEN**. Stop here.

---

## 6. Kill criteria summary

| ID | Triggered | Action |
|----|-----------|--------|
| KC1 | {{KC1}} | {{KC1_ACTION}} |
| KC2 | {{KC2}} | {{KC2_ACTION}} |
| KC3 | {{KC3}} | {{KC3_ACTION}} |
| KC4 | {{KC4}} | {{KC4_ACTION}} |

**Overall decision:** {{OVERALL_DECISION}}

---

## 7. Output split (gate 7)

### Confirmatory track

- Variants: {{CONF_N}}  
- Source: gnomAD rare + dual-track where available  
- Enrichment summary: {{CONF_ENRICHMENT_STATUS}}  

### Exploratory track

- Variants: {{EXPL_N}}  
- ClinVar-only flagged: {{CLINVAR_ONLY_N}}  
- Enrichment summary: {{EXPL_ENRICHMENT_STATUS}}  

**Rule:** Do not merge tracks in interpretation.

---

## 8. Scoring method

| Method | N variants | Notes |
|--------|------------|-------|
| ARCHCODE | {{ARCHCODE_N}} | GM12878 |
| LSSIM fallback | {{LSSIM_N}} | stub — not confirmatory |

---

## 9. Negative evidence cross-check

Map pilot findings to `08_negative_evidence/alternative_explanations_map.md`:

| Alt ID | Relevant? | Pilot observation |
|--------|-----------|-----------------|
| A1 mapping artifact | {{A1}} | {{A1_NOTE}} |
| A2 mappability | {{A2}} | {{A2_NOTE}} |
| A3 ClinVar bias | {{A3}} | {{A3_NOTE}} |
| A4 TE overlap ≠ function | {{A4}} | {{A4_NOTE}} |
| A5 CTCF proximity | {{A5}} | {{A5_NOTE}} |

---

## 10. Next steps (if not killed)

1. Orthogonal validation (KC6): expression / CRISPR from confirmatory corpus  
2. Expand beyond chr11 only after kill criteria review  
3. Wire real ARCHCODE binary  
4. Sequential covariate model (KC2)  

---

## 11. Artifacts

```
{{ARTIFACT_LIST}}
```

---

*Generated from pilot_scaffold/ — synthesis gate: chr11 pilot mechanics only.*
