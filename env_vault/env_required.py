"""Track and enforce required keys in a vault."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _required_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_required.json"


def _load_required(vault_dir: str) -> List[str]:
    p = _required_path(vault_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_required(vault_dir: str, keys: List[str]) -> None:
    _required_path(vault_dir).write_text(json.dumps(sorted(set(keys)), indent=2))


def mark_required(vault_dir: str, key: str) -> bool:
    """Mark a key as required. Returns True if newly added, False if already present."""
    keys = _load_required(vault_dir)
    if key in keys:
        return False
    keys.append(key)
    _save_required(vault_dir, keys)
    return True


def unmark_required(vault_dir: str, key: str) -> bool:
    """Remove required mark from a key. Returns True if removed, False if not found."""
    keys = _load_required(vault_dir)
    if key not in keys:
        return False
    keys.remove(key)
    _save_required(vault_dir, keys)
    return True


def is_required(vault_dir: str, key: str) -> bool:
    return key in _load_required(vault_dir)


def list_required(vault_dir: str) -> List[str]:
    return _load_required(vault_dir)


@dataclass
class RequiredCheckResult:
    missing: List[str] = field(default_factory=list)
    present: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.missing) == 0

    def summary(self) -> str:
        if self.passed:
            return "All required keys are present."
        keys = ", ".join(self.missing)
        return f"Missing required keys: {keys}"


def check_required(vault_dir: str, available_keys: List[str]) -> RequiredCheckResult:
    """Check which required keys are missing from available_keys."""
    required = _load_required(vault_dir)
    available = set(available_keys)
    missing = [k for k in required if k not in available]
    present = [k for k in required if k in available]
    return RequiredCheckResult(missing=missing, present=present)
