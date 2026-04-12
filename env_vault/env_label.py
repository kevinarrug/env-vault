"""Assign human-readable labels to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def _label_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_labels.json"


def _load_labels(vault_dir: str) -> Dict[str, str]:
    p = _label_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(vault_dir: str, data: Dict[str, str]) -> None:
    _label_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_label(vault_dir: str, key: str, label: str) -> bool:
    """Set a label for a key. Returns True if new, False if updated."""
    if not label:
        raise ValueError("Label must not be empty.")
    data = _load_labels(vault_dir)
    is_new = key not in data or data[key] != label
    data[key] = label
    _save_labels(vault_dir, data)
    return is_new


def remove_label(vault_dir: str, key: str) -> bool:
    """Remove a label from a key. Returns True if removed, False if not found."""
    data = _load_labels(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_labels(vault_dir, data)
    return True


def get_label(vault_dir: str, key: str) -> Optional[str]:
    """Return the label for a key, or None if not set."""
    return _load_labels(vault_dir).get(key)


def list_labels(vault_dir: str) -> Dict[str, str]:
    """Return all key-label mappings sorted by key."""
    return dict(sorted(_load_labels(vault_dir).items()))


def keys_with_label(vault_dir: str, label: str) -> list[str]:
    """Return all keys that have the given label."""
    return sorted(k for k, v in _load_labels(vault_dir).items() if v == label)
