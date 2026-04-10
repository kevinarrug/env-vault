"""Profile support: named sets of keys for different environments (dev, staging, prod)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _profiles_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".profiles.json"


def _load_profiles(vault_dir: str) -> Dict[str, List[str]]:
    path = _profiles_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_profiles(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _profiles_path(vault_dir).write_text(json.dumps(data, indent=2, sort_keys=True))


def create_profile(vault_dir: str, profile: str) -> None:
    """Create an empty profile if it does not already exist."""
    data = _load_profiles(vault_dir)
    if profile not in data:
        data[profile] = []
        _save_profiles(vault_dir, data)


def delete_profile(vault_dir: str, profile: str) -> bool:
    """Delete a profile. Returns True if it existed, False otherwise."""
    data = _load_profiles(vault_dir)
    if profile in data:
        del data[profile]
        _save_profiles(vault_dir, data)
        return True
    return False


def assign_key(vault_dir: str, profile: str, key: str) -> None:
    """Assign a vault key to a profile, creating the profile if needed."""
    data = _load_profiles(vault_dir)
    keys = data.setdefault(profile, [])
    if key not in keys:
        keys.append(key)
    _save_profiles(vault_dir, data)


def unassign_key(vault_dir: str, profile: str, key: str) -> bool:
    """Remove a key from a profile. Returns True if the key was present."""
    data = _load_profiles(vault_dir)
    keys = data.get(profile, [])
    if key in keys:
        keys.remove(key)
        _save_profiles(vault_dir, data)
        return True
    return False


def get_profile_keys(vault_dir: str, profile: str) -> List[str]:
    """Return keys assigned to a profile (empty list if profile unknown)."""
    return list(_load_profiles(vault_dir).get(profile, []))


def list_profiles(vault_dir: str) -> List[str]:
    """Return sorted list of all profile names."""
    return sorted(_load_profiles(vault_dir).keys())


def key_profiles(vault_dir: str, key: str) -> List[str]:
    """Return all profiles that contain the given key."""
    data = _load_profiles(vault_dir)
    return sorted(name for name, keys in data.items() if key in keys)
