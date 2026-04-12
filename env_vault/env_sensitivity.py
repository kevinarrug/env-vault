"""Sensitivity level management for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

LEVELS = ("public", "internal", "confidential", "secret")


def _sensitivity_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".sensitivity.json"


def _load_sensitivity(vault_dir: str) -> Dict[str, str]:
    p = _sensitivity_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_sensitivity(vault_dir: str, data: Dict[str, str]) -> None:
    _sensitivity_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_sensitivity(vault_dir: str, key: str, level: str) -> bool:
    """Set sensitivity level for a key. Returns True if changed, False if unchanged."""
    if level not in LEVELS:
        raise ValueError(f"Invalid level '{level}'. Must be one of: {', '.join(LEVELS)}")
    data = _load_sensitivity(vault_dir)
    changed = data.get(key) != level
    data[key] = level
    _save_sensitivity(vault_dir, data)
    return changed


def get_sensitivity(vault_dir: str, key: str) -> Optional[str]:
    """Return the sensitivity level for a key, or None if not set."""
    return _load_sensitivity(vault_dir).get(key)


def remove_sensitivity(vault_dir: str, key: str) -> bool:
    """Remove sensitivity level for a key. Returns True if it existed."""
    data = _load_sensitivity(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_sensitivity(vault_dir, data)
    return True


def list_sensitivity(vault_dir: str) -> Dict[str, str]:
    """Return all key -> level mappings."""
    return dict(_load_sensitivity(vault_dir))


def keys_at_level(vault_dir: str, level: str) -> List[str]:
    """Return all keys assigned to a specific sensitivity level."""
    if level not in LEVELS:
        raise ValueError(f"Invalid level '{level}'. Must be one of: {', '.join(LEVELS)}")
    data = _load_sensitivity(vault_dir)
    return sorted(k for k, v in data.items() if v == level)
