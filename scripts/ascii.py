from __future__ import annotations

from pathlib import Path


def load_ascii_portrait(path: Path) -> list[str]:
    """Load an ASCII portrait while preserving spacing."""
    if not path.exists():
        raise FileNotFoundError(f"ASCII portrait not found: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"ASCII portrait is empty: {path}")

    return lines
