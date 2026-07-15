"""Fetch dual-track inputs without bulk gnomAD genome download.

1) gnomAD HBB window via GraphQL API (chr11:5.2–5.3Mb) → data/gnomad_hbb_window.tsv + VCF-like.gz
2) HUDEP-2 CTCF peaks (ChIP-Atlas) chr11 → data/ctcf_HUDEP2_peaks.bed
3) Optional: expand window via --start/--end
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

GNOMAD_API = "https://gnomad.broadinstitute.org/api"
CHIP_ATLAS_URLS = [
    "https://chip-atlas.dbcls.jp/data/hg38/eachData/bed05/SRX5821035.05.bed",
    "https://dbarchive.biosciencedbc.jp/kyushu-u/hg38/eachData/bed05/SRX5821035.05.bed",
]


def _post_graphql(query: str, variables: dict | None = None, timeout: int = 180) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(
        GNOMAD_API,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DNK-TE3D-pilot/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def fetch_gnomad_window(
    chrom: str,
    start: int,
    end: int,
    chunk: int = 25000,
    *,
    out_prefix: str | None = None,
    max_attempts: int = 16,
    min_chunk: int = 2000,
    allow_gaps: bool = False,
) -> Path:
    """Paginate region in chunks to avoid API timeouts.

    out_prefix: stem under data/ (default gnomad_hbb_window).
    Resumes from `{stem}.partial.jsonl` + `{stem}.progress` if present.
    """
    DATA.mkdir(parents=True, exist_ok=True)
    stem = out_prefix or "gnomad_hbb_window"
    out_tsv = DATA / f"{stem}.tsv"
    out_vcf = DATA / f"{stem}.vcf.gz"
    partial = DATA / f"{stem}.partial.jsonl"
    progress = DATA / f"{stem}.progress"

    # gnomAD API chrom without chr prefix for region()
    api_chrom = chrom.replace("chr", "")
    rows: list[dict] = []

    query = """
    query RegionVariants($chrom: String!, $start: Int!, $stop: Int!) {
      region(chrom: $chrom, start: $start, stop: $stop, reference_genome: GRCh38) {
        variants(dataset: gnomad_r4) {
          variant_id
          chrom
          pos
          ref
          alt
          genome { af ac an filters }
          exome { af ac an filters }
        }
      }
    }
    """

    pos = start
    cur_chunk = chunk
    gaps: list[dict[str, int | str]] = []
    if progress.exists() and partial.exists():
        try:
            pos = max(start, int(progress.read_text(encoding="utf-8").strip()) + 1)
            with partial.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))
            print(f"resume {stem} at pos={pos} loaded={len(rows)}")
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"progress corrupt ({exc}); restarting from {start}")
            pos = start
            rows = []
            partial.unlink(missing_ok=True)
            progress.unlink(missing_ok=True)

    while pos < end:
        stop = min(pos + cur_chunk - 1, end)
        print(f"gnomAD GraphQL {api_chrom}:{pos}-{stop} (chunk={cur_chunk})")
        attempt = 0
        data: dict | None = None
        while True:
            attempt += 1
            try:
                data = _post_graphql(
                    query,
                    {"chrom": api_chrom, "start": pos, "stop": stop},
                )
                break
            except urllib.error.HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504}:
                    raise
                if attempt >= max_attempts:
                    if cur_chunk > min_chunk:
                        cur_chunk = max(min_chunk, cur_chunk // 2)
                        print(f"  shrink chunk -> {cur_chunk}, reset attempts")
                        attempt = 0
                        stop = min(pos + cur_chunk - 1, end)
                        print(f"gnomAD GraphQL {api_chrom}:{pos}-{stop} (chunk={cur_chunk})")
                        continue
                    if allow_gaps:
                        print(f"  SKIP gap {pos}-{stop} after HTTP {exc.code} (allow_gaps)")
                        gaps.append(
                            {
                                "chrom": f"chr{api_chrom}",
                                "start": pos,
                                "end": stop,
                                "reason": f"HTTP_{exc.code}",
                            }
                        )
                        progress.write_text(str(stop), encoding="utf-8")
                        pos = stop + 1
                        cur_chunk = chunk
                        data = None
                        break
                    raise
                wait = min(60, 5 * (2 ** min(attempt - 1, 4)))
                print(f"  HTTP {exc.code}, retry in {wait}s ({attempt}/{max_attempts})")
                time.sleep(wait)
            except (TimeoutError, urllib.error.URLError) as exc:
                if attempt >= max_attempts:
                    if cur_chunk > min_chunk:
                        cur_chunk = max(min_chunk, cur_chunk // 2)
                        print(f"  shrink chunk -> {cur_chunk}, reset attempts")
                        attempt = 0
                        stop = min(pos + cur_chunk - 1, end)
                        continue
                    if allow_gaps:
                        print(f"  SKIP gap {pos}-{stop} after network error (allow_gaps)")
                        gaps.append(
                            {
                                "chrom": f"chr{api_chrom}",
                                "start": pos,
                                "end": stop,
                                "reason": type(exc).__name__,
                            }
                        )
                        progress.write_text(str(stop), encoding="utf-8")
                        pos = stop + 1
                        cur_chunk = chunk
                        data = None
                        break
                    raise
                wait = min(60, 5 * attempt)
                print(f"  network timeout/error, retry in {wait}s ({attempt}/{max_attempts})")
                time.sleep(wait)

        if data is None:
            continue
        assert data is not None
        if data.get("errors"):
            print("  API errors:", data["errors"][:2])
        variants = (((data.get("data") or {}).get("region") or {}).get("variants")) or []
        print(f"  n={len(variants)}")
        chunk_rows: list[dict] = []
        for v in variants:
            genome = v.get("genome") or {}
            exome = v.get("exome") or {}
            af = genome.get("af")
            if af is None:
                af = exome.get("af")
            filt = genome.get("filters") or exome.get("filters") or []
            filt_s = ",".join(filt) if isinstance(filt, list) else str(filt)
            alt = v.get("alt")
            if isinstance(alt, list):
                alt = alt[0] if alt else ""
            chunk_rows.append(
                {
                    "chrom": f"chr{v.get('chrom', api_chrom)}".replace("chrchr", "chr"),
                    "pos": int(v["pos"]),
                    "ref": v.get("ref", ""),
                    "alt": alt,
                    "af": af,
                    "filters": filt_s,
                    "variant_id": v.get("variant_id", ""),
                    "ac_genome": (genome or {}).get("ac"),
                    "an_genome": (genome or {}).get("an"),
                    "af_exome": (exome or {}).get("af"),
                }
            )
        rows.extend(chunk_rows)
        with partial.open("a", encoding="utf-8") as fh:
            for r in chunk_rows:
                fh.write(json.dumps(r) + "\n")
        progress.write_text(str(stop), encoding="utf-8")
        pos = stop + 1
        # slowly grow chunk back after successes
        if cur_chunk < chunk and attempt == 1:
            cur_chunk = min(chunk, cur_chunk * 2)
        time.sleep(0.8)

    if gaps:
        gap_path = DATA / f"{stem}.gaps.json"
        gap_path.write_text(json.dumps({"gaps": gaps, "n_gaps": len(gaps)}, indent=2), encoding="utf-8")
        print(f"wrote {gap_path} n_gaps={len(gaps)}")

    # dedupe
    seen = set()
    uniq = []
    for r in rows:
        key = (r["chrom"], r["pos"], r["ref"], r["alt"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)

    with out_tsv.open("w", encoding="utf-8") as fh:
        fh.write("chrom\tpos\tref\talt\taf\tfilters\tvariant_id\tac_genome\tan_genome\taf_exome\n")
        for r in uniq:
            fh.write(
                f"{r['chrom']}\t{r['pos']}\t{r['ref']}\t{r['alt']}\t{r['af']}\t"
                f"{r['filters']}\t{r['variant_id']}\t{r['ac_genome']}\t{r['an_genome']}\t{r['af_exome']}\n"
            )

    # minimal VCF for loader compatibility
    with gzip.open(out_vcf, "wt", encoding="utf-8") as fh:
        fh.write("##fileformat=VCFv4.2\n")
        fh.write("##source=gnomAD_GraphQL_r4_window_slice\n")
        fh.write('##INFO=<ID=AF,Number=A,Type=Float,Description="AF">\n')
        fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for r in uniq:
            chrom = r["chrom"]
            filt = "PASS" if (not r["filters"] or r["filters"] in {".", "PASS", ""}) else r["filters"]
            af = r["af"] if r["af"] is not None else "."
            info = f"AF={af}" if af != "." else "."
            vid = r["variant_id"] or "."
            fh.write(f"{chrom}\t{r['pos']}\t{vid}\t{r['ref']}\t{r['alt']}\t.\t{filt}\t{info}\n")

    print(f"wrote {out_tsv} and {out_vcf} n={len(uniq)}")
    partial.unlink(missing_ok=True)
    progress.unlink(missing_ok=True)
    return out_vcf


def fetch_huddep2_ctcf() -> Path | None:
    DATA.mkdir(parents=True, exist_ok=True)
    raw = DATA / "ctcf_HUDEP2_peaks_raw.bed"
    out = DATA / "ctcf_HUDEP2_peaks.bed"
    if out.exists() and out.stat().st_size > 0:
        print(f"exists: {out}")
        return out

    for url in CHIP_ATLAS_URLS:
        print(f"GET {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DNK-TE3D-pilot/1.0"})
            with urllib.request.urlopen(req, timeout=180) as resp, raw.open("wb") as fh:
                fh.write(resp.read())
            print(f"downloaded {raw.stat().st_size} bytes")
            break
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {exc}")
            raw.unlink(missing_ok=True)
    else:
        return None

    n = 0
    with raw.open(encoding="utf-8", errors="replace") as fin, out.open("w", encoding="utf-8") as fout:
        fout.write("# HUDEP-2 CTCF ChIP-Atlas SRX5821035 (hg38), chr11 slice\n")
        fout.write("# source: GSE131055 / erythropoiesis Day3\n")
        for line in fin:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip().split("\t")
            if len(parts) < 3:
                continue
            chrom = parts[0] if parts[0].startswith("chr") else f"chr{parts[0]}"
            if chrom != "chr11":
                continue
            fout.write(f"{chrom}\t{parts[1]}\t{parts[2]}\tHUDEP2_CTCF\n")
            n += 1
    print(f"HUDEP-2 CTCF chr11 peaks: {n} -> {out}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=5_200_000)
    ap.add_argument("--end", type=int, default=5_300_000)
    ap.add_argument("--chunk", type=int, default=20_000)
    ap.add_argument("--skip-gnomad", action="store_true")
    ap.add_argument("--skip-ctcf", action="store_true")
    args = ap.parse_args()

    if not args.skip_ctcf:
        fetch_huddep2_ctcf()
    if not args.skip_gnomad:
        fetch_gnomad_window("chr11", args.start, args.end, chunk=args.chunk)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
