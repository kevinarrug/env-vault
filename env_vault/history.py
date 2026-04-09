"""Version history tracking for vault entries."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

HISTORY_FILENAME = ".vault_history.json"
MAX_HISTORY_PER_KEY = 20


def _load_raw(history_path: Path) -> dict[str, list[dict[str, Any]]]:
    if not history_path.exists():
        return {}
    with history_path.open("r") as fh:
        return json.load(fh)


def _save_raw(history_path: Path, data: dict[str, list[dict[str, Any]]]) -> None:
    with history_path.open("w") as fh:
        json.dump(data, fh, indent=2)


def record_change(
    history_path: Path,
    key: str,
    encrypted_value: str,
    action: str = "set",
) -> None:
    """Append a history entry for *key*."""
    data = _load_raw(history_path)
    entries = data.setdefault(key, [])
    entries.append(
        {
            "action": action,
            "value": encrypted_value,
            "timestamp": time.time(),
        }
    )
    # Trim to the most recent entries
    data[key] = entries[-MAX_HISTORY_PER_KEY:]
    _save_raw(history_path, data)


def get_history(
    history_path: Path, key: str
) -> list[dict[str, Any]]:
    """Return the history list for *key* (oldest first)."""
    data = _load_raw(history_path)
    return data.get(key, [])


def list_keys_with_history(history_path: Path) -> list[str]:
    """Return all keys that have at least one history entry."""
    return list(_load_raw(history_path).keys())


def purge_key_history(history_path: Path, key: str) -> None:
    """Remove all history entries for *key*."""
    data = _load_raw(history_path)
    data.pop(key, None)
    _save_raw(history_path, data)
