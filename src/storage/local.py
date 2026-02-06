"""Local filesystem storage (dev)."""

from __future__ import annotations

from pathlib import Path


def save_bytes(path: str | Path, data: bytes) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return str(target)
