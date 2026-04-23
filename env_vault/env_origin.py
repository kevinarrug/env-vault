"""Track the origin/source system of environment variable keys."""

from __future__ import annotations

import json
from pathlib import Path

ORIGINS_FILE = ".env_origins.json"


def _origin_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ORIGINS_FILE


def _load_origins(vault_dir: str) -> dict:
    p = _origin_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_origins(vault_dir: str, data: dict) -> None:
    p = _origin_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_origin(vault_dir: str, key: str, origin: str) -> bool:
    """Set origin for a key. Returns True if new, False if updated."""
    data = _load_origins(vault_dir)
    is_new = key not in data or data[key] != origin
    data[key] = origin
    _save_origins(vault_dir, data)
    return is_new


def get_origin(vault_dir: str, key: str) -> str | None:
    """Return origin for key, or None if not set."""
    return _load_origins(vault_dir).get(key)


def remove_origin(vault_dir: str, key: str) -> bool:
    """Remove origin for key. Returns True if removed, False if not found."""
    data = _load_origins(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_origins(vault_dir, data)
    return True


def list_origins(vault_dir: str) -> dict[str, str]:
    """Return all key -> origin mappings."""
    return dict(_load_origins(vault_dir))


def keys_by_origin(vault_dir: str, origin: str) -> list[str]:
    """Return all keys that have the given origin."""
    data = _load_origins(vault_dir)
    return sorted(k for k, v in data.items() if v == origin)
