"""Audit log for tracking access and mutations to vault entries."""

import json
import os
import time
from pathlib import Path
from typing import List, Optional

AUDIT_FILENAME = ".env_vault_audit.json"
MAX_AUDIT_ENTRIES = 500


def _audit_path(vault_dir: str) -> Path:
    return Path(vault_dir) / AUDIT_FILENAME


def _load_audit(vault_dir: str) -> List[dict]:
    path = _audit_path(vault_dir)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_audit(vault_dir: str, entries: List[dict]) -> None:
    path = _audit_path(vault_dir)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_access(vault_dir: str, action: str, key: str, actor: Optional[str] = None) -> None:
    """Record an audit event for the given key and action."""
    entries = _load_audit(vault_dir)
    entry = {
        "timestamp": time.time(),
        "action": action,
        "key": key,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    entries.append(entry)
    if len(entries) > MAX_AUDIT_ENTRIES:
        entries = entries[-MAX_AUDIT_ENTRIES:]
    _save_audit(vault_dir, entries)


def get_audit_log(vault_dir: str, key: Optional[str] = None) -> List[dict]:
    """Return audit entries, optionally filtered by key."""
    entries = _load_audit(vault_dir)
    if key:
        entries = [e for e in entries if e.get("key") == key]
    return entries


def clear_audit_log(vault_dir: str) -> int:
    """Remove all audit entries. Returns count of removed entries."""
    entries = _load_audit(vault_dir)
    count = len(entries)
    _save_audit(vault_dir, [])
    return count
