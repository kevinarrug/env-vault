"""Category management for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _category_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".categories.json"


def _load_categories(vault_dir: str) -> Dict[str, str]:
    path = _category_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_categories(vault_dir: str, data: Dict[str, str]) -> None:
    path = _category_path(vault_dir)
    path.write_text(json.dumps(data, indent=2))


def set_category(vault_dir: str, key: str, category: str) -> bool:
    """Assign a category to a key. Returns True if new, False if updated."""
    data = _load_categories(vault_dir)
    is_new = key not in data or data[key] != category
    data[key] = category
    _save_categories(vault_dir, data)
    return is_new


def get_category(vault_dir: str, key: str) -> Optional[str]:
    """Return the category for a key, or None if not set."""
    return _load_categories(vault_dir).get(key)


def remove_category(vault_dir: str, key: str) -> bool:
    """Remove the category assignment for a key. Returns True if it existed."""
    data = _load_categories(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_categories(vault_dir, data)
    return True


def list_categories(vault_dir: str) -> Dict[str, str]:
    """Return all key -> category mappings."""
    return dict(_load_categories(vault_dir))


def keys_in_category(vault_dir: str, category: str) -> List[str]:
    """Return all keys assigned to the given category, sorted."""
    data = _load_categories(vault_dir)
    return sorted(k for k, v in data.items() if v == category)


def all_category_names(vault_dir: str) -> List[str]:
    """Return a sorted list of unique category names in use."""
    data = _load_categories(vault_dir)
    return sorted(set(data.values()))
