"""Key quality rating module for env-vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_RATINGS = {1, 2, 3, 4, 5}


def _rating_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_ratings.json"


def _load_ratings(vault_dir: str) -> dict:
    p = _rating_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ratings(vault_dir: str, data: dict) -> None:
    _rating_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_rating(vault_dir: str, key: str, rating: int) -> bool:
    """Set a quality rating (1-5) for a key.

    Returns True if new or changed, False if unchanged.
    Raises ValueError for invalid ratings.
    """
    if rating not in VALID_RATINGS:
        raise ValueError(f"Rating must be 1-5, got {rating}")
    data = _load_ratings(vault_dir)
    changed = data.get(key) != rating
    data[key] = rating
    _save_ratings(vault_dir, data)
    return changed


def remove_rating(vault_dir: str, key: str) -> bool:
    """Remove rating for a key. Returns True if removed, False if not found."""
    data = _load_ratings(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_ratings(vault_dir, data)
    return True


def get_rating(vault_dir: str, key: str) -> Optional[int]:
    """Return the rating for a key, or None if not set."""
    return _load_ratings(vault_dir).get(key)


def list_ratings(vault_dir: str) -> dict[str, int]:
    """Return all key -> rating mappings sorted by key."""
    return dict(sorted(_load_ratings(vault_dir).items()))


def average_rating(vault_dir: str) -> Optional[float]:
    """Return the average rating across all rated keys, or None if none rated."""
    data = _load_ratings(vault_dir)
    if not data:
        return None
    return sum(data.values()) / len(data)
