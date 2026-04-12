"""Attach and retrieve human-readable comments for vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _comment_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".comments.json"


def _load_comments(vault_dir: str) -> dict[str, str]:
    p = _comment_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_comments(vault_dir: str, data: dict[str, str]) -> None:
    _comment_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_comment(vault_dir: str, key: str, comment: str) -> bool:
    """Set a comment for *key*. Returns True if new, False if updated."""
    data = _load_comments(vault_dir)
    is_new = key not in data
    data[key] = comment
    _save_comments(vault_dir, data)
    return is_new


def get_comment(vault_dir: str, key: str) -> Optional[str]:
    """Return the comment for *key*, or None if not set."""
    return _load_comments(vault_dir).get(key)


def remove_comment(vault_dir: str, key: str) -> bool:
    """Remove the comment for *key*. Returns True if it existed."""
    data = _load_comments(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_comments(vault_dir, data)
    return True


def list_comments(vault_dir: str) -> dict[str, str]:
    """Return all key→comment mappings."""
    return dict(_load_comments(vault_dir))


def keys_with_comments(vault_dir: str) -> list[str]:
    """Return sorted list of keys that have a comment."""
    return sorted(_load_comments(vault_dir).keys())
