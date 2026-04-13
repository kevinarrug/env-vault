"""Type annotation support for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_TYPES = {"string", "int", "float", "bool", "json"}


def _type_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_types.json"


def _load_types(vault_dir: str) -> dict:
    p = _type_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_types(vault_dir: str, data: dict) -> None:
    _type_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_type(vault_dir: str, key: str, type_name: str) -> bool:
    """Set the declared type for a key. Returns True if new, False if updated."""
    if type_name not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type_name}'. Must be one of: {sorted(VALID_TYPES)}")
    data = _load_types(vault_dir)
    is_new = key not in data or data[key] != type_name
    data[key] = type_name
    _save_types(vault_dir, data)
    return is_new


def get_type(vault_dir: str, key: str) -> Optional[str]:
    """Return the declared type for a key, or None if not set."""
    return _load_types(vault_dir).get(key)


def remove_type(vault_dir: str, key: str) -> bool:
    """Remove the type annotation for a key. Returns True if removed."""
    data = _load_types(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_types(vault_dir, data)
    return True


def list_types(vault_dir: str) -> dict:
    """Return all key -> type mappings."""
    return dict(_load_types(vault_dir))


def validate_value(value: str, type_name: str) -> bool:
    """Return True if value is compatible with the declared type."""
    try:
        if type_name == "string":
            return True
        elif type_name == "int":
            int(value)
        elif type_name == "float":
            float(value)
        elif type_name == "bool":
            return value.lower() in {"true", "false", "1", "0", "yes", "no"}
        elif type_name == "json":
            json.loads(value)
        return True
    except (ValueError, json.JSONDecodeError):
        return False
