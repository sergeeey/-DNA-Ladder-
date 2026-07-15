"""Chr11 pilot orchestrator — redesign v2 (dual estimand + block perm).

Usage:
  python run_pilot.py --dry-run
  python run_pilot.py --n-perm 2000
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any

from matching_diagnostics import matching_diagnostics, write_diagnostics
from build_matched_controls import (
    AnnotatedVariant,
    balance_for_pairs,
    build_control_pool,
    match_controls_for_estimand,
    match_controls_same_family,
    match_controls_same_subfamily,
    resolve_ctcf_bed,
    write_manifest,
    annotate,
)
from compute_disruption_scores import score_variant, write_scores
from permutation_test import (
    block_permutation_null,
    evaluate_kc0,
    evaluate_kill_criteria,
    load_score_freeze,
    permutation_null,
)
from qc_filters import (
    VariantRecord,
    apply_qc,
    assign_track,
    dry_run_variants,
    load_config,
    write_dry_run_fixtures,
)
from vcf_loader import load_gnomad_rare, load_variant_tsv

ROOT = Path(__file__).resolve().parent


def _vid(v: VariantRecord) -> str:
    return v.variant_id or f"{v.chrom}:{v.pos}:{v.ref}:{v.alt}"


def _resolve_data(cfg: dict[str, Any]) -> Path:
    return ROOT / cfg["paths"]["data_dir"]


def _resolve_out(cfg: dict[str, Any]) -> Path:
    return (ROOT / cfg["outputs"]["base_dir"]).resolve()


def load_test_and_pool(
    cfg: dict[str, Any],
    data_dir: Path,
) -> tuple[list[VariantRecord], list[VariantRecord], dict[str, Any]]:
    meta: dict[str, Any] = {"sources": []}
    chrom = cfg["pilot"]["chromosome"]
    window = cfg["pilot"].get("genomic_window") or {}
    clinvar = data_dir / "clinvar_chr11.vcf.gz"
    if not clinvar.exists():
        clinvar = data_dir / "clinvar_chr11.vcf"
    gnomad = data_dir / "gnomad_chr11.vcf.gz"
    if not gnomad.exists():
        gnomad = data_dir / "gnomad_hbb_window.vcf.gz"

    test: list[VariantRecord] = []
    pool: list[VariantRecord] = []

    def in_window(v: VariantRecord) -> bool:
        if not window or not window.get("start"):
            return True
        return (
            v.chrom == window.get("chrom", chrom)
            and int(window["start"]) <= v.pos < int(window["end"])
        )

    if clinvar.exists():
        allowed = cfg["variant_sets"]["test_clinvar"]["clinical_significance"]
        from vcf_loader import _clin_sig_ok, iter_vcf_variants

        for v in iter_vcf_variants(clinvar, chrom_filter=chrom, source="clinvar"):
            if not in_window(v):
                continue
            if _clin_sig_ok(v.clinical_significance, allowed):
                test.append(v)
            else:
                pool.append(v)
        meta["sources"].append(f"clinvar_plp:{len(test)}")
        meta["sources"].append(f"clinvar_pool:{len(pool)}")
    elif (data_dir / "test_variants.tsv").exists():
        test = [
            v
            for v in load_variant_tsv(data_dir / "test_variants.tsv", source="tsv")
            if in_window(v)
        ]
        meta["sources"].append(f"tsv_test:{len(test)}")

    if gnomad.exists():
        max_af = cfg["variant_sets"]["test_gnomad_rare"]["max_af"]
        for v in load_gnomad_rare(gnomad, chrom=chrom, max_af=max_af):
            if in_window(v):
                test.append(v)
        for v in load_gnomad_rare(gnomad, chrom=chrom, max_af=1.0, pass_only=True):
            if in_window(v):
                pool.append(v)
        meta["sources"].append(f"gnomad:{gnomad.name}")
    elif (data_dir / "control_pool.tsv").exists():
        pool.extend(
            v
            for v in load_variant_tsv(data_dir / "control_pool.tsv", source="tsv")
            if in_window(v)
        )
        meta["sources"].append(f"tsv_pool:{len(pool)}")

    if window and window.get("start"):
        meta["window"] = (
            f"{window.get('label', '')}:{window['chrom']}:{window['start']}-{window['end']}"
        )

    max_pool = int(cfg.get("pilot", {}).get("max_pool_size", 5000))
    if len(pool) > max_pool:
        rng = random.Random(cfg["pilot"]["random_seed"])
        pool = rng.sample(pool, max_pool)
        meta["pool_capped"] = max_pool

    if not test and not pool:
        raise FileNotFoundError(
            "No inputs found. Run: python fetch_chr11_inputs.py "
            "or place clinvar_chr11.vcf.gz under data/"
        )
    return test, pool, meta


def _run_estimand(
    *,
    estimand: str,
    test_ann: list[AnnotatedVariant],
    pool_a: list[AnnotatedVariant],
    pool_b: list[AnnotatedVariant],
    cfg: dict[str, Any],
    rng: random.Random,
    out_dir: Path,
    work_dir: Path,
    audit_test: dict[str, Any],
    kc0: dict[str, Any],
    freeze: dict[str, Any],
    used_fallback: bool,
    n_perm: int,
    clinvar_only: bool,
) -> dict[str, Any]:
    pairs_a: list[tuple[AnnotatedVariant, list[AnnotatedVariant]]] = []
    manifest_rows: list[dict[str, Any]] = []
    undermatched = 0

    for t in test_ann:
        chosen, tier = match_controls_for_estimand(
            t, pool_a, cfg, rng, estimand  # type: ignore[arg-type]
        )
        if len(chosen) < cfg["qc_gates"]["gate_5_matched_controls"]["n_per_variant"]:
            undermatched += 1
        pairs_a.append((t, chosen))
        manifest_rows.append(
            {
                "estimand": estimand,
                "test_variant_id": _vid(t.variant),
                "control_ids": ";".join(_vid(c.variant) for c in chosen),
                "match_tier": tier,
                "n_controls": len(chosen),
                "control_level": "A",
                "track": t.variant.track,
            }
        )

        # Control B diagnostic (same family) — may be empty
        if pool_b:
            b_chosen, b_tier = match_controls_same_family(
                t, pool_b, cfg, rng, estimand  # type: ignore[arg-type]
            )
            if b_chosen:
                manifest_rows.append(
                    {
                        "estimand": estimand,
                        "test_variant_id": _vid(t.variant),
                        "control_ids": ";".join(_vid(c.variant) for c in b_chosen),
                        "match_tier": b_tier,
                        "n_controls": len(b_chosen),
                        "control_level": "B",
                        "track": t.variant.track,
                    }
                )
            c_chosen, c_tier = match_controls_same_subfamily(
                t, pool_b, cfg, rng, estimand  # type: ignore[arg-type]
            )
            if c_chosen:
                manifest_rows.append(
                    {
                        "estimand": estimand,
                        "test_variant_id": _vid(t.variant),
                        "control_ids": ";".join(_vid(c.variant) for c in c_chosen),
                        "match_tier": c_tier,
                        "n_controls": len(c_chosen),
                        "control_level": "C",
                        "track": t.variant.track,
                    }
                )

    write_manifest(manifest_rows, out_dir / f"control_manifest_{estimand}.csv")
    balance = balance_for_pairs(test_ann, pairs_a)
    (out_dir / f"balance_table_{estimand}.csv").write_text(
        "metric,value\n" + "\n".join(f"{k},{v}" for k, v in balance.items()) + "\n",
        encoding="utf-8",
    )
    n_req = cfg["qc_gates"]["gate_5_matched_controls"]["n_per_variant"]
    diag = matching_diagnostics(test_ann, pairs_a, estimand=estimand, n_requested=n_req)
    diag["balance"] = balance
    write_diagnostics(diag, out_dir / f"matching_diagnostics_{estimand}.json")
    (out_dir / f"undermatched_{estimand}.json").write_text(
        json.dumps({"undermatched_n": undermatched, "n_test": len(test_ann)}, indent=2),
        encoding="utf-8",
    )

    # Scores for Control A matched sets
    score_cache: dict[str, float] = {}

    def sc(v: VariantRecord) -> float:
        vid = _vid(v)
        if vid not in score_cache:
            score_cache[vid] = float(score_variant(v, cfg, data_dir=work_dir)["score"])
        return score_cache[vid]

    matched_sets: list[tuple[float, list[float]]] = []
    score_rows: list[dict[str, Any]] = []
    for t, chosen in pairs_a:
        te_s = sc(t.variant)
        ctrl_s = [sc(c.variant) for c in chosen]
        matched_sets.append((te_s, ctrl_s))
        row = score_variant(t.variant, cfg, data_dir=work_dir)
        row["estimand"] = estimand
        row["role"] = "test"
        score_rows.append(row)
        for c in chosen:
            crow = score_variant(c.variant, cfg, data_dir=work_dir)
            crow["estimand"] = estimand
            crow["role"] = "control_A"
            score_rows.append(crow)

    write_scores(score_rows, out_dir / f"disruption_scores_{estimand}.csv")

    perm_n = min(n_perm, 10000)
    primary = block_permutation_null(matched_sets, n_perm=perm_n, rng=rng)
    te_flat = [s[0] for s in matched_sets]
    ctrl_flat = [c for _, cs in matched_sets for c in cs]
    software = permutation_null(te_flat, ctrl_flat or te_flat, n_perm=min(perm_n, 500), rng=rng)

    kill = evaluate_kill_criteria(
        primary,
        cfg,
        audit_test,
        estimand=estimand,
        kc0=kc0,
        score_freeze=freeze,
        used_fallback=used_fallback,
    )
    kill["KC3"] = {
        "triggered": clinvar_only,
        "reason": "clinvar_only_without_gnomad" if clinvar_only else "dual_or_gnomad_present",
        "action": "exploratory_only" if clinvar_only else "continue",
    }

    perm_out = {
        "estimand": estimand,
        "primary_block": primary,
        "software_global": software,
    }
    (out_dir / f"permutation_results_{estimand}.json").write_text(
        json.dumps(perm_out, indent=2), encoding="utf-8"
    )
    (out_dir / f"kill_criteria_status_{estimand}.json").write_text(
        json.dumps(kill, indent=2), encoding="utf-8"
    )

    # Enrichment: only if perm gate passes; still exploratory if KC0/freeze/fallback/KC3
    summary_dir = out_dir / "exploratory"
    if kill.get("confirmatory_gate", {}).get("passed") and not clinvar_only:
        summary_dir = out_dir / "confirmatory"
    summary_dir.mkdir(exist_ok=True)
    summary_path = summary_dir / f"enrichment_summary_{estimand}.csv"

    if kill["permutation_gate"]["passed"]:
        with summary_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["metric", "value"])
            w.writerow(["note", "pilot_only_not_biology"])
            w.writerow(["estimand", estimand])
            w.writerow(["median_delta", primary.get("observed_effect_median_delta")])
            w.writerow(["delta_MAD", primary.get("observed_delta_MAD")])
            w.writerow(["perm_p_block", primary.get("perm_p")])
            w.writerow(["confirmatory_gate", kill["confirmatory_gate"]["passed"]])
    else:
        summary_path.write_text(
            f"metric,value\nestimand,{estimand}\nstatus,BLOCKED_BY_PERMUTATION_GATE\n",
            encoding="utf-8",
        )

    return {
        "estimand": estimand,
        "balance": balance,
        "diagnostics": diag,
        "undermatched": undermatched,
        "permutation": primary,
        "kill_criteria": kill,
        "n_sets": primary.get("n_sets"),
    }


def run_pipeline(cfg: dict[str, Any], dry: bool, n_perm: int | None) -> dict[str, Any]:
    data_dir = _resolve_data(cfg)
    out_dir = _resolve_out(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "confirmatory").mkdir(exist_ok=True)
    (out_dir / "exploratory").mkdir(exist_ok=True)
    rng = random.Random(cfg["pilot"]["random_seed"])
    n_perm = n_perm or cfg["qc_gates"]["gate_6_permutation"]["n_perm"]

    kc0 = evaluate_kc0(cfg)
    freeze = load_score_freeze(ROOT / "score_freeze.yaml")
    used_fallback = not bool((cfg.get("scoring") or {}).get("archcode", {}).get("binary_path"))

    if dry:
        dry_dir = data_dir / "dry_run"
        write_dry_run_fixtures(dry_dir)
        (dry_dir / "ctcf_GM12878_peaks.bed").write_text(
            "chr11\t5226900\t5226950\tCTCF_peak\nchr11\t10800000\t10800080\tCTCF_peak\n",
            encoding="utf-8",
        )
        (dry_dir / "gencode_v46_protein_coding_TSS_chr11.bed").write_text(
            "chr11\t5226000\t5226010\tHBB\t-\n",
            encoding="utf-8",
        )
        work_dir = dry_dir
        raw_test = dry_run_variants()
        for v in raw_test:
            if v.pos in {5227000, 17400000}:
                v.te_family = "SINE/Alu"
        raw_pool = dry_run_variants() + [
            VariantRecord("chr11", 5227200, "A", "G", source="gnomad", af=0.001),
            VariantRecord("chr11", 5227300, "G", "C", source="gnomad", af=0.002),
            VariantRecord("chr11", 5227400, "T", "A", source="gnomad", af=0.003),
            VariantRecord("chr11", 5227500, "C", "G", source="gnomad", af=0.004),
            VariantRecord("chr11", 17400200, "A", "C", source="gnomad", af=0.001),
        ]
        meta = {"sources": ["dry_run"], "mode": "dry_run"}
    else:
        work_dir = data_dir
        raw_test, raw_pool, meta = load_test_and_pool(cfg, data_dir)
        meta["mode"] = "real"

    test_qc, audit_test = apply_qc(raw_test, cfg, work_dir, role="test")
    pool_qc, audit_pool = apply_qc(raw_pool, cfg, work_dir, role="pool")
    # TE-overlapping non-test for Control B: from raw_pool before TE exclusion
    # Re-annotate TE membership without failing pool on TE
    te_pool_raw: list[VariantRecord] = []
    for v in raw_pool + raw_test:
        # mark TE via apply on copy role test-like detection: use bed via annotate after soft flag
        te_pool_raw.append(v)

    assign_track(test_qc, cfg)
    for v in test_qc:
        if kc0.get("flags"):
            # exploratory flag for cell-type mismatch
            if v.track == "confirmatory":
                v.track = "exploratory"

    qc_report = {
        "meta": meta,
        "test_audit": audit_test,
        "pool_audit": audit_pool,
        "kc0": kc0,
        "score_freeze_status": freeze.get("status"),
        "used_fallback_scorer": used_fallback,
        "redesign_version": cfg.get("pilot", {}).get("redesign_version", "v2"),
        "passed_test": [v.to_dict() for v in test_qc],
        "kill_first": True,
    }
    (out_dir / "qc_dropout_report.json").write_text(
        json.dumps(qc_report, indent=2), encoding="utf-8"
    )

    if len(test_qc) < 2:
        kill = {
            "KC0": kc0,
            "KC1": {"triggered": True, "reason": f"n_test={len(test_qc)} < 2", "action": "STOP"},
            "permutation_gate": {"passed": False, "message": "insufficient_test_variants"},
        }
        (out_dir / "kill_criteria_status.json").write_text(json.dumps(kill, indent=2), encoding="utf-8")
        (out_dir / "exploratory" / "enrichment_summary.csv").write_text(
            "metric,value\nstatus,BLOCKED_INSUFFICIENT_N\n", encoding="utf-8"
        )
        return {"status": "killed", "reason": "insufficient_n", "audit": audit_test, "kc0": kc0}

    ctcf = resolve_ctcf_bed(cfg, work_dir)
    tss = work_dir / "gencode_v46_protein_coding_TSS_chr11.bed"
    meta_ctcf = {"ctcf_bed": str(ctcf.name)}
    test_ann = [annotate(v, work_dir, ctcf, tss) for v in test_qc]
    pool_a = build_control_pool(pool_qc, work_dir, require_non_te=True, ctcf_bed=ctcf, tss_bed=tss)

    # Control B pool: TE-overlapping variants not in test set
    test_ids = {_vid(v) for v in test_qc}
    # Soft TE detect via repeat bed through annotate + apply_qc role unused:
    # build from raw variants that fail non-TE pool filter but pass hard QC gates
    from qc_filters import _load_te_index, _te_overlap_indexed

    te_bed = work_dir / "repeatmasker_chr11_alu_sva.bed"
    if not te_bed.exists():
        te_bed = work_dir / "repeatmasker_chr11.bed"
    te_index = _load_te_index(te_bed, set(cfg["te_focus"]["families"]))
    te_family_pool_vars: list[VariantRecord] = []
    for v in te_pool_raw:
        if _vid(v) in test_ids:
            continue
        overlap, fam = _te_overlap_indexed(v.chrom, v.pos, te_index)
        if overlap:
            v.te_overlap = True
            v.te_family = fam
            te_family_pool_vars.append(v)
    pool_b = build_control_pool(
        te_family_pool_vars, work_dir, require_non_te=False, ctcf_bed=ctcf, tss_bed=tss
    )

    clinvar_only = all(v.source == "clinvar" for v in test_qc) and not any(
        (data_dir / f).exists()
        for f in ("gnomad_chr11.vcf.gz", "gnomad_hbb_window.vcf.gz", "gnomad_hbb_window.tsv")
    )

    results: dict[str, Any] = {}
    for estimand in ("T", "C"):
        results[estimand] = _run_estimand(
            estimand=estimand,
            test_ann=test_ann,
            pool_a=pool_a,
            pool_b=pool_b,
            cfg=cfg,
            rng=rng,
            out_dir=out_dir,
            work_dir=work_dir,
            audit_test=audit_test,
            kc0=kc0,
            freeze=freeze,
            used_fallback=used_fallback,
            n_perm=n_perm,
            clinvar_only=clinvar_only,
        )

    # Combined kill status
    combined = {
        "KC0": kc0,
        "score_freeze": {"status": freeze.get("status"), "used_fallback": used_fallback},
        "estimands": {e: results[e]["kill_criteria"] for e in results},
        "rule": "report T and C separately; loss of C does not auto-kill T",
    }
    (out_dir / "kill_criteria_status.json").write_text(
        json.dumps(combined, indent=2), encoding="utf-8"
    )
    (out_dir / "permutation_results.json").write_text(
        json.dumps({e: results[e]["permutation"] for e in results}, indent=2),
        encoding="utf-8",
    )

    any_perm = any(results[e]["kill_criteria"]["permutation_gate"]["passed"] for e in results)
    (out_dir / "variant_counts.json").write_text(
        json.dumps(
            {
                "raw_test": len(raw_test),
                "raw_pool": len(raw_pool),
                "qc_test": len(test_qc),
                "qc_pool_A": len(pool_a),
                "qc_pool_B": len(pool_b),
                "meta": {**meta, **meta_ctcf},
                "kc0": kc0,
                "estimands": {e: {"balance": results[e]["balance"], "n_sets": results[e]["n_sets"]} for e in results},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "status": "ok" if any_perm else "killed_or_blocked",
        "kc0": kc0,
        "score_freeze_status": freeze.get("status"),
        "used_fallback": used_fallback,
        "estimands": results,
        "n_test": len(test_qc),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Chr11 kill-first pilot (redesign v2)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--n-perm", type=int, default=None)
    args = ap.parse_args()
    cfg = load_config()
    try:
        result = run_pipeline(cfg, dry=args.dry_run, n_perm=args.n_perm)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
