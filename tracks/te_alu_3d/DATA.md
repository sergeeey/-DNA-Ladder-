# Data assets — `te_alu_3d`

## In git (small)

- CTCF / TE BED subsets and proxy loop BEDPEs under `pilot_scaffold/data/`
- Prospective markdown/JSON/YAML under `09_outputs/prospective/`
- Desk scripts under `pilot_scaffold/` (no jars)

## Local-only (fetch yourself; gitignored)

| Asset | Typical location | Notes |
|---|---|---|
| HUDEP-2 Hi-C `.hic` | e.g. `D:\...\data\HUDEP2_GSE160422\` | GSM4873113–3118; do not commit |
| `juicer_tools.jar` + JDK 17 | local `tools/` | used by G4a multisample desk script |
| Full `clinvar.vcf.gz`, `rmsk.txt.gz` | download via UCSC / NCBI | too large for this repo |
| Holdout gnomAD dumps | **sealed** | keep private; not for public PR |
| AlphaGenome API key | `.env` | never commit |

## Manifest pointers

See also:

- `09_outputs/prospective/GSE160422_download_manifest.md`
- `pilot_scaffold` scripts that document expected paths in docstrings
