"""Retention policy management for vault keys."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


def _retention_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_retention.json"


def _load_retention(vault_dir: str) -> dict:
    p = _retention_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_retention(vault_dir: str, data: dict) -> None:
    _retention_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_retention(vault_dir: str, key: str, days: int) -> bool:
    """Set a retention period (in days) for a key. Returns True if new, False if updated."""
    if days <= 0:
        raise ValueError("Retention days must be a positive integer.")
    data = _load_retention(vault_dir)
    is_new = key not in data
    data[key] = {
        "days": days,
        "set_at": time.time(),
    }
    _save_retention(vault_dir, data)
    return is_new


def remove_retention(vault_dir: str, key: str) -> bool:
    """Remove retention policy for a key. Returns True if removed, False if not found."""
    data = _load_retention(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_retention(vault_dir, data)
    return True


def get_retention(vault_dir: str, key: str) -> Optional[dict]:
    """Return retention info for a key, or None if not set."""
    return _load_retention(vault_dir).get(key)


def is_expired(vault_dir: str, key: str) -> bool:
    """Return True if the key's retention period has elapsed since it was set."""
    info = get_retention(vault_dir, key)
    if info is None:
        return False
    elapsed = time.time() - info["set_at"]
    return elapsed > info["days"] * 86400


def list_retention(vault_dir: str) -> dict:
    """Return all retention policies keyed by variable name."""
    return _load_retention(vault_dir)


def expired_keys(vault_dir: str) -> list[str]:
    """Return a list of keys whose retention period has elapsed."""
    return [k for k in list_retention(vault_dir) if is_expired(vault_dir, k)]
