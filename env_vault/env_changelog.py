"""Track a human-readable changelog entry per key."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _changelog_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_changelog.json"


def _load_changelog(vault_dir: str) -> dict:
    p = _changelog_path(vault_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_changelog(vault_dir: str, data: dict) -> None:
    p = _changelog_path(vault_dir)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def add_entry(vault_dir: str, key: str, message: str, author: Optional[str] = None) -> dict:
    """Append a changelog entry for *key*.  Returns the new entry."""
    data = _load_changelog(vault_dir)
    entries = data.get(key, [])
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "author": author,
    }
    entries.append(entry)
    data[key] = entries
    _save_changelog(vault_dir, data)
    return entry


def get_entries(vault_dir: str, key: str) -> List[dict]:
    """Return all changelog entries for *key*, oldest first."""
    data = _load_changelog(vault_dir)
    return list(data.get(key, []))


def remove_entries(vault_dir: str, key: str) -> bool:
    """Delete all changelog entries for *key*.  Returns True if entries existed."""
    data = _load_changelog(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_changelog(vault_dir, data)
    return True


def list_keys(vault_dir: str) -> List[str]:
    """Return all keys that have at least one changelog entry."""
    return sorted(_load_changelog(vault_dir).keys())
