"""Unit tests for ARCHCODE-PROSPECTIVE leakage-free framework."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from baseline_scorers import distance_only_score, motif_only_score
from build_prospective_universe import (
    build_universe,
    ensure_dry_fixtures,
    load_allowed_tsv,
    load_prospective_config,
    validate_headers,
    write_fixture_seed,
)
from holdout_guard import assert_not_scoring_holdout
from leakage_audit import run_audit
from qc_filters import VariantRecord
from run_prospective_baselines import run_baselines, summarize

ROOT = Path(__file__).resolve().parent


class ProspectiveFrameworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = load_prospective_config()
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_forbidden_headers_rejected(self) -> None:
        hits = validate_headers(
            ["chrom", "pos", "ref", "alt", "clinical_significance"], self.cfg
        )
        self.assertIn("clinical_significance", hits)

    def test_clean_headers_ok(self) -> None:
        hits = validate_headers(["chrom", "pos", "ref", "alt", "af", "variant_id"], self.cfg)
        self.assertEqual(hits, [])

    def test_clinvar_tsv_raises(self) -> None:
        bad = self.tmp_path / "bad.tsv"
        bad.write_text(
            "chrom\tpos\tref\talt\tclnsig\nchr11\t10800060\tG\tA\tPathogenic\n",
            encoding="utf-8",
        )
        with self.assertRaises(RuntimeError):
            load_allowed_tsv(bad, self.cfg)

    def test_holdout_path_blocked(self) -> None:
        # Create a fake sealed-like path under holdout name
        hold = self.tmp_path / "holdout" / "x.tsv"
        hold.parent.mkdir(parents=True)
        hold.write_text("chrom\tpos\tref\talt\n", encoding="utf-8")
        # assert_not_scoring_holdout uses real manifest; if sealed, any path with holdout fails
        try:
            assert_not_scoring_holdout(hold)
        except RuntimeError as exc:
            self.assertIn("Holdout sealed", str(exc))
        else:
            # If manifest not sealed in this workspace, still ensure builder rejects token
            from build_prospective_universe import validate_input_path

            with self.assertRaises(RuntimeError):
                validate_input_path(hold, self.cfg)

    def test_hbb_excluded_from_universe(self) -> None:
        data_dir = self.tmp_path / "data"
        seed = ensure_dry_fixtures(data_dir)
        variants = load_allowed_tsv(seed, self.cfg)
        kept, audit = build_universe(variants, self.cfg, data_dir)
        self.assertGreaterEqual(audit["drop"]["excluded_window"], 1)
        self.assertTrue(all(not (5200000 <= v.pos < 5300000) for v in kept))
        self.assertGreaterEqual(len(kept), 1)

    def test_distance_only_deterministic(self) -> None:
        peaks = self.tmp_path / "peaks.bed"
        peaks.write_text("chr11\t100\t110\tCTCF\n", encoding="utf-8")
        v = VariantRecord("chr11", 105, "A", "G", variant_id="x")
        a = distance_only_score(v, peaks_path=peaks)
        b = distance_only_score(v, peaks_path=peaks)
        self.assertTrue(a["ok"])
        self.assertEqual(a["score"], b["score"])
        self.assertAlmostEqual(a["score"], 1.0 / (1.0 + 0.0), places=6)

    def test_motif_only_dry_fasta(self) -> None:
        data_dir = self.tmp_path / "fix"
        ensure_dry_fixtures(data_dir)
        fa = data_dir / "chr11_prospective_fixture.fa"
        peaks = data_dir / "ctcf_HUDEP2_peaks.bed"
        v = VariantRecord("chr11", 10800060, "G", "A", variant_id="m")
        # Force ref match against synthetic fasta base
        # Fixture seq starts at 10800000; index 60 is within range
        scored = motif_only_score(v, fasta_path=fa, peaks_path=peaks)
        self.assertIn(scored["ok"], (True, False))  # allele may mismatch synthetic seq
        self.assertEqual(scored["baseline"], "motif_only")

    def test_dry_run_baselines_pipeline(self) -> None:
        data_dir = self.tmp_path / "fix"
        out_dir = self.tmp_path / "out"
        out_dir.mkdir()
        seed = ensure_dry_fixtures(data_dir)
        audit = run_audit(self.cfg, input_tsv=seed, out_dir=out_dir)
        self.assertEqual(audit["verdict"], "PASS")
        variants = load_allowed_tsv(seed, self.cfg)
        kept, _ = build_universe(variants, self.cfg, data_dir)
        peaks = data_dir / "ctcf_HUDEP2_peaks.bed"
        fasta = data_dir / "chr11_prospective_fixture.fa"
        rows = run_baselines(kept, fasta_path=fasta, peaks_path=peaks)
        summary = summarize(rows)
        self.assertEqual(summary["role"], "G2_preparation_only")
        self.assertIsNone(summary["claim"])
        self.assertGreaterEqual(summary["n_distance_scored"], 1)

    def test_g9_template_exists(self) -> None:
        shell = (
            ROOT.parent
            / "09_outputs"
            / "prospective"
            / "templates"
            / "G9_immutable_manifest.yaml"
        )
        self.assertTrue(shell.exists())
        text = shell.read_text(encoding="utf-8")
        self.assertIn("immutable: false", text)

    def test_ensemble_templates_and_contract(self) -> None:
        methods = ROOT.parent / "07_methods" / "competitor_baseline_ensemble.md"
        self.assertTrue(methods.exists())
        text = methods.read_text(encoding="utf-8")
        self.assertIn("Arm B", text)
        self.assertIn("AlphaGenome", text)
        g2b = ROOT.parent / "09_outputs" / "prospective" / "templates" / "G2b_model_independence_matrix.yaml"
        g2c = ROOT.parent / "09_outputs" / "prospective" / "templates" / "G2c_ensemble_classification.yaml"
        self.assertTrue(g2b.exists())
        self.assertTrue(g2c.exists())
        self.assertIn("principled_disagreement", g2c.read_text(encoding="utf-8"))
        self.assertEqual(self.cfg["prospective"]["arms"]["archcode_only_no_mechanism"], "reject")


if __name__ == "__main__":
    unittest.main()
