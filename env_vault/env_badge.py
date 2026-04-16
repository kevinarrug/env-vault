from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_BADGES = {"stable", "experimental", "deprecated", "internal", "public", "beta"}


def _badge_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_badge.json"


def _load_badges(vault_dir: str) -> dict:
    p = _badge_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_badges(vault_dir: str, data: dict) -> None:
    _badge_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_badge(vault_dir: str, key: str, badge: str) -> bool:
    """Assign a badge to a key. Returns True if new/changed, False if unchanged."""
    if badge not in VALID_BADGES:
        raise ValueError(f"Invalid badge '{badge}'. Valid: {sorted(VALID_BADGES)}")
    data = _load_badges(vault_dir)
    changed = data.get(key) != badge
    data[key] = badge
    _save_badges(vault_dir, data)
    return changed


def remove_badge(vault_dir: str, key: str) -> bool:
    """Remove badge from a key. Returns True if removed, False if not found."""
    data = _load_badges(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_badges(vault_dir, data)
    return True


def get_badge(vault_dir: str, key: str) -> Optional[str]:
    return _load_badges(vault_dir).get(key)


def list_badges(vault_dir: str) -> dict[str, str]:
    return dict(_load_badges(vault_dir))


def filter_by_badge(vault_dir: str, badge: str) -> list[str]:
    """Return all keys that have the given badge."""
    return [k for k, v in _load_badges(vault_dir).items() if v == badge]
