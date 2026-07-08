# DNA Ladder — Research Directions (backlog)

Recorded 2026-07-08, before any project infrastructure was bootstrapped. This is a list of
candidate directions to run through the falsification-first protocol (EstimandOps L0 gate →
mandatory Novelty Check → pre-registered claim → real public data → honest verdict), inherited
in spirit from ARCHCODE (`C:\Users\sboi\ARCHCODE_review`). Not prioritized yet. Not all of these
will survive a Novelty Check — some are well-trodden ground and would need the same honest
reformulation treatment that Hypothesis B (BCL11A/Casgevy) got in ARCHCODE before being worth
running.

## Candidate directions

1. **Non-coding "junk" DNA function** — how much of the ~98-99% non-coding genome is
   functional vs. evolutionary ballast (ENCODE "mostly functional" vs. evolutionary-biology
   "mostly ballast" dispute). Likely too broad as stated — would need a narrow, testable
   sub-question (specific element class, specific dataset).

2. **Liquid-liquid phase separation (LLPS) / transcriptional condensates** — how membraneless
   nuclear condensates (TF + RNA Pol II droplets) regulate gene activation. Fast-moving field
   (2018-2026); check for recent primary literature before designing anything, not just review
   articles.

3. **"Dark" transcriptome** — function of the large majority of annotated lncRNAs and ORFs with
   no known role. Needs a specific, falsifiable sub-question (e.g. one lncRNA family, one
   functional assay proxy), not "lncRNA function" as a whole.

4. **Centromeric / satellite DNA** — function of highly repetitive sequence classes only fully
   sequenced since the T2T (Telomere-to-Telomere) consortium, 2022. T2T reference now exists —
   check what's already been published on this before assuming it's untested.

5. **Transgenerational epigenetic inheritance** — mechanism by which parental
   stress/nutrition-associated methylation marks might survive embryonic reprogramming.
   Contested even in mammalian model organisms; human evidence is weaker — likely needs a
   narrow, mouse-model-literature-grounded framing, not a human-ClinVar-style test.

6. **Non-B DNA structures** (G-quadruplexes, R-loops, Z-DNA) — where/when these form in living
   cells and their regulatory role in replication/transcription. Growing literature; check for
   existing public genome-wide prediction/experimental datasets (e.g. G4-seq) before designing
   a new test.
   **Checked 2026-07-08:** real public G4-seq data exists (Chambers 2015 Nat Biotechnol,
   Marsico 2019 NAR, GEO `GSE110582`) but the only found download is a 21GB raw `.tar` of
   fastq/bigwig files -- impractical to process in a single session. A smaller processed
   peak-call/BED file (journal supplementary, or a UCSC track) was not located on a first
   pass. Parked, not pursued further today -- worth a second look with more targeted search
   (e.g. UCSC Genome Browser track hubs, or the paper's own GitHub repo if one exists) before
   attempting again.

7. **Real-time single-cell 3D genome dynamics** — chromatin loops as dynamic, fluctuating
   structures (live-imaging) vs. the population-averaged Hi-C snapshot ARCHCODE and most of the
   field use. Most directly continuous with ARCHCODE's own Kramer-kinetics physics engine —
   candidate for reusing ARCHCODE code/methodology most directly, if pursued.

8. **Missing heritability / regulatory-variant interpretation** — same VUS-interpretation
   problem worked on all day in ARCHCODE (Hypotheses A/B'/C), generalized beyond the HBB/BCL11A
   erythroid loci this session focused on. Most directly continuous with ARCHCODE's ClinVar/
   gnomAD/VEP pipeline patterns.

## Notes

- Directions 7 and 8 are the most natural to inherit ARCHCODE's actual code/scripts for
  (chromatin-dynamics modeling, ClinVar/gnomAD/VEP fetch + stats pipeline respectively) — see
  [[dna-ladder-spinoff-project]] memory in the ARCHCODE session for the "consult old project
  for lessons + keys" workflow agreement.
- Directions 1-6 are broader open-science questions further from ARCHCODE's existing tooling —
  each would need its own Novelty Check before any data work, same as every hypothesis this
  session ran.
- Bootstrap scope (methodology-only vs. methodology+scripts vs. skeleton-only) was explicitly
  deferred by the user on 2026-07-08 — do not assume a structure until that's decided.
