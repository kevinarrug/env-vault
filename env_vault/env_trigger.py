"""Trigger rules: run a shell command when a key's value changes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _trigger_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_triggers.json"


def _load_triggers(vault_dir: str) -> Dict[str, List[str]]:
    p = _trigger_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_triggers(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _trigger_path(vault_dir).write_text(json.dumps(data, indent=2))


def add_trigger(vault_dir: str, key: str, command: str) -> bool:
    """Register *command* to fire when *key* changes. Returns True if new."""
    data = _load_triggers(vault_dir)
    cmds = data.setdefault(key, [])
    if command in cmds:
        return False
    cmds.append(command)
    _save_triggers(vault_dir, data)
    return True


def remove_trigger(vault_dir: str, key: str, command: str) -> bool:
    """Remove *command* from *key*'s trigger list. Returns True if removed."""
    data = _load_triggers(vault_dir)
    cmds = data.get(key, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    if not cmds:
        del data[key]
    _save_triggers(vault_dir, data)
    return True


def get_triggers(vault_dir: str, key: str) -> List[str]:
    """Return all commands registered for *key*."""
    return list(_load_triggers(vault_dir).get(key, []))


def list_all_triggers(vault_dir: str) -> Dict[str, List[str]]:
    """Return the full trigger map."""
    return dict(_load_triggers(vault_dir))


def clear_triggers(vault_dir: str, key: str) -> int:
    """Remove all triggers for *key*. Returns number removed."""
    data = _load_triggers(vault_dir)
    cmds = data.pop(key, [])
    _save_triggers(vault_dir, data)
    return len(cmds)
