"""Load project-root .env into os.environ (setdefault only).

Path: DNA_TE_3DGenome_Context/.env (gitignored).
User explicitly accepts local persistence risk (2026-07-15).
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
_LOADED = False


def load_project_env(*, force: bool = False) -> Path | None:
    """Load ALPHAGENOME_API_KEY etc. from gitignored .env. Returns path if read."""
    global _LOADED
    if _LOADED and not force:
        return _ENV_PATH if _ENV_PATH.exists() else None
    if not _ENV_PATH.exists():
        return None
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    _LOADED = True
    return _ENV_PATH


def alphagenome_api_key() -> str | None:
    load_project_env()
    key = os.environ.get("ALPHAGENOME_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    return key or None
