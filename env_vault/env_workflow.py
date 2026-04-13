"""Workflow step definitions for env-vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_STEPS = ["draft", "review", "approved", "deprecated", "archived"]


def _workflow_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_workflow.json"


def _load_workflows(vault_dir: str) -> Dict[str, str]:
    path = _workflow_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_workflows(vault_dir: str, data: Dict[str, str]) -> None:
    _workflow_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_step(vault_dir: str, key: str, step: str) -> bool:
    """Set the workflow step for a key. Returns True if changed, False if unchanged."""
    if step not in VALID_STEPS:
        raise ValueError(f"Invalid step '{step}'. Must be one of: {VALID_STEPS}")
    data = _load_workflows(vault_dir)
    changed = data.get(key) != step
    data[key] = step
    _save_workflows(vault_dir, data)
    return changed


def get_step(vault_dir: str, key: str) -> Optional[str]:
    """Return the current workflow step for a key, or None if not set."""
    return _load_workflows(vault_dir).get(key)


def remove_step(vault_dir: str, key: str) -> bool:
    """Remove workflow step for a key. Returns True if it existed."""
    data = _load_workflows(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_workflows(vault_dir, data)
    return True


def list_steps(vault_dir: str) -> Dict[str, str]:
    """Return all key -> step mappings."""
    return dict(_load_workflows(vault_dir))


def keys_in_step(vault_dir: str, step: str) -> List[str]:
    """Return all keys currently at the given workflow step."""
    if step not in VALID_STEPS:
        raise ValueError(f"Invalid step '{step}'. Must be one of: {VALID_STEPS}")
    data = _load_workflows(vault_dir)
    return sorted(k for k, v in data.items() if v == step)
