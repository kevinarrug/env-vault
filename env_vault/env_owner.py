"""Ownership tracking for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_OWNER_FILE = "owners.json"


def _owner_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _OWNER_FILE


def _load_owners(vault_dir: str) -> Dict[str, str]:
    p = _owner_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_owners(vault_dir: str, data: Dict[str, str]) -> None:
    _owner_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_owner(vault_dir: str, key: str, owner: str) -> bool:
    """Assign *owner* to *key*. Returns True if new, False if updated."""
    data = _load_owners(vault_dir)
    is_new = key not in data or data[key] != owner
    data[key] = owner
    _save_owners(vault_dir, data)
    return is_new


def get_owner(vault_dir: str, key: str) -> Optional[str]:
    """Return the owner of *key*, or None if unset."""
    return _load_owners(vault_dir).get(key)


def remove_owner(vault_dir: str, key: str) -> bool:
    """Remove ownership record for *key*. Returns True if it existed."""
    data = _load_owners(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_owners(vault_dir, data)
    return True


def list_owned_by(vault_dir: str, owner: str) -> List[str]:
    """Return all keys owned by *owner*, sorted."""
    data = _load_owners(vault_dir)
    return sorted(k for k, v in data.items() if v == owner)


def get_all_owners(vault_dir: str) -> Dict[str, str]:
    """Return the full key→owner mapping."""
    return dict(_load_owners(vault_dir))
