"""Key expiry management: set, check, and list expiring keys in a vault."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _expiry_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".expiry.json"


def _load_expiry(vault_dir: str) -> Dict[str, float]:
    path = _expiry_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry(vault_dir: str, data: Dict[str, float]) -> None:
    _expiry_path(vault_dir).write_text(json.dumps(data, indent=2))


@dataclass
class ExpiryInfo:
    key: str
    expires_at: float

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.expires_at - time.time())

    def __str__(self) -> str:
        status = "EXPIRED" if self.is_expired else f"{self.remaining_seconds:.0f}s remaining"
        return f"{self.key}: expires_at={self.expires_at:.0f} ({status})"


def set_expiry(vault_dir: str, key: str, seconds: float) -> float:
    """Set an expiry on *key* that fires *seconds* from now. Returns the epoch timestamp."""
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    data = _load_expiry(vault_dir)
    expires_at = time.time() + seconds
    data[key] = expires_at
    _save_expiry(vault_dir, data)
    return expires_at


def remove_expiry(vault_dir: str, key: str) -> bool:
    """Remove expiry for *key*. Returns True if an entry was removed."""
    data = _load_expiry(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_expiry(vault_dir, data)
    return True


def get_expiry(vault_dir: str, key: str) -> Optional[ExpiryInfo]:
    """Return ExpiryInfo for *key*, or None if no expiry is set."""
    data = _load_expiry(vault_dir)
    if key not in data:
        return None
    return ExpiryInfo(key=key, expires_at=data[key])


def list_expiring(vault_dir: str) -> List[ExpiryInfo]:
    """Return all keys that have an expiry set, sorted by expiry time."""
    data = _load_expiry(vault_dir)
    infos = [ExpiryInfo(key=k, expires_at=v) for k, v in data.items()]
    return sorted(infos, key=lambda e: e.expires_at)


def purge_expired(vault_dir: str) -> List[str]:
    """Remove expired entries from the expiry store. Returns list of purged keys."""
    data = _load_expiry(vault_dir)
    now = time.time()
    expired = [k for k, ts in data.items() if ts <= now]
    for k in expired:
        del data[k]
    if expired:
        _save_expiry(vault_dir, data)
    return expired
