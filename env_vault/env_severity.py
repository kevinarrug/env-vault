"""Severity levels for environment variable keys."""

from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = {"low", "medium", "high", "critical"}


def _severity_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_severity.json"


def _load_severity(vault_dir: str) -> dict:
    p = _severity_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_severity(vault_dir: str, data: dict) -> None:
    _severity_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_severity(vault_dir: str, key: str, level: str) -> bool:
    """Set severity level for a key. Returns True if changed, False if unchanged."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid severity level '{level}'. Must be one of: {sorted(VALID_LEVELS)}")
    data = _load_severity(vault_dir)
    changed = data.get(key) != level
    data[key] = level
    _save_severity(vault_dir, data)
    return changed


def get_severity(vault_dir: str, key: str) -> str | None:
    """Get severity level for a key, or None if not set."""
    return _load_severity(vault_dir).get(key)


def remove_severity(vault_dir: str, key: str) -> bool:
    """Remove severity for a key. Returns True if it existed."""
    data = _load_severity(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_severity(vault_dir, data)
    return True


def list_severity(vault_dir: str) -> dict[str, str]:
    """Return all key -> severity level mappings."""
    return dict(_load_severity(vault_dir))


def keys_by_level(vault_dir: str, level: str) -> list[str]:
    """Return all keys with the given severity level."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid severity level '{level}'. Must be one of: {sorted(VALID_LEVELS)}")
    data = _load_severity(vault_dir)
    return sorted(k for k, v in data.items() if v == level)
