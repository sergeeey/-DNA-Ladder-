"""Load project-root .env into os.environ (setdefault only).

Search order (first existing wins):
1. tracks/te_alu_3d/.env (gitignored)
2. sibling desk project DNA_TE_3DGenome_Context/.env
User explicitly accepts local persistence risk (2026-07-15).
"""

from __future__ import annotations

import os
from pathlib import Path

_TRACK_ENV = Path(__file__).resolve().parents[1] / ".env"
_DESK_ENV = Path(r"D:\DNK - 2\DNA_TE_3DGenome_Context\.env")
_LOADED: Path | None = None


def _candidate_env_paths() -> list[Path]:
    return [_TRACK_ENV, _DESK_ENV]


def load_project_env(*, force: bool = False) -> Path | None:
    """Load ALPHAGENOME_API_KEY etc. from gitignored .env. Returns path if read."""
    global _LOADED
    if _LOADED is not None and not force:
        return _LOADED if _LOADED.exists() else None
    path = next((p for p in _candidate_env_paths() if p.exists()), None)
    if path is None:
        _LOADED = None
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    _LOADED = path
    return path


def alphagenome_api_key() -> str | None:
    load_project_env()
    key = os.environ.get("ALPHAGENOME_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    return key or None
