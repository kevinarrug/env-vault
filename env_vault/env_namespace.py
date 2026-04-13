"""Namespace support for grouping keys under a prefix."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _namespace_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_namespace.json"


def _load_namespaces(vault_dir: str) -> Dict[str, str]:
    path = _namespace_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_namespaces(vault_dir: str, data: Dict[str, str]) -> None:
    _namespace_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_namespace(vault_dir: str, key: str, namespace: str) -> bool:
    """Assign a namespace to a key. Returns True if new, False if updated."""
    data = _load_namespaces(vault_dir)
    is_new = key not in data or data[key] != namespace
    data[key] = namespace
    _save_namespaces(vault_dir, data)
    return is_new


def get_namespace(vault_dir: str, key: str) -> Optional[str]:
    """Return the namespace for a key, or None if not set."""
    return _load_namespaces(vault_dir).get(key)


def remove_namespace(vault_dir: str, key: str) -> bool:
    """Remove the namespace assignment for a key. Returns True if removed."""
    data = _load_namespaces(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_namespaces(vault_dir, data)
    return True


def list_namespaces(vault_dir: str) -> Dict[str, str]:
    """Return all key -> namespace mappings."""
    return dict(_load_namespaces(vault_dir))


def keys_in_namespace(vault_dir: str, namespace: str) -> List[str]:
    """Return all keys assigned to the given namespace, sorted."""
    data = _load_namespaces(vault_dir)
    return sorted(k for k, ns in data.items() if ns == namespace)


def list_all_namespaces(vault_dir: str) -> List[str]:
    """Return a sorted list of unique namespace names."""
    return sorted(set(_load_namespaces(vault_dir).values()))
