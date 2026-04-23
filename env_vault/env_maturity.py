"""Track maturity level of environment variable keys."""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("experimental", "beta", "stable", "deprecated")


def _maturity_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".maturity.json"


def _load_maturity(vault_dir: str) -> dict:
    p = _maturity_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_maturity(vault_dir: str, data: dict) -> None:
    _maturity_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_maturity(vault_dir: str, key: str, level: str) -> bool:
    """Set maturity level for a key. Returns True if changed, False if unchanged."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid maturity level '{level}'. Must be one of {VALID_LEVELS}")
    data = _load_maturity(vault_dir)
    changed = data.get(key) != level
    data[key] = level
    _save_maturity(vault_dir, data)
    return changed


def get_maturity(vault_dir: str, key: str) -> str | None:
    """Return maturity level for a key, or None if not set."""
    return _load_maturity(vault_dir).get(key)


def remove_maturity(vault_dir: str, key: str) -> bool:
    """Remove maturity level for a key. Returns True if it existed."""
    data = _load_maturity(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_maturity(vault_dir, data)
    return True


def list_maturity(vault_dir: str) -> dict[str, str]:
    """Return all key -> maturity level mappings."""
    return dict(_load_maturity(vault_dir))


def get_keys_by_level(vault_dir: str, level: str) -> list[str]:
    """Return all keys with a given maturity level."""
    data = _load_maturity(vault_dir)
    return sorted(k for k, v in data.items() if v == level)
