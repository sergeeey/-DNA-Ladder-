#!/usr/bin/env python3
"""C-B1 kill-test: CRE-community topology ΔAUC over redesigned baseline.

Baseline (post rE2G SURVIVES_WITH_REDESIGN):
  log10 genomic distance + activity proxy (cCRE pELS/dELS) + SE membership

Topology (ENCFF693XIL loop graph on CRISPR anchors):
  enhancer loop degree, promoter loop degree, shared community size,
  optional min direct-loop span rank

Primary split: train all chroms except chr20–22; test chr20–22.
Kill if ΔAUC < 0.02; SUPPORT if ≥ 0.05; else INCONCLUSIVE.

Large inputs are fetched under data/input/ (gitignored binaries).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

EXP = Path(__file__).resolve().parent.parent
TRACK = EXP.parent.parent
DATA = EXP / "data" / "input"
RESULTS = EXP / "results"
SE_PATH = TRACK / "data" / "input" / "k562_super_enhancers_grch38.json"

CRISPR_URL = (
    "https://raw.githubusercontent.com/EngreitzLab/ENCODE_rE2G/main/"
    "reference/EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz"
)
CRISPR_SHA256 = "d0806eb8a3cfe71066a9a1c88da2f730ccf5d86364bd52ca9bc6ba628744e417"
HIC_URL = "https://www.encodeproject.org/files/ENCFF693XIL/@@download/ENCFF693XIL.bedpe.gz"
CCRE_URL = "https://www.encodeproject.org/files/ENCFF210CAN/@@download/ENCFF210CAN.bed.gz"

TEST_CHROMS = {"chr20", "chr21", "chr22"}
PROMOTER_FLANK = 2000
LABEL_COL = "Regulated"
LABEL_TRUE = "TRUE"

BASELINE_FEATURES = ["log10_distance", "activity_els", "se_membership"]
TOPOLOGY_FEATURES = [
    "enh_loop_degree",
    "prom_loop_degree",
    "shared_community_size",
    "min_loop_span_rank",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_file(path: Path, url: str, expected_sha: str | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        print(f"Downloading {url} -> {path}", flush=True)
        urllib.request.urlretrieve(url, path)
    if expected_sha is not None:
        got = sha256_file(path)
        if got != expected_sha:
            raise SystemExit(f"SHA-256 mismatch for {path}: {got} != {expected_sha}")
    return path


def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    return a0 < b1 and b0 < a1


def load_se_intervals(path: Path) -> dict[str, list[tuple[int, int]]]:
    data = json.loads(path.read_text())
    by_chrom: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for se in data["super_enhancers"]:
        by_chrom[se["chrom"]].append((int(se["start"]), int(se["end"])))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return dict(by_chrom)


def interval_hits(sorted_ivs: list[tuple[int, int]], start: int, end: int) -> bool:
    """Binary search over sorted non-necessarily-merged intervals."""
    lo, hi = 0, len(sorted_ivs)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_ivs[mid][1] <= start:
            lo = mid + 1
        else:
            hi = mid
    i = lo
    while i < len(sorted_ivs) and sorted_ivs[i][0] < end:
        if overlaps(start, end, sorted_ivs[i][0], sorted_ivs[i][1]):
            return True
        i += 1
    return False


def load_els_intervals(path: Path) -> dict[str, list[tuple[int, int]]]:
    """K562 cCRE bed: keep pELS / dELS as activity proxy."""
    by_chrom: dict[str, list[tuple[int, int]]] = defaultdict(list)
    opener = gzip.open if path.suffix == ".gz" or path.name.endswith(".gz") else open
    with opener(path, "rt") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 10:
                continue
            chrom, start, end, _name = parts[0], int(parts[1]), int(parts[2]), parts[3]
            klass = parts[9]
            if "pELS" in klass or "dELS" in klass:
                by_chrom[chrom].append((start, end))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return dict(by_chrom)


def load_crispr_pairs(path: Path) -> list[dict]:
    rows: list[dict] = []
    with gzip.open(path, "rt") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r.get(LABEL_COL) not in ("TRUE", "FALSE"):
                continue
            chrom = r["chrom"]
            if not chrom.startswith("chr"):
                continue
            if r.get("startTSS") in (None, "", "NA") or r.get("chromStart") in (
                None,
                "",
                "NA",
            ):
                continue
            e0, e1 = int(r["chromStart"]), int(r["chromEnd"])
            tss = int(float(r["startTSS"]))
            mid = (e0 + e1) // 2
            dist = abs(mid - tss)
            rows.append(
                {
                    "chrom": chrom,
                    "enh_start": e0,
                    "enh_end": e1,
                    "tss": tss,
                    "prom_start": max(0, tss - PROMOTER_FLANK),
                    "prom_end": tss + PROMOTER_FLANK,
                    "log10_distance": math.log10(dist + 1.0),
                    "label": 1 if r[LABEL_COL] == LABEL_TRUE else 0,
                    "dataset": r.get("dataset", ""),
                    "pair_uid": r.get("pair_uid", ""),
                    "effect_size": r.get("EffectSize", ""),
                }
            )
    return rows


def load_loops(path: Path) -> list[tuple[str, int, int, str, int, int]]:
    loops: list[tuple[str, int, int, str, int, int]] = []
    with gzip.open(path, "rt") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.split("\t")
            if len(p) < 6:
                continue
            c1, x1, x2, c2, y1, y2 = p[0], int(p[1]), int(p[2]), p[3], int(p[4]), int(p[5])
            if c1 != c2:
                continue  # community graph is intra-chromosomal
            loops.append((c1, x1, x2, c2, y1, y2))
    return loops


class LoopGraph:
    """Per-chromosome undirected loop graph over anchor nodes + degree/community queries."""

    def __init__(self, loops: list[tuple[str, int, int, str, int, int]]):
        self.anchors_by_chrom: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
        # node_id -> list of neighbor node_ids
        self.adj: dict[int, set[int]] = defaultdict(set)
        self.node_chrom: dict[int, str] = {}
        self._next_id = 0
        # For direct E–P spanning loops: list of (x1,x2,y1,y2,span) per chrom
        self.spans_by_chrom: dict[str, list[tuple[int, int, int, int, int]]] = defaultdict(list)

        # Dedup anchors by exact interval key within chrom
        key_to_id: dict[tuple[str, int, int], int] = {}

        def node_for(chrom: str, a: int, b: int) -> int:
            key = (chrom, a, b)
            if key not in key_to_id:
                nid = self._next_id
                self._next_id += 1
                key_to_id[key] = nid
                self.anchors_by_chrom[chrom].append((a, b, nid))
                self.node_chrom[nid] = chrom
            return key_to_id[key]

        for c1, x1, x2, c2, y1, y2 in loops:
            u = node_for(c1, x1, x2)
            v = node_for(c2, y1, y2)
            if u == v:
                continue
            self.adj[u].add(v)
            self.adj[v].add(u)
            span = abs(((y1 + y2) // 2) - ((x1 + x2) // 2))
            self.spans_by_chrom[c1].append((x1, x2, y1, y2, span))

        for chrom in self.anchors_by_chrom:
            self.anchors_by_chrom[chrom].sort()
            self.spans_by_chrom[chrom].sort(key=lambda t: t[4])

        self.component_of, self.component_size = self._connected_components()

    def _connected_components(self) -> tuple[dict[int, int], dict[int, int]]:
        parent: dict[int, int] = {}

        def find(x: int) -> int:
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for u, nbrs in self.adj.items():
            find(u)
            for v in nbrs:
                union(u, v)

        # also include isolated anchors
        for chrom, anchors in self.anchors_by_chrom.items():
            for _, _, nid in anchors:
                find(nid)

        sizes: dict[int, int] = defaultdict(int)
        comp: dict[int, int] = {}
        for nid in parent:
            root = find(nid)
            comp[nid] = root
            sizes[root] += 1
        return comp, dict(sizes)

    def overlapping_nodes(self, chrom: str, start: int, end: int) -> list[int]:
        anchors = self.anchors_by_chrom.get(chrom, [])
        # binary search by start
        lo, hi = 0, len(anchors)
        while lo < hi:
            mid = (lo + hi) // 2
            if anchors[mid][1] <= start:
                lo = mid + 1
            else:
                hi = mid
        out: list[int] = []
        i = lo
        while i < len(anchors) and anchors[i][0] < end:
            a, b, nid = anchors[i]
            if overlaps(start, end, a, b):
                out.append(nid)
            i += 1
        return out

    def degree_of_region(self, chrom: str, start: int, end: int) -> int:
        """Number of unique loop edges incident to anchors overlapping the region."""
        nodes = self.overlapping_nodes(chrom, start, end)
        if not nodes:
            return 0
        node_set = set(nodes)
        edges = 0
        seen_pairs: set[tuple[int, int]] = set()
        for u in nodes:
            for v in self.adj.get(u, ()):
                # count each undirected edge once; allow partner outside region
                a, b = (u, v) if u < v else (v, u)
                if (a, b) in seen_pairs:
                    continue
                seen_pairs.add((a, b))
                edges += 1
        # If both ends of a loop overlap the same region, still one edge — correct.
        _ = node_set
        return edges

    def community_size(self, chrom: str, start: int, end: int) -> int:
        nodes = self.overlapping_nodes(chrom, start, end)
        if not nodes:
            return 0
        return max(self.component_size.get(self.component_of[n], 1) for n in nodes)

    def shared_community_size(
        self, chrom: str, e0: int, e1: int, p0: int, p1: int
    ) -> int:
        e_nodes = self.overlapping_nodes(chrom, e0, e1)
        p_nodes = self.overlapping_nodes(chrom, p0, p1)
        if not e_nodes or not p_nodes:
            return 0
        e_comps = {self.component_of[n] for n in e_nodes}
        p_comps = {self.component_of[n] for n in p_nodes}
        shared = e_comps & p_comps
        if not shared:
            return 0
        return max(self.component_size.get(c, 1) for c in shared)

    def min_loop_span_rank(self, chrom: str, e0: int, e1: int, p0: int, p1: int) -> float:
        """Rank (1=shortest) among chrom loops of the shortest loop spanning E and P.

        If no direct spanning loop, returns n_loops_on_chrom + 1 (worst rank).
        """
        spans = self.spans_by_chrom.get(chrom, [])
        if not spans:
            return 1.0
        best_rank = None
        for rank, (x1, x2, y1, y2, _span) in enumerate(spans, start=1):
            e_hit_x = overlaps(e0, e1, x1, x2)
            e_hit_y = overlaps(e0, e1, y1, y2)
            p_hit_x = overlaps(p0, p1, x1, x2)
            p_hit_y = overlaps(p0, p1, y1, y2)
            if (e_hit_x and p_hit_y) or (e_hit_y and p_hit_x):
                best_rank = rank
                break
        if best_rank is None:
            return float(len(spans) + 1)
        return float(best_rank)


def annotate_features(
    pairs: list[dict],
    se_ivs: dict[str, list[tuple[int, int]]],
    els_ivs: dict[str, list[tuple[int, int]]],
    graph: LoopGraph,
) -> list[dict]:
    out = []
    for r in pairs:
        chrom = r["chrom"]
        e0, e1 = r["enh_start"], r["enh_end"]
        p0, p1 = r["prom_start"], r["prom_end"]
        feat = dict(r)
        feat["activity_els"] = (
            1.0 if interval_hits(els_ivs.get(chrom, []), e0, e1) else 0.0
        )
        feat["se_membership"] = (
            1.0 if interval_hits(se_ivs.get(chrom, []), e0, e1) else 0.0
        )
        feat["enh_loop_degree"] = float(graph.degree_of_region(chrom, e0, e1))
        feat["prom_loop_degree"] = float(graph.degree_of_region(chrom, p0, p1))
        feat["shared_community_size"] = float(
            graph.shared_community_size(chrom, e0, e1, p0, p1)
        )
        feat["min_loop_span_rank"] = float(
            graph.min_loop_span_rank(chrom, e0, e1, p0, p1)
        )
        # invert rank so higher = more topology-supportive (optional scale)
        feat["min_loop_span_rank_inv"] = 1.0 / feat["min_loop_span_rank"]
        out.append(feat)
    return out


def matrix(rows: list[dict], cols: list[str]) -> np.ndarray:
    return np.array([[float(r[c]) for c in cols] for r in rows], dtype=float)


def fit_auc(
    train: list[dict], test: list[dict], cols: list[str]
) -> tuple[float, float | None]:
    y_train = np.array([r["label"] for r in train], dtype=int)
    y_test = np.array([r["label"] for r in test], dtype=int)
    if len(set(y_train.tolist())) < 2 or len(set(y_test.tolist())) < 2:
        return float("nan"), None
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    solver="lbfgs",
                ),
            ),
        ]
    )
    X_train, X_test = matrix(train, cols), matrix(test, cols)
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, proba))
    try:
        auprc = float(average_precision_score(y_test, proba))
    except ValueError:
        auprc = None
    return auc, auprc


def leave_one_chr_mean(rows: list[dict], cols: list[str]) -> dict:
    chroms = sorted({r["chrom"] for r in rows if r["chrom"].startswith("chr")})
    aucs = []
    for hold in chroms:
        train = [r for r in rows if r["chrom"] != hold]
        test = [r for r in rows if r["chrom"] == hold]
        if len(test) < 20:
            continue
        y_test = [r["label"] for r in test]
        if len(set(y_test)) < 2:
            continue
        auc, _ = fit_auc(train, test, cols)
        if not math.isnan(auc):
            aucs.append({"holdout": hold, "n_test": len(test), "auc": auc})
    mean_auc = float(np.mean([a["auc"] for a in aucs])) if aucs else float("nan")
    return {"folds": aucs, "mean_auc": mean_auc, "n_folds": len(aucs)}


def shuffle_null_delta(
    train: list[dict],
    test: list[dict],
    baseline_cols: list[str],
    full_cols: list[str],
    n_perm: int = 20,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    deltas = []
    # Shuffle labels on the combined set consistently, then re-split by chrom
    combined = train + test
    labels = np.array([r["label"] for r in combined], dtype=int)
    for _ in range(n_perm):
        shuffled = labels.copy()
        rng.shuffle(shuffled)
        for r, lab in zip(combined, shuffled):
            r["_shuf"] = int(lab)
        tr = [{**r, "label": r["_shuf"]} for r in train]
        te = [{**r, "label": r["_shuf"]} for r in test]
        # need both classes in train and test
        if len({r["label"] for r in tr}) < 2 or len({r["label"] for r in te}) < 2:
            continue
        auc_b, _ = fit_auc(tr, te, baseline_cols)
        auc_f, _ = fit_auc(tr, te, full_cols)
        if math.isnan(auc_b) or math.isnan(auc_f):
            continue
        deltas.append(auc_f - auc_b)
    return {
        "n_perm": n_perm,
        "n_valid": len(deltas),
        "mean_delta_auc": float(np.mean(deltas)) if deltas else float("nan"),
        "std_delta_auc": float(np.std(deltas)) if deltas else float("nan"),
        "deltas": [float(d) for d in deltas],
    }


def verdict_from_delta(delta: float) -> str:
    if math.isnan(delta):
        return "BLOCKED_PIPELINE"
    if delta < 0.02:
        return "FAIL_KILL"
    if delta >= 0.05:
        return "PASS_KILL"
    return "INCONCLUSIVE"


def run(args: argparse.Namespace) -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    crispr_path = ensure_file(DATA / "EPCrisprBenchmark_ensemble_data_GRCh38.tsv.gz", CRISPR_URL, CRISPR_SHA256)
    hic_path = ensure_file(DATA / "ENCFF693XIL.bedpe.gz", HIC_URL)
    ccre_path = ensure_file(DATA / "ENCFF210CAN.bed.gz", CCRE_URL)

    if not SE_PATH.exists():
        return {
            "status": "BLOCKED_DATA",
            "reason": f"SE calls missing at {SE_PATH}",
        }

    pairs = load_crispr_pairs(crispr_path)
    if not pairs:
        return {"status": "BLOCKED_DATA", "reason": "No usable Regulated labels in CRISPR TSV"}

    se_ivs = load_se_intervals(SE_PATH)
    els_ivs = load_els_intervals(ccre_path)
    loops = load_loops(hic_path)
    graph = LoopGraph(loops)
    feats = annotate_features(pairs, se_ivs, els_ivs, graph)

    # Primary split: hold out chr20–22
    train = [r for r in feats if r["chrom"] not in TEST_CHROMS]
    test = [r for r in feats if r["chrom"] in TEST_CHROMS]

    topology_cols = list(TOPOLOGY_FEATURES)
    # Use inverted rank in the model (higher better); keep raw rank in features for audit
    model_topo = [
        "enh_loop_degree",
        "prom_loop_degree",
        "shared_community_size",
        "min_loop_span_rank_inv",
    ]
    baseline_cols = list(BASELINE_FEATURES)
    full_cols = baseline_cols + model_topo

    auc_base, auprc_base = fit_auc(train, test, baseline_cols)
    auc_full, auprc_full = fit_auc(train, test, full_cols)
    delta = auc_full - auc_base

    # Positive control: distance alone
    auc_dist, _ = fit_auc(train, test, ["log10_distance"])

    # SE-only sensitivity (legacy prereg comparator; not primary)
    auc_se, _ = fit_auc(train, test, ["se_membership"])

    locv_base = leave_one_chr_mean(feats, baseline_cols)
    locv_full = leave_one_chr_mean(feats, full_cols)
    locv_delta = locv_full["mean_auc"] - locv_base["mean_auc"]

    null = shuffle_null_delta(train, test, baseline_cols, full_cols, n_perm=args.n_perm)

    verdict = verdict_from_delta(delta)
    if not math.isnan(auc_dist) and auc_dist <= 0.55:
        distance_note = (
            f"Distance-alone AUC={auc_dist:.4f} ≤ 0.55 — benchmark is hard / "
            "weak distance signal; interpret topology ΔAUC cautiously (not BLOCKED_PIPELINE)."
        )
    else:
        distance_note = f"Distance-alone AUC={auc_dist:.4f} (>0.55 positive-control gate PASS)."

    n_pos_test = sum(r["label"] for r in test)
    n_pos_train = sum(r["label"] for r in train)

    payload = {
        "experiment": "exp_topology_community_crispr_eg",
        "candidate_id": "C-B1",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "status": verdict,
        "estimand_redesign": (
            "ΔAUC of baseline+topology vs baseline=log10_distance+activity_els+se_membership; "
            "NOT novelty for any 3D contact (rE2G already has contact/loops)."
        ),
        "label": {
            "column": LABEL_COL,
            "positive": LABEL_TRUE,
            "note": (
                "Frozen EngreitzLab ensemble binary Regulated flag "
                "(not a post-hoc |EffectSize|≥0.1 rethreshold)."
            ),
        },
        "inputs": {
            "crispr": {
                "path": str(crispr_path),
                "sha256": CRISPR_SHA256,
                "n_pairs_usable": len(feats),
            },
            "hic_loops": {
                "accession": "ENCFF693XIL",
                "n_intrachrom_loops": len(loops),
            },
            "ccre_activity": {
                "accession": "ENCFF210CAN",
                "proxy": "binary overlap with pELS or dELS",
            },
            "se": {
                "path": str(SE_PATH),
                "source": "dbSUPER K562 lifted GRCh38",
            },
        },
        "features": {
            "baseline": baseline_cols,
            "topology_model": model_topo,
            "topology_raw_also_computed": topology_cols,
        },
        "split": {
            "protocol": "chromosome_holdout_chr20_21_22",
            "test_chroms": sorted(TEST_CHROMS),
            "n_train": len(train),
            "n_test": len(test),
            "n_pos_train": n_pos_train,
            "n_pos_test": n_pos_test,
        },
        "primary": {
            "auc_baseline": auc_base,
            "auc_baseline_plus_topology": auc_full,
            "delta_auc": delta,
            "auprc_baseline": auprc_base,
            "auprc_baseline_plus_topology": auprc_full,
            "kill_threshold": 0.02,
            "support_threshold": 0.05,
            "verdict": verdict,
        },
        "positive_control_distance": {
            "auc": auc_dist,
            "gate": ">0.55 preferred",
            "note": distance_note,
        },
        "sensitivity_se_only_auc": auc_se,
        "leave_one_chr_cv": {
            "baseline_mean_auc": locv_base["mean_auc"],
            "full_mean_auc": locv_full["mean_auc"],
            "delta_mean_auc": locv_delta,
            "n_folds_baseline": locv_base["n_folds"],
            "n_folds_full": locv_full["n_folds"],
        },
        "shuffle_label_null": null,
        "feature_prevalence": {
            "activity_els_frac": float(np.mean([r["activity_els"] for r in feats])),
            "se_membership_frac": float(np.mean([r["se_membership"] for r in feats])),
            "mean_enh_loop_degree": float(np.mean([r["enh_loop_degree"] for r in feats])),
            "mean_prom_loop_degree": float(np.mean([r["prom_loop_degree"] for r in feats])),
            "frac_shared_community_gt0": float(
                np.mean([r["shared_community_size"] > 0 for r in feats])
            ),
        },
    }

    out_json = RESULTS / "kill_test_chr_holdout.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    md = RESULTS / "kill_test_chr_holdout.md"
    md.write_text(
        "\n".join(
            [
                "# Kill-test — chromosome holdout (C-B1)",
                "",
                f"**Run (UTC):** {payload['run_utc']}",
                f"**Verdict:** `{verdict}`",
                "",
                "## Estimand (redesigned after rE2G audit)",
                "",
                payload["estimand_redesign"],
                "",
                f"- **Label:** `{LABEL_COL}=={LABEL_TRUE}` (ensemble CRISPR benchmark)",
                f"- **Train:** all chroms except {sorted(TEST_CHROMS)} (n={len(train)}, "
                f"pos={n_pos_train})",
                f"- **Test:** {sorted(TEST_CHROMS)} (n={len(test)}, pos={n_pos_test})",
                "",
                "## Primary metric",
                "",
                f"| Model | ROC-AUC | AUPRC |",
                f"|-------|---------|-------|",
                f"| Baseline (log10_dist + ELS + SE) | {auc_base:.4f} | {auprc_base} |",
                f"| Baseline + topology | {auc_full:.4f} | {auprc_full} |",
                f"| **ΔAUC** | **{delta:.4f}** | — |",
                "",
                f"- Kill if ΔAUC < 0.02 → FAIL_KILL / REJECT",
                f"- SUPPORT if ΔAUC ≥ 0.05 → PASS_KILL",
                f"- else INCONCLUSIVE",
                "",
                "## Controls",
                "",
                f"- Distance alone AUC: **{auc_dist:.4f}** — {distance_note}",
                f"- SE-only AUC (sensitivity): {auc_se:.4f}",
                f"- Leave-one-chr mean ΔAUC: {locv_delta:.4f}",
                f"- Shuffle-label null mean ΔAUC: {null['mean_delta_auc']:.4f} "
                f"(std {null['std_delta_auc']:.4f}, n_valid={null['n_valid']})",
                "",
                "## Feature prevalence",
                "",
                json.dumps(payload["feature_prevalence"], indent=2),
                "",
                "## What this does NOT mean",
                "",
                "1. Not a claim that 3D contact/loops are novel for E–G prediction (rE2G).",
                "2. Not causal CRE-community → regulation.",
                "3. Beating this baseline is not beating full ENCODE-rE2G.",
                "4. Does not reopen closed SE enrichment nulls or TE C-A1.",
                "",
            ]
        )
        + "\n"
    )
    print(json.dumps({"verdict": verdict, "delta_auc": delta, "auc_dist": auc_dist}, indent=2))
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=20)
    args = ap.parse_args()
    payload = run(args)
    if payload.get("status") == "BLOCKED_DATA":
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS / "kill_test_chr_holdout.json").write_text(
            json.dumps(payload, indent=2) + "\n"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
