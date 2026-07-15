"""AlphaGenome contact / TF delta scoring helpers.

Auth: ALPHAGENOME_API_KEY from env or project .env (gitignored).
Never score sealed holdout paths.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import numpy as np

# pilot_scaffold on path when imported as adapters.ag_contact_delta
import sys
from pathlib import Path as _Path

_PS = _Path(__file__).resolve().parents[1]
if str(_PS) not in sys.path:
    sys.path.insert(0, str(_PS))

from load_project_env import alphagenome_api_key, load_project_env


@dataclass(frozen=True)
class VariantSpec:
    chrom: str
    pos: int
    ref: str
    alt: str

    @property
    def variant_id(self) -> str:
        return f"{self.chrom}:{self.pos}:{self.ref}:{self.alt}"


def _require_key() -> str:
    load_project_env()
    key = alphagenome_api_key()
    if not key:
        raise RuntimeError("Set ALPHAGENOME_API_KEY in .env or environment before scoring")
    return key


def score_variant_deltas(
    variant: VariantSpec,
    *,
    sequence_length_key: str = "SEQUENCE_LENGTH_100KB",
) -> dict[str, Any]:
    """Return numeric REF→ALT deltas for CONTACT_MAPS and CHIP_TF."""
    from alphagenome.data import genome
    from alphagenome.models import dna_client

    model = dna_client.create(_require_key())
    width = getattr(dna_client, sequence_length_key)
    gv = genome.Variant(
        chromosome=variant.chrom,
        position=variant.pos,
        reference_bases=variant.ref,
        alternate_bases=variant.alt,
    )
    interval = gv.reference_interval.resize(width)
    out = model.predict_variant(
        interval=interval,
        variant=gv,
        ontology_terms=None,
        requested_outputs=[
            dna_client.OutputType.CONTACT_MAPS,
            dna_client.OutputType.CHIP_TF,
        ],
    )

    ref_cm = np.asarray(out.reference.contact_maps.values, dtype=np.float64)
    alt_cm = np.asarray(out.alternate.contact_maps.values, dtype=np.float64)
    cm_diff = alt_cm - ref_cm
    # Prefer hematopoietic-proximal channels when present (K562 absent in AG tracks).
    md = out.reference.contact_maps.metadata
    names = [str(x) for x in md["biosample_name"].tolist()]
    prefer = {"GM12878", "KBM-7", "IMR-90", "HCT116"}
    idxs = [i for i, n in enumerate(names) if n in prefer]
    if idxs:
        cm_pref = cm_diff[:, :, idxs]
        contact_mae_pref = float(np.mean(np.abs(cm_pref)))
        contact_fro_pref = float(np.linalg.norm(cm_pref))
    else:
        contact_mae_pref = float("nan")
        contact_fro_pref = float("nan")

    ref_tf = np.asarray(out.reference.chip_tf.values, dtype=np.float64)
    alt_tf = np.asarray(out.alternate.chip_tf.values, dtype=np.float64)
    tf_diff = alt_tf - ref_tf

    return {
        "variant_id": variant.variant_id,
        "chrom": variant.chrom,
        "pos": variant.pos,
        "ref": variant.ref,
        "alt": variant.alt,
        "interval_width_bp": int(interval.end - interval.start),
        "contact_mae_all": float(np.mean(np.abs(cm_diff))),
        "contact_fro_all": float(np.linalg.norm(cm_diff)),
        "contact_mae_heme_proxy": contact_mae_pref,
        "contact_fro_heme_proxy": contact_fro_pref,
        "chip_tf_mae": float(np.mean(np.abs(tf_diff))),
        "chip_tf_fro": float(np.linalg.norm(tf_diff)),
        "primary_score": float(np.mean(np.abs(cm_diff))),  # higher = more contact change
        "biosample_channels": names,
        "scorer": "alphagenome_contact_tf_delta_v0.1",
        "confirmatory": False,
        "scored_holdout": False,
    }
