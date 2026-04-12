"""Access control: restrict which keys a given role/user can read or write."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _access_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_access.json"


def _load_access(vault_dir: str) -> Dict[str, Dict[str, List[str]]]:
    p = _access_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(vault_dir: str, data: Dict[str, Dict[str, List[str]]]) -> None:
    _access_path(vault_dir).write_text(json.dumps(data, indent=2, sort_keys=True))


def grant(vault_dir: str, key: str, role: str, permission: str) -> bool:
    """Grant *role* the given *permission* ('read' or 'write') on *key*.
    Returns True if newly added, False if already present."""
    if permission not in ("read", "write"):
        raise ValueError(f"permission must be 'read' or 'write', got {permission!r}")
    data = _load_access(vault_dir)
    perms: List[str] = data.setdefault(key, {}).setdefault(role, [])
    if permission in perms:
        return False
    perms.append(permission)
    _save_access(vault_dir, data)
    return True


def revoke(vault_dir: str, key: str, role: str, permission: str) -> bool:
    """Revoke *permission* from *role* on *key*.
    Returns True if removed, False if not present."""
    data = _load_access(vault_dir)
    perms: List[str] = data.get(key, {}).get(role, [])
    if permission not in perms:
        return False
    perms.remove(permission)
    _save_access(vault_dir, data)
    return True


def can(vault_dir: str, key: str, role: str, permission: str) -> bool:
    """Return True if *role* has *permission* on *key*."""
    data = _load_access(vault_dir)
    return permission in data.get(key, {}).get(role, [])


def get_permissions(vault_dir: str, key: str) -> Dict[str, List[str]]:
    """Return all role→permissions mappings for *key*."""
    return dict(_load_access(vault_dir).get(key, {}))


def list_accessible_keys(vault_dir: str, role: str, permission: str) -> List[str]:
    """Return all keys where *role* has *permission*."""
    data = _load_access(vault_dir)
    return sorted(k for k, roles in data.items() if permission in roles.get(role, []))


def clear_key(vault_dir: str, key: str) -> bool:
    """Remove all ACL entries for *key*. Returns True if anything was removed."""
    data = _load_access(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_access(vault_dir, data)
    return True
