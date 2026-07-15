"""Pre-register G4b bait windows from locked E/P (GRCh38 + hg19)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "09_outputs" / "prospective" / "G4b_bait_windows_locked.yaml"

OUT.write_text(
    """# Locked bait windows for future Capture-C / MCC (do not shop after data view)
genome_build_primary: GRCh38
genome_build_legacy_hic: hg19
source_lock: C1_claim_freeze_pack_v1.md

baits:
  - id: bait_E
    role: enhancer_anchor
    grch38: chr11:62390000-62395000
    hg19: chr11:62157472-62162472
  - id: bait_P
    role: promoter_anchor
    grch38: chr11:62690000-62695000
    hg19: chr11:62457472-62462472
  - id: viewpoint_C1
    role: variant_site_not_bait_required
    grch38: chr11:62753923
    hg19: chr11:62521395

design_rules:
  - Prefer bait on E OR P (or both in multiplex Capture-C)
  - Do not move coordinates after seeing allele-specific maps
  - Match genome build of processed contacts
  - Include P1-local planted CTCF bait neighborhood when planted control is built
""",
    encoding="utf-8",
)
print("wrote", OUT)
