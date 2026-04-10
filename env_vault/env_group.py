"""Group management for env-vault: assign keys to named groups and filter by group."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_GROUPS_FILE = ".env_groups.json"


def _groups_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _GROUPS_FILE


def _load_groups(vault_dir: str) -> Dict[str, List[str]]:
    path = _groups_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_groups(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _groups_path(vault_dir).write_text(json.dumps(data, indent=2))


def add_to_group(vault_dir: str, group: str, key: str) -> bool:
    """Add *key* to *group*. Returns True if the key was newly added."""
    data = _load_groups(vault_dir)
    members = data.setdefault(group, [])
    if key in members:
        return False
    members.append(key)
    _save_groups(vault_dir, data)
    return True


def remove_from_group(vault_dir: str, group: str, key: str) -> bool:
    """Remove *key* from *group*. Returns True if the key was present."""
    data = _load_groups(vault_dir)
    members = data.get(group, [])
    if key not in members:
        return False
    members.remove(key)
    if not members:
        del data[group]
    else:
        data[group] = members
    _save_groups(vault_dir, data)
    return True


def get_groups_for_key(vault_dir: str, key: str) -> List[str]:
    """Return all group names that contain *key*."""
    data = _load_groups(vault_dir)
    return sorted(g for g, members in data.items() if key in members)


def get_keys_in_group(vault_dir: str, group: str) -> List[str]:
    """Return all keys belonging to *group*, sorted."""
    data = _load_groups(vault_dir)
    return sorted(data.get(group, []))


def list_groups(vault_dir: str) -> List[str]:
    """Return all defined group names, sorted."""
    return sorted(_load_groups(vault_dir).keys())


def delete_group(vault_dir: str, group: str) -> bool:
    """Delete an entire group. Returns True if the group existed."""
    data = _load_groups(vault_dir)
    if group not in data:
        return False
    del data[group]
    _save_groups(vault_dir, data)
    return True
