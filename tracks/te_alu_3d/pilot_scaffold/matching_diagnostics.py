"""Matching / effective-N diagnostics (scientific freeze v1)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from build_matched_controls import AnnotatedVariant, _vid


def _te_instance_key(a: AnnotatedVariant) -> str:
    # Approximate TE copy id from family+subfamily+10kb block
    block = (a.variant.pos // 10_000) * 10_000
    return f"{a.variant.chrom}:{block}:{a.te_family_norm}:{a.te_subfamily}"


def _peak_bin(dist: int, bin_size: int = 500) -> int:
    if dist >= 10**8:
        return -1
    return dist // bin_size


def matching_diagnostics(
    test_ann: list[AnnotatedVariant],
    pairs: list[tuple[AnnotatedVariant, list[AnnotatedVariant]]],
    *,
    estimand: str,
    n_requested: int,
) -> dict[str, Any]:
    test_ids = [_vid(t.variant) for t in test_ann]
    te_copies = {_te_instance_key(t) for t in test_ann}
    peak_bins = {_peak_bin(t.dist_ctcf) for t in test_ann}
    blocks = {(t.variant.chrom, (t.variant.pos // 10_000) * 10_000) for t in test_ann}

    n_matched = sum(1 for _, cs in pairs if cs)
    n_full = sum(1 for _, cs in pairs if len(cs) >= n_requested)
    control_ids = [_vid(c.variant) for _, cs in pairs for c in cs]
    reuse = Counter(control_ids)
    reused = sum(1 for _id, n in reuse.items() if n > 1)

    tiers = Counter()
    # tiers logged externally; here report set sizes
    ctrl_per_set = [len(cs) for _, cs in pairs]

    # Effective N approximations (Kish-like on TE copies)
    n_var = len(test_ann)
    n_te = max(len(te_copies), 1)
    n_peak = max(len(peak_bins), 1)
    n_block = max(len(blocks), 1)

    return {
        "estimand": estimand,
        "unique_variants": n_var,
        "unique_TE_copies_approx": len(te_copies),
        "unique_CTCF_distance_bins": len(peak_bins),
        "unique_10kb_blocks": len(blocks),
        "unique_matched_sets": n_matched,
        "fraction_with_any_match": n_matched / max(n_var, 1),
        "fraction_full_k_match": n_full / max(n_var, 1),
        "n_requested_controls": n_requested,
        "control_assignments": len(control_ids),
        "unique_controls": len(reuse),
        "controls_reused": reused,
        "max_control_reuse": max(reuse.values()) if reuse else 0,
        "mean_controls_per_set": (sum(ctrl_per_set) / len(ctrl_per_set)) if ctrl_per_set else 0,
        "effective_n_TE_copies": n_te,
        "effective_n_blocks": n_block,
        "effective_n_peak_bins": n_peak,
        "inflation_variants_over_TE_copies": n_var / n_te,
        "note": "TE_copy id is approx (family+subfamily+10kb); replace with RM interval id when available",
        "test_variant_ids_head": test_ids[:5],
    }


def write_diagnostics(diag: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(diag, indent=2), encoding="utf-8")
