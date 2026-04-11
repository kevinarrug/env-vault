"""Scope management: associate vault keys with named scopes (e.g. dev, staging, prod)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _scopes_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_scopes.json"


def _load_scopes(vault_dir: str) -> Dict[str, List[str]]:
    p = _scopes_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_scopes(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _scopes_path(vault_dir).write_text(json.dumps(data, indent=2))


def add_to_scope(vault_dir: str, scope: str, key: str) -> bool:
    """Add key to scope. Returns True if newly added, False if already present."""
    data = _load_scopes(vault_dir)
    members = data.setdefault(scope, [])
    if key in members:
        return False
    members.append(key)
    _save_scopes(vault_dir, data)
    return True


def remove_from_scope(vault_dir: str, scope: str, key: str) -> bool:
    """Remove key from scope. Returns True if removed, False if not found."""
    data = _load_scopes(vault_dir)
    members = data.get(scope, [])
    if key not in members:
        return False
    members.remove(key)
    if not members:
        del data[scope]
    else:
        data[scope] = members
    _save_scopes(vault_dir, data)
    return True


def get_keys_in_scope(vault_dir: str, scope: str) -> List[str]:
    """Return all keys assigned to the given scope."""
    return list(_load_scopes(vault_dir).get(scope, []))


def get_scopes_for_key(vault_dir: str, key: str) -> List[str]:
    """Return all scopes that contain the given key."""
    data = _load_scopes(vault_dir)
    return sorted(scope for scope, members in data.items() if key in members)


def list_scopes(vault_dir: str) -> List[str]:
    """Return all defined scope names, sorted."""
    return sorted(_load_scopes(vault_dir).keys())


def delete_scope(vault_dir: str, scope: str) -> bool:
    """Delete an entire scope. Returns True if it existed, False otherwise."""
    data = _load_scopes(vault_dir)
    if scope not in data:
        return False
    del data[scope]
    _save_scopes(vault_dir, data)
    return True
