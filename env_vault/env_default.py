"""env_default.py — manage default/fallback values for vault keys."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _default_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_defaults.json"


def _load_defaults(vault_dir: str) -> dict:
    p = _default_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_defaults(vault_dir: str, data: dict) -> None:
    _default_path(vault_dir).write_text(json.dumps(data, indent=2, sort_keys=True))


def set_default(vault_dir: str, key: str, value: str) -> bool:
    """Set a default value for *key*. Returns True if newly added, False if updated."""
    data = _load_defaults(vault_dir)
    is_new = key not in data
    data[key] = value
    _save_defaults(vault_dir, data)
    return is_new


def remove_default(vault_dir: str, key: str) -> bool:
    """Remove the default for *key*. Returns True if it existed."""
    data = _load_defaults(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_defaults(vault_dir, data)
    return True


def get_default(vault_dir: str, key: str) -> Optional[str]:
    """Return the stored default for *key*, or None."""
    return _load_defaults(vault_dir).get(key)


def list_defaults(vault_dir: str) -> dict:
    """Return all stored defaults as {key: value}."""
    return dict(_load_defaults(vault_dir))


@dataclass
class ResolveDefault:
    key: str
    value: str
    from_default: bool

    def __str__(self) -> str:
        source = "default" if self.from_default else "vault"
        return f"{self.key}={self.value!r} (source: {source})"


def resolve_with_default(vault_dir: str, key: str, vault_value: Optional[str]) -> ResolveDefault:
    """Return vault value if present, else the stored default.

    Raises KeyError if neither vault value nor default exists.
    """
    if vault_value is not None:
        return ResolveDefault(key=key, value=vault_value, from_default=False)
    default = get_default(vault_dir, key)
    if default is not None:
        return ResolveDefault(key=key, value=default, from_default=True)
    raise KeyError(f"No value or default found for key: {key!r}")
