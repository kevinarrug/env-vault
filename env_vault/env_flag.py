"""Boolean flag metadata for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _flag_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".flags.json"


def _load_flags(vault_dir: str) -> Dict[str, bool]:
    p = _flag_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_flags(vault_dir: str, data: Dict[str, bool]) -> None:
    _flag_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_flag(vault_dir: str, key: str, value: bool) -> bool:
    """Set a boolean flag on a key. Returns True if changed, False if unchanged."""
    data = _load_flags(vault_dir)
    changed = data.get(key) != value
    data[key] = value
    _save_flags(vault_dir, data)
    return changed


def remove_flag(vault_dir: str, key: str) -> bool:
    """Remove a flag from a key. Returns True if it existed."""
    data = _load_flags(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_flags(vault_dir, data)
    return True


def get_flag(vault_dir: str, key: str) -> Optional[bool]:
    """Return the flag value for a key, or None if not set."""
    return _load_flags(vault_dir).get(key)


def list_flags(vault_dir: str) -> Dict[str, bool]:
    """Return all key -> flag mappings."""
    return dict(_load_flags(vault_dir))


def keys_with_flag(vault_dir: str, value: bool) -> List[str]:
    """Return all keys whose flag equals *value*."""
    return [k for k, v in _load_flags(vault_dir).items() if v == value]
