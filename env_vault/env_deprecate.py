"""Mark vault keys as deprecated with optional replacement suggestions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _deprecate_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".deprecations.json"


def _load_deprecations(vault_dir: str) -> dict:
    p = _deprecate_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deprecations(vault_dir: str, data: dict) -> None:
    _deprecate_path(vault_dir).write_text(json.dumps(data, indent=2))


@dataclass
class DeprecationInfo:
    key: str
    reason: str
    replacement: Optional[str] = None

    def __str__(self) -> str:
        msg = f"{self.key} is deprecated: {self.reason}"
        if self.replacement:
            msg += f" (use '{self.replacement}' instead)"
        return msg


def deprecate_key(
    vault_dir: str,
    key: str,
    reason: str,
    replacement: Optional[str] = None,
) -> bool:
    """Mark a key as deprecated. Returns True if newly added, False if updated."""
    data = _load_deprecations(vault_dir)
    is_new = key not in data
    data[key] = {"reason": reason, "replacement": replacement}
    _save_deprecations(vault_dir, data)
    return is_new


def undeprecate_key(vault_dir: str, key: str) -> bool:
    """Remove deprecation from a key. Returns True if removed, False if not found."""
    data = _load_deprecations(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_deprecations(vault_dir, data)
    return True


def get_deprecation(vault_dir: str, key: str) -> Optional[DeprecationInfo]:
    """Return DeprecationInfo for a key, or None if not deprecated."""
    data = _load_deprecations(vault_dir)
    if key not in data:
        return None
    entry = data[key]
    return DeprecationInfo(key=key, reason=entry["reason"], replacement=entry.get("replacement"))


def list_deprecated(vault_dir: str) -> list[DeprecationInfo]:
    """Return all deprecated keys sorted alphabetically."""
    data = _load_deprecations(vault_dir)
    return [
        DeprecationInfo(key=k, reason=v["reason"], replacement=v.get("replacement"))
        for k, v in sorted(data.items())
    ]


def is_deprecated(vault_dir: str, key: str) -> bool:
    """Return True if the key is marked as deprecated."""
    return key in _load_deprecations(vault_dir)
