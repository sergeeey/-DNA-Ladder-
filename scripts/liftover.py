"""Minimal UCSC chain-file liftOver implementation (stdlib only, no pyliftover
dependency). Lifts single genomic coordinates from one assembly to another
using a standard UCSC .chain file (e.g. hg19ToHg38.over.chain.gz -- real,
public, from hgdownload.soe.ucsc.edu). For interval liftover, the start and
end coordinates are lifted independently (each via the chain block that
contains it) -- a standard, defensible approximation for approximate region
classification, NOT base-pair-exact for intervals spanning a chain gap.
This limitation is intentional and documented, not silently assumed away.
"""

import gzip
import io
from collections import defaultdict


class Chain:
    __slots__ = ("t_start", "t_end", "q_start", "q_strand", "q_size", "blocks")

    def __init__(self, t_start, t_end, q_start, q_strand, q_size, blocks):
        self.t_start = t_start
        self.t_end = t_end
        self.q_start = q_start
        self.q_strand = q_strand
        self.q_size = q_size
        self.blocks = blocks  # list of (t_block_start, t_block_end, q_block_start)


def load_chain_file(raw_gz_bytes: bytes) -> dict:
    """Returns {t_chrom: [Chain, ...]} sorted by t_start."""
    chains_by_chrom = defaultdict(list)
    with gzip.open(io.BytesIO(raw_gz_bytes), "rt") as f:
        header = None
        blocks = []
        t_pos = q_pos = 0
        t_chrom = q_strand = q_size = t_start = q_start = None

        def flush():
            if header is None:
                return
            chains_by_chrom[t_chrom].append(
                Chain(t_start, header_t_end, q_start, q_strand, q_size, blocks[:])
            )

        header_t_end = None
        for line in f:
            line = line.strip()
            if not line:
                if header is not None:
                    flush()
                    header = None
                    blocks = []
                continue
            if line.startswith("chain"):
                parts = line.split()
                # chain score tName tSize tStrand tStart tEnd qName qSize qStrand qStart qEnd id
                t_chrom = parts[2]
                t_start = int(parts[5])
                header_t_end = int(parts[6])
                q_size = int(parts[8])
                q_strand = parts[9]
                q_start = int(parts[10])
                header = line
                blocks = []
                t_pos, q_pos = t_start, q_start
                continue
            parts = line.split()
            size = int(parts[0])
            blocks.append((t_pos, t_pos + size, q_pos))
            if len(parts) == 3:
                dt, dq = int(parts[1]), int(parts[2])
                t_pos += size + dt
                q_pos += size + dq
            else:
                t_pos += size
                q_pos += size
        if header is not None:
            flush()

    for chrom in chains_by_chrom:
        chains_by_chrom[chrom].sort(key=lambda c: c.t_start)
    return dict(chains_by_chrom)


def lift_point(chains_by_chrom: dict, chrom: str, pos: int):
    """Returns lifted (chrom, pos) or None if unmapped (falls in a gap or
    outside any chain)."""
    chains = chains_by_chrom.get(chrom)
    if not chains:
        return None
    for chain in chains:
        if chain.t_start <= pos < chain.t_end:
            for t_block_start, t_block_end, q_block_start in chain.blocks:
                if t_block_start <= pos < t_block_end:
                    offset = pos - t_block_start
                    if chain.q_strand == "+":
                        return (chrom, q_block_start + offset)
                    else:
                        # query is on the minus strand relative to the chain's
                        # own qSize -- rare for hg19->hg38 but handled for
                        # correctness rather than silently assuming '+'.
                        return (chrom, chain.q_size - (q_block_start + offset))
            return None  # inside chain span but in a gap between blocks
    return None


def lift_interval(chains_by_chrom: dict, chrom: str, start: int, end: int):
    """Lifts start and end independently. Returns (chrom, new_start, new_end)
    or None if either endpoint fails to map."""
    lifted_start = lift_point(chains_by_chrom, chrom, start)
    lifted_end = lift_point(chains_by_chrom, chrom, end - 1)
    if lifted_start is None or lifted_end is None:
        return None
    _, ns = lifted_start
    _, ne = lifted_end
    if ns > ne:
        ns, ne = ne, ns
    return (chrom, ns, ne + 1)
