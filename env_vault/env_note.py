"""Attach freeform notes to vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _note_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_notes.json"


def _load_notes(vault_dir: str) -> dict:
    p = _note_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_notes(vault_dir: str, data: dict) -> None:
    _note_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_note(vault_dir: str, key: str, note: str) -> bool:
    """Set a note for *key*. Returns True if new, False if updated."""
    data = _load_notes(vault_dir)
    is_new = key not in data
    data[key] = note
    _save_notes(vault_dir, data)
    return is_new


def get_note(vault_dir: str, key: str) -> Optional[str]:
    """Return the note for *key*, or None if not set."""
    return _load_notes(vault_dir).get(key)


def remove_note(vault_dir: str, key: str) -> bool:
    """Remove the note for *key*. Returns True if it existed."""
    data = _load_notes(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_notes(vault_dir, data)
    return True


def list_notes(vault_dir: str) -> dict[str, str]:
    """Return all key→note mappings, sorted by key."""
    return dict(sorted(_load_notes(vault_dir).items()))


def clear_notes(vault_dir: str) -> int:
    """Remove all notes. Returns the count of removed entries."""
    data = _load_notes(vault_dir)
    count = len(data)
    _save_notes(vault_dir, {})
    return count
