"""Visibility control for vault keys (public / private / internal)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_LEVELS = {"public", "private", "internal"}


def _visibility_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".visibility.json"


def _load_visibility(vault_dir: str) -> Dict[str, str]:
    p = _visibility_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_visibility(vault_dir: str, data: Dict[str, str]) -> None:
    _visibility_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_visibility(vault_dir: str, key: str, level: str) -> bool:
    """Set visibility level for *key*. Returns True if changed, False if unchanged."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level '{level}'. Choose from {VALID_LEVELS}.")
    data = _load_visibility(vault_dir)
    changed = data.get(key) != level
    data[key] = level
    _save_visibility(vault_dir, data)
    return changed


def get_visibility(vault_dir: str, key: str) -> Optional[str]:
    """Return the visibility level for *key*, or None if not set."""
    return _load_visibility(vault_dir).get(key)


def remove_visibility(vault_dir: str, key: str) -> bool:
    """Remove visibility setting for *key*. Returns True if it existed."""
    data = _load_visibility(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_visibility(vault_dir, data)
    return True


def list_visibility(vault_dir: str) -> Dict[str, str]:
    """Return all key → visibility-level mappings."""
    return dict(_load_visibility(vault_dir))


def keys_with_level(vault_dir: str, level: str) -> List[str]:
    """Return all keys that have the given visibility level."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level '{level}'. Choose from {VALID_LEVELS}.")
    return [k for k, v in _load_visibility(vault_dir).items() if v == level]
