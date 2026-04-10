"""env_lock.py — lock/unlock individual keys to prevent accidental modification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _lock_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_lock.json"


def _load_locks(vault_dir: str) -> dict:
    p = _lock_path(vault_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_locks(vault_dir: str, data: dict) -> None:
    p = _lock_path(vault_dir)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def lock_key(vault_dir: str, key: str) -> bool:
    """Lock a key. Returns True if newly locked, False if already locked."""
    locks = _load_locks(vault_dir)
    if locks.get(key):
        return False
    locks[key] = True
    _save_locks(vault_dir, locks)
    return True


def unlock_key(vault_dir: str, key: str) -> bool:
    """Unlock a key. Returns True if unlocked, False if it was not locked."""
    locks = _load_locks(vault_dir)
    if not locks.get(key):
        return False
    del locks[key]
    _save_locks(vault_dir, locks)
    return True


def is_locked(vault_dir: str, key: str) -> bool:
    """Return True if the key is currently locked."""
    return bool(_load_locks(vault_dir).get(key))


def list_locked(vault_dir: str) -> List[str]:
    """Return sorted list of all locked keys."""
    return sorted(k for k, v in _load_locks(vault_dir).items() if v)


def assert_not_locked(vault_dir: str, key: str) -> None:
    """Raise ValueError if key is locked."""
    if is_locked(vault_dir, key):
        raise ValueError(f"Key '{key}' is locked and cannot be modified. Unlock it first.")


def clear_locks(vault_dir: str) -> int:
    """Remove all locks. Returns number of locks cleared."""
    locks = _load_locks(vault_dir)
    count = len([k for k, v in locks.items() if v])
    _save_locks(vault_dir, {})
    return count
