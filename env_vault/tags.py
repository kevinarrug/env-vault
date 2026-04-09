"""Tag management for env-vault: assign, remove, and filter keys by tag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_TAGS_FILENAME = ".env_vault_tags.json"


def _tags_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _TAGS_FILENAME


def _load_tags(vault_dir: str) -> Dict[str, List[str]]:
    """Return mapping of key -> list[tag]."""
    path = _tags_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_tags(vault_dir: str, data: Dict[str, List[str]]) -> None:
    path = _tags_path(vault_dir)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)


def add_tag(vault_dir: str, key: str, tag: str) -> None:
    """Add *tag* to *key*. Idempotent."""
    data = _load_tags(vault_dir)
    tags = data.setdefault(key, [])
    if tag not in tags:
        tags.append(tag)
    _save_tags(vault_dir, data)


def remove_tag(vault_dir: str, key: str, tag: str) -> bool:
    """Remove *tag* from *key*. Returns True if the tag existed."""
    data = _load_tags(vault_dir)
    tags = data.get(key, [])
    if tag not in tags:
        return False
    tags.remove(tag)
    if not tags:
        data.pop(key, None)
    else:
        data[key] = tags
    _save_tags(vault_dir, data)
    return True


def get_tags(vault_dir: str, key: str) -> List[str]:
    """Return all tags for *key*."""
    return _load_tags(vault_dir).get(key, [])


def keys_by_tag(vault_dir: str, tag: str) -> List[str]:
    """Return all keys that carry *tag*."""
    data = _load_tags(vault_dir)
    return sorted(k for k, tags in data.items() if tag in tags)


def all_tags(vault_dir: str) -> Dict[str, List[str]]:
    """Return the full tag mapping."""
    return _load_tags(vault_dir)


def clear_tags_for_key(vault_dir: str, key: str) -> None:
    """Remove all tags associated with *key*."""
    data = _load_tags(vault_dir)
    data.pop(key, None)
    _save_tags(vault_dir, data)
