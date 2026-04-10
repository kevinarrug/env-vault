"""TTL (time-to-live) support for vault keys — keys expire after a set duration."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

_TTL_FILENAME = ".ttl.json"


def _ttl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _TTL_FILENAME


def _load_ttl(vault_dir: str) -> dict:
    p = _ttl_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(vault_dir: str, data: dict) -> None:
    _ttl_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_ttl(vault_dir: str, key: str, seconds: int) -> float:
    """Set TTL for a key. Returns the absolute expiry timestamp."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    data = _load_ttl(vault_dir)
    expires_at = time.time() + seconds
    data[key] = expires_at
    _save_ttl(vault_dir, data)
    return expires_at


def remove_ttl(vault_dir: str, key: str) -> bool:
    """Remove TTL for a key. Returns True if it existed."""
    data = _load_ttl(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_ttl(vault_dir, data)
    return True


def get_ttl(vault_dir: str, key: str) -> Optional[float]:
    """Return remaining seconds for a key, or None if no TTL is set."""
    data = _load_ttl(vault_dir)
    if key not in data:
        return None
    remaining = data[key] - time.time()
    return max(remaining, 0.0)


def is_expired(vault_dir: str, key: str) -> bool:
    """Return True if the key has a TTL that has already elapsed."""
    data = _load_ttl(vault_dir)
    if key not in data:
        return False
    return time.time() >= data[key]


def list_ttls(vault_dir: str) -> dict[str, float]:
    """Return a mapping of key -> remaining seconds for all TTL-tracked keys."""
    data = _load_ttl(vault_dir)
    now = time.time()
    return {k: max(v - now, 0.0) for k, v in data.items()}


def purge_expired(vault_dir: str) -> list[str]:
    """Remove expired TTL entries and return the list of expired keys."""
    data = _load_ttl(vault_dir)
    now = time.time()
    expired = [k for k, exp in data.items() if now >= exp]
    for k in expired:
        del data[k]
    if expired:
        _save_ttl(vault_dir, data)
    return expired
