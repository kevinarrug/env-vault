"""Key-level version pinning: record and enforce a specific version index for a key."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _version_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_versions.json"


def _load_versions(vault_dir: str) -> dict:
    p = _version_path(vault_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_versions(vault_dir: str, data: dict) -> None:
    p = _version_path(vault_dir)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


@dataclass
class VersionPin:
    key: str
    pinned_index: int
    note: str

    def __str__(self) -> str:
        return f"{self.key} pinned at index {self.pinned_index}: {self.note}"


def pin_version(vault_dir: str, key: str, index: int, note: str = "") -> bool:
    """Pin *key* to *index* in history. Returns True if newly set, False if updated."""
    if index < 0:
        raise ValueError("index must be >= 0")
    data = _load_versions(vault_dir)
    is_new = key not in data
    data[key] = {"index": index, "note": note}
    _save_versions(vault_dir, data)
    return is_new


def unpin_version(vault_dir: str, key: str) -> bool:
    """Remove version pin for *key*. Returns True if removed, False if not found."""
    data = _load_versions(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_versions(vault_dir, data)
    return True


def get_pin(vault_dir: str, key: str) -> Optional[VersionPin]:
    """Return VersionPin for *key*, or None if not pinned."""
    data = _load_versions(vault_dir)
    if key not in data:
        return None
    entry = data[key]
    return VersionPin(key=key, pinned_index=entry["index"], note=entry.get("note", ""))


def list_pins(vault_dir: str) -> list[VersionPin]:
    """Return all version pins sorted by key."""
    data = _load_versions(vault_dir)
    return [
        VersionPin(key=k, pinned_index=v["index"], note=v.get("note", ""))
        for k, v in sorted(data.items())
    ]


def is_pinned(vault_dir: str, key: str) -> bool:
    return get_pin(vault_dir, key) is not None
