"""Desk PE candidate hunt for C1 A>G at chr11:62753923 (GRCh38).

Heuristic only — not wet-lab ordered guides.
Finds SpCas9 NGG/CCN where the cut is within RTT reach of the edit.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEQ_PATH = ROOT / "pilot_scaffold" / "data" / "cultivation" / "c1_pe_window_161bp.txt"
OUT_MD = ROOT / "09_outputs" / "prospective" / "G5_PE_shortlist_C1_desk_v1.md"
OUT_JSON = ROOT / "09_outputs" / "prospective" / "G5_PE_shortlist_C1_desk_v1.json"

# Window: genomic start of first base
WIN_START = 62_753_923 - 80  # 62753843
EDIT_POS = 62_753_923  # 1-based
EDIT_IDX = EDIT_POS - WIN_START  # 80
REF = "A"
ALT = "G"
MAX_RTT = 30
MIN_PBS = 10
MAX_PBS = 15
SPACER = 20


def revcomp(s: str) -> str:
    t = str.maketrans("ACGTNacgtn", "TGCANtgcan")
    return s.translate(t)[::-1]


def find_candidates(seq: str) -> list[dict]:
    seq = seq.upper()
    assert seq[EDIT_IDX] == REF
    out: list[dict] = []

    # + strand NGG PAMs
    for i in range(SPACER, len(seq) - 2):
        pam = seq[i : i + 3]
        if len(pam) < 3 or pam[1:] != "GG":
            continue
        # cut between idx i-4 and i-3; nick leaves 3' end starting at i-3 for non-target? 
        # Distance from cut (i-3) to edit for +strand install via RT along +strand template:
        cut = i - 3  # 0-based index of first base after cut on target (+ spacer) strand
        # For PE, edit should lie on the flap that is rewritten — commonly edit between cut and ~+RTT
        # Prefer edit downstream of cut on + strand: EDIT_IDX >= cut and EDIT_IDX - cut <= MAX_RTT
        dist = EDIT_IDX - cut
        if not (0 <= dist <= MAX_RTT):
            continue
        spacer = seq[i - SPACER : i]
        # PBS: complementary to region upstream of nick on target strand (typically 10-15 nt of sequence ending at nick)
        # Use seq[cut-MAX_PBS:cut] on +strand; PBS is revcomp of that (binds nicked strand)
        pbs_len = 13
        if cut - pbs_len < 0:
            continue
        pbs_bind = seq[cut - pbs_len : cut]
        pbs = revcomp(pbs_bind)
        # RT template: from cut through edit to a few bases past edit (include ALT)
        rtt_end = min(len(seq), EDIT_IDX + 5)
        rtt_ref = seq[cut:rtt_end]
        # install ALT at relative position EDIT_IDX-cut
        rtt_list = list(rtt_ref)
        rtt_list[EDIT_IDX - cut] = ALT
        rtt = "".join(rtt_list)
        # extension: 3' of pegRNA is PBS then RTT (convention varies; PE typically 5'-spacer-scaffold-RTT-PBS-3')
        # For reporting we give spacer, RTT, PBS separately
        out.append(
            {
                "strand": "+",
                "pam": pam,
                "pam_genomic_start": WIN_START + i,
                "spacer": spacer,
                "cut_genomic": WIN_START + cut + 1,  # 1-based first base after cut approx
                "edit_distance_from_cut_bp": dist,
                "pbs": pbs,
                "rtt": rtt,
                "rtt_len": len(rtt),
                "pbs_len": len(pbs),
                "notes": "desk heuristic; validate in PrimeDesign/Easy-Prime before order",
            }
        )

    # - strand (CCN PAM on + means NGG on -)
    for i in range(0, len(seq) - SPACER - 2):
        pam = seq[i : i + 3]
        if pam[0] != "C" or pam[1] != "C":
            continue
        # On reverse strand, spacer is revcomp of seq[i+3:i+3+20]
        if i + 3 + SPACER > len(seq):
            continue
        spacer = revcomp(seq[i + 3 : i + 3 + SPACER])
        # Cut on - strand: analogous, ~3 bp from PAM into spacer on - strand
        # Approximate genomic cut coordinate near i+3+3 = i+6
        cut = i + 6
        dist = cut - EDIT_IDX  # prefer edit "downstream" of cut on - strand synthesis ≈ upstream on +
        if not (0 <= dist <= MAX_RTT):
            # also allow small window where edit is near cut either side
            dist2 = abs(EDIT_IDX - cut)
            if dist2 > MAX_RTT:
                continue
            dist = dist2
            side = "near"
        else:
            side = "downstream_minus"
        pbs_len = 13
        # construct simple RTT/PBS placeholders from local sequence
        # For - strand PE: build reverse-complement edit into RTT
        # Use local window around edit
        left = max(0, min(EDIT_IDX, cut) - 2)
        right = min(len(seq), max(EDIT_IDX, cut) + 5)
        core = seq[left:right]
        core_list = list(core)
        core_list[EDIT_IDX - left] = ALT
        rtt = revcomp("".join(core_list))[: max(8, dist + 5)]
        pbs = seq[cut : cut + pbs_len] if cut + pbs_len <= len(seq) else ""
        if len(pbs) < MIN_PBS:
            continue
        out.append(
            {
                "strand": "-",
                "pam": pam + "(CCN=+)",
                "pam_genomic_start": WIN_START + i,
                "spacer": spacer,
                "cut_genomic": WIN_START + cut + 1,
                "edit_distance_from_cut_bp": dist,
                "pbs": pbs,
                "rtt": rtt,
                "rtt_len": len(rtt),
                "pbs_len": len(pbs),
                "notes": f"minus-strand heuristic ({side}); lower confidence — validate externally",
            }
        )

    # rank: prefer +strand, shorter edit distance, moderate RTT
    def score(c: dict) -> tuple:
        return (
            0 if c["strand"] == "+" else 1,
            c["edit_distance_from_cut_bp"],
            abs(c["rtt_len"] - 15),
        )

    out.sort(key=score)
    return out


def main() -> None:
    seq = SEQ_PATH.read_text(encoding="utf-8").strip().upper()
    cands = find_candidates(seq)
    top = cands[:8]
    payload = {
        "variant": "chr11:62753923:A:G",
        "genome_build": "GRCh38",
        "window_start": WIN_START,
        "n_candidates": len(cands),
        "top": top,
        "status": "DESK_ONLY_NO_ORDER",
        "wet_lab": "STOPPED",
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# G5 PE shortlist — C1 A>G (desk only)",
        "",
        "**Status:** `DESK_ONLY` · **NO guide ordering** · wet-lab STOPPED  ",
        "**Variant:** `chr11:62753923 A>G` (GRCh38) · AluSz  ",
        "**Method:** local heuristic SpCas9 PE2-style candidates (not PrimeDesign).",
        "",
        "## Decision",
        "",
        "| Item | Result |",
        "|------|--------|",
        "| Classic SpCas9 BE | FAIL (prior desk: pos 17–18) |",
        "| Prime editing | **CONDITIONAL path** — candidates below |",
        "| Wet-lab order | **FORBIDDEN** until panel/MCID freeze |",
        "",
        f"Found **{len(cands)}** PAM geometries with edit within {MAX_RTT} bp of cut; showing top {len(top)}.",
        "",
        "## Top candidates",
        "",
        "| rank | strand | PAM@ | spacer | edit→cut (bp) | PBS | RTT |",
        "|-----:|:------:|-----:|--------|--------------:|-----|-----|",
    ]
    for i, c in enumerate(top, 1):
        lines.append(
            f"| {i} | {c['strand']} | {c['pam_genomic_start']} | `{c['spacer']}` | "
            f"{c['edit_distance_from_cut_bp']} | `{c['pbs']}` | `{c['rtt']}` |"
        )
    lines += [
        "",
        "## Next validation (before any order)",
        "",
        "1. Recompute in PrimeDesign / Easy-Prime / pegLIT  ",
        "2. PE3 nicking sgRNA opposite strand  ",
        "3. Cas-OFFinder / CRISPRitz off-targets for spacer  ",
        "4. Confirm no essential splice disruption outside intended A>G  ",
        "",
        "## Gate linkage",
        "",
        "- Architecture G4b needs this edit verified in HUDEP-2 clones  ",
        "- Activity Branch B can use same PE path for expression readout  ",
        "",
        f"JSON: `{OUT_JSON.name}`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"n": len(cands), "top1": top[0] if top else None}, indent=2))


if __name__ == "__main__":
    main()
