"""Filesystem paths that must resolve correctly both when running from
source and when running from a PyInstaller-frozen executable."""

import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parents[2]  # project root
    return base.joinpath(*parts)
