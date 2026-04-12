"""Freeze/unfreeze vault keys to prevent accidental modification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


def _freeze_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".freeze.json"


def _load_frozen(vault_dir: str) -> dict:
    p = _freeze_path(vault_dir)
    if not p.exists():
        return {"keys": []}
    return json.loads(p.read_text())


def _save_frozen(vault_dir: str, data: dict) -> None:
    _freeze_path(vault_dir).write_text(json.dumps(data, indent=2))


def freeze_key(vault_dir: str, key: str) -> bool:
    """Freeze a key. Returns True if newly frozen, False if already frozen."""
    data = _load_frozen(vault_dir)
    if key in data["keys"]:
        return False
    data["keys"].append(key)
    _save_frozen(vault_dir, data)
    return True


def unfreeze_key(vault_dir: str, key: str) -> bool:
    """Unfreeze a key. Returns True if removed, False if not found."""
    data = _load_frozen(vault_dir)
    if key not in data["keys"]:
        return False
    data["keys"].remove(key)
    _save_frozen(vault_dir, data)
    return True


def is_frozen(vault_dir: str, key: str) -> bool:
    """Return True if the key is currently frozen."""
    return key in _load_frozen(vault_dir)["keys"]


def list_frozen(vault_dir: str) -> List[str]:
    """Return all frozen keys, sorted."""
    return sorted(_load_frozen(vault_dir)["keys"])


@dataclass
class FreezeGuard:
    """Context used to check writes against frozen keys."""
    vault_dir: str

    def check(self, key: str) -> Optional[str]:
        """Return an error message if key is frozen, else None."""
        if is_frozen(self.vault_dir, key):
            return f"Key '{key}' is frozen and cannot be modified."
        return None
