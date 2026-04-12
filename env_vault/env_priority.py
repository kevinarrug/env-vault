"""Priority levels for environment variable keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_PRIORITIES = ("critical", "high", "normal", "low")
_FILENAME = ".env_priority.json"


def _priority_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _FILENAME


def _load_priorities(vault_dir: str) -> Dict[str, str]:
    p = _priority_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(vault_dir: str, data: Dict[str, str]) -> None:
    _priority_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_priority(vault_dir: str, key: str, priority: str) -> bool:
    """Set priority for a key. Returns True if changed, False if already set to same value."""
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Choose from: {VALID_PRIORITIES}")
    data = _load_priorities(vault_dir)
    changed = data.get(key) != priority
    data[key] = priority
    _save_priorities(vault_dir, data)
    return changed


def get_priority(vault_dir: str, key: str) -> Optional[str]:
    """Return the priority for a key, or None if not set."""
    return _load_priorities(vault_dir).get(key)


def remove_priority(vault_dir: str, key: str) -> bool:
    """Remove priority for a key. Returns True if removed, False if not found."""
    data = _load_priorities(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_priorities(vault_dir, data)
    return True


def list_priorities(vault_dir: str) -> Dict[str, str]:
    """Return all key -> priority mappings."""
    return dict(_load_priorities(vault_dir))


def keys_by_priority(vault_dir: str, priority: str) -> List[str]:
    """Return all keys assigned to the given priority level."""
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Choose from: {VALID_PRIORITIES}")
    return sorted(k for k, v in _load_priorities(vault_dir).items() if v == priority)
