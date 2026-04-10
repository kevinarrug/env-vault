"""Key aliasing — create short or friendly names that map to real vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _alias_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".aliases.json"


def _load_aliases(vault_dir: str) -> Dict[str, str]:
    path = _alias_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(vault_dir: str, aliases: Dict[str, str]) -> None:
    _alias_path(vault_dir).write_text(json.dumps(aliases, indent=2, sort_keys=True))


def add_alias(vault_dir: str, alias: str, target_key: str) -> bool:
    """Map *alias* to *target_key*. Returns True if newly created, False if updated."""
    aliases = _load_aliases(vault_dir)
    is_new = alias not in aliases
    aliases[alias] = target_key
    _save_aliases(vault_dir, aliases)
    return is_new


def remove_alias(vault_dir: str, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(vault_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(vault_dir, aliases)
    return True


def resolve_alias(vault_dir: str, alias: str) -> Optional[str]:
    """Return the real key for *alias*, or None if not found."""
    return _load_aliases(vault_dir).get(alias)


def list_aliases(vault_dir: str) -> List[Dict[str, str]]:
    """Return sorted list of {alias, target} dicts."""
    aliases = _load_aliases(vault_dir)
    return [
        {"alias": a, "target": t}
        for a, t in sorted(aliases.items())
    ]


def rename_alias(vault_dir: str, old_alias: str, new_alias: str) -> bool:
    """Rename an alias without changing its target. Returns False if old_alias missing."""
    aliases = _load_aliases(vault_dir)
    if old_alias not in aliases:
        return False
    aliases[new_alias] = aliases.pop(old_alias)
    _save_aliases(vault_dir, aliases)
    return True
