# gnomAD — chr11 / HBB window only

**Forbidden:** full gnomAD genome download.

## Status (2026-07-13)

Fetched via **gnomAD GraphQL API** (no bulk VCF):

| File | Content |
|------|---------|
| `gnomad_hbb_window.tsv` | 39 737 variants, chr11:5 200 000–5 300 000 |
| `gnomad_hbb_window.vcf.gz` | minimal VCF for `run_pilot.py` loader |

```bash
python fetch_dual_track_inputs.py --start 5200000 --end 5300000 --chunk 20000
```

## Optional: full chr11 sites (still not bulk genome)

```text
https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
```

Only if GraphQL window is insufficient; requires tabix/remote slice — do **not** download whole genomes release.
