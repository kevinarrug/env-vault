"""Track the source/origin of environment variable values."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _source_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_sources.json"


def _load_sources(vault_dir: str) -> Dict[str, str]:
    path = _source_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_sources(vault_dir: str, data: Dict[str, str]) -> None:
    _source_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_source(vault_dir: str, key: str, source: str) -> bool:
    """Set the source for a key. Returns True if new, False if updated."""
    data = _load_sources(vault_dir)
    is_new = key not in data
    data[key] = source
    _save_sources(vault_dir, data)
    return is_new


def get_source(vault_dir: str, key: str) -> Optional[str]:
    """Return the source for a key, or None if not set."""
    return _load_sources(vault_dir).get(key)


def remove_source(vault_dir: str, key: str) -> bool:
    """Remove source for a key. Returns True if it existed."""
    data = _load_sources(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_sources(vault_dir, data)
    return True


def list_sources(vault_dir: str) -> Dict[str, str]:
    """Return all key -> source mappings."""
    return dict(_load_sources(vault_dir))


def keys_by_source(vault_dir: str, source: str) -> List[str]:
    """Return all keys that match the given source."""
    data = _load_sources(vault_dir)
    return sorted(k for k, v in data.items() if v == source)
