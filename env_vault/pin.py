"""Pin specific vault keys to a required value or pattern, preventing accidental overwrites."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional


def _pin_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".pin.json"


def _load_pins(vault_dir: str) -> dict:
    p = _pin_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(vault_dir: str, data: dict) -> None:
    _write_text(json.dumps(data, indent=2))


def pin_key(vault_dir: str, key: str, pattern: str) -> bool:
    """Pin a key to a regex pattern. Returns True if newly pinned, False if updated."""
    pins = _load_pins(vault_dir)
    is_new = key not in pins
    pins[key] = pattern
    _save_pins(vault_dir, pins)
    return is_new


def unpin_key(vault_dir: str, key: str) -> bool:
    """Remove a pin for a key. Returns True if removed, False if not found."""
    pins = _load_pins(vault_dir)
    if key not in pins:
        return False
    del pins[key]
    _save_pins(vault_dir, pins)
    return True


def get_pin(vault_dir: str, key: str) -> Optional[str]:
    """Return the pin pattern for a key, or None if not pinned."""
    return _load_pins(vault_dir).get(key)


def list_pins(vault_dir: str) -> dict[str, str]:
    """Return all pinned keys and their patterns."""
    return dict(_load_pins(vault_dir))


def check_pin(vault_dir: str, key: str, value: str) -> bool:
    """Return True if value satisfies the pin pattern (or key is not pinned)."""
    pattern = get_pin(vault_dir, key)
    if pattern is None:
        return True
    return bool(re.fullmatch(pattern, value))


def validate_all(vault_dir: str, secrets: dict[str, str]) -> dict[str, str]:
    """Return a dict of {key: pattern} for every pinned key whose value fails validation."""
    violations: dict[str, str] = {}
    pins = _load_pins(vault_dir)
    for key, pattern in pins.items():
        value = secrets.get(key, "")
        if not re.fullmatch(pattern, value):
            violations[key] = pattern
    return violations
