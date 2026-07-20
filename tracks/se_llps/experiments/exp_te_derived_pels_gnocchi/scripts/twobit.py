#!/usr/bin/env python3
"""Minimal hg38.2bit sequence reader (GC% for intervals)."""

from __future__ import annotations

import struct
from pathlib import Path


class TwoBitFile:
    """Read UCSC .2bit (version 0) DNA; returns uppercase ACGTN strings."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.fh = open(self.path, "rb")
        raw = self.fh.read(16)
        sig, ver, n_seq, _reserved = struct.unpack(">IIII", raw)
        if sig != 0x1A412743:
            # try little-endian
            self.fh.seek(0)
            sig, ver, n_seq, _reserved = struct.unpack("<IIII", self.fh.read(16))
            self.endian = "<"
            if sig != 0x1A412743:
                raise ValueError(f"bad 2bit signature: {sig:#x}")
        else:
            self.endian = ">"
        if ver != 0:
            raise ValueError(f"unsupported 2bit version {ver}")
        self.index: dict[str, int] = {}
        for _ in range(n_seq):
            (name_len,) = struct.unpack(f"{self.endian}B", self.fh.read(1))
            name = self.fh.read(name_len).decode("ascii")
            (offset,) = struct.unpack(f"{self.endian}I", self.fh.read(4))
            self.index[name] = offset
        self._seq_meta: dict[str, tuple[int, list[tuple[int, int]], list[tuple[int, int]], int]] = {}

    def close(self) -> None:
        self.fh.close()

    def __enter__(self) -> TwoBitFile:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _load_meta(self, chrom: str) -> None:
        if chrom in self._seq_meta:
            return
        off = self.index[chrom]
        self.fh.seek(off)
        (dna_size,) = struct.unpack(f"{self.endian}I", self.fh.read(4))
        (n_blocks,) = struct.unpack(f"{self.endian}I", self.fh.read(4))
        n_starts = list(
            struct.unpack(
                f"{self.endian}{n_blocks}I", self.fh.read(4 * n_blocks)
            )
        ) if n_blocks else []
        n_sizes = list(
            struct.unpack(
                f"{self.endian}{n_blocks}I", self.fh.read(4 * n_blocks)
            )
        ) if n_blocks else []
        (mask_blocks,) = struct.unpack(f"{self.endian}I", self.fh.read(4))
        m_starts = list(
            struct.unpack(
                f"{self.endian}{mask_blocks}I", self.fh.read(4 * mask_blocks)
            )
        ) if mask_blocks else []
        m_sizes = list(
            struct.unpack(
                f"{self.endian}{mask_blocks}I", self.fh.read(4 * mask_blocks)
            )
        ) if mask_blocks else []
        self.fh.read(4)  # reserved
        packed_off = self.fh.tell()
        n_regions = list(zip(n_starts, n_sizes))
        m_regions = list(zip(m_starts, m_sizes))
        self._seq_meta[chrom] = (dna_size, n_regions, m_regions, packed_off)

    def sequence(self, chrom: str, start: int, end: int) -> str:
        """0-based half-open genomic interval."""
        self._load_meta(chrom)
        dna_size, n_regions, _m_regions, packed_off = self._seq_meta[chrom]
        if start < 0 or end > dna_size or end < start:
            raise ValueError(f"bad interval {chrom}:{start}-{end} size={dna_size}")
        # packed DNA: 4 bases per byte, bits 7-6 = base0
        bases = []
        byte_len = (dna_size + 3) // 4
        # read only needed byte span
        b0 = start // 4
        b1 = (end + 3) // 4
        self.fh.seek(packed_off + b0)
        blob = self.fh.read(b1 - b0)
        decode = ("T", "C", "A", "G")
        for pos in range(start, end):
            bi = pos // 4 - b0
            shift = 6 - 2 * (pos % 4)
            bases.append(decode[(blob[bi] >> shift) & 0x3])
        # apply N blocks
        for ns, nsz in n_regions:
            ne = ns + nsz
            if ne <= start or ns >= end:
                continue
            for i in range(max(ns, start), min(ne, end)):
                bases[i - start] = "N"
        return "".join(bases)

    def gc_fraction(self, chrom: str, start: int, end: int) -> float:
        seq = self.sequence(chrom, start, end)
        gc = sum(1 for b in seq if b in "GCgc")
        atgc = sum(1 for b in seq if b in "ATGCatgc")
        if atgc == 0:
            return float("nan")
        return gc / atgc
