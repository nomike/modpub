from __future__ import annotations
import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
