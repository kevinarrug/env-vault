"""Reference tracking: mark a key as a reference to another key."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _ref_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_refs.json"


def _load_refs(vault_dir: str) -> dict:
    p = _ref_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_refs(vault_dir: str, data: dict) -> None:
    _ref_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_ref(vault_dir: str, key: str, target: str) -> bool:
    """Point *key* at *target*. Returns True if new, False if updated."""
    if key == target:
        raise ValueError(f"A key cannot reference itself: {key!r}")
    refs = _load_refs(vault_dir)
    is_new = key not in refs
    refs[key] = target
    _save_refs(vault_dir, refs)
    return is_new


def remove_ref(vault_dir: str, key: str) -> bool:
    """Remove the reference for *key*. Returns True if it existed."""
    refs = _load_refs(vault_dir)
    if key not in refs:
        return False
    del refs[key]
    _save_refs(vault_dir, refs)
    return True


def get_ref(vault_dir: str, key: str) -> Optional[str]:
    """Return the target key that *key* references, or None."""
    return _load_refs(vault_dir).get(key)


def list_refs(vault_dir: str) -> dict[str, str]:
    """Return all {key: target} reference mappings."""
    return dict(_load_refs(vault_dir))


def resolve_ref(vault_dir: str, key: str, vault) -> Optional[str]:
    """Resolve a reference chain and return the final value, or None."""
    seen: set[str] = set()
    current = key
    while True:
        target = get_ref(vault_dir, current)
        if target is None:
            # current is not a reference — read directly from vault
            try:
                return vault.get(current)
            except KeyError:
                return None
        if target in seen:
            return None  # circular reference guard
        seen.add(current)
        current = target
