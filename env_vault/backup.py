"""Backup and restore vault snapshots."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import List, Optional

_BACKUP_DIR = ".backups"


def _backup_dir(vault_dir: str) -> Path:
    return Path(vault_dir) / _BACKUP_DIR


def create_backup(vault_dir: str, label: Optional[str] = None) -> Path:
    """Copy the current vault.json into a timestamped backup file."""
    src = Path(vault_dir) / "vault.json"
    if not src.exists():
        raise FileNotFoundError(f"No vault found at {src}")

    bdir = _backup_dir(vault_dir)
    bdir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())
    suffix = f"_{label}" if label else ""
    dest = bdir / f"vault_{ts}{suffix}.json"
    shutil.copy2(src, dest)
    return dest


def list_backups(vault_dir: str) -> List[Path]:
    """Return backup files sorted oldest-first."""
    bdir = _backup_dir(vault_dir)
    if not bdir.exists():
        return []
    return sorted(bdir.glob("vault_*.json"))


def restore_backup(vault_dir: str, backup_path: str) -> None:
    """Overwrite the current vault.json with a backup."""\n    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup not found: {src}")

    # Validate it looks like a vault file
    with src.open() as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Backup file does not contain a valid vault object")

    dest = Path(vault_dir) / "vault.json"
    shutil.copy2(src, dest)


def delete_backup(backup_path: str) -> None:
    """Delete a single backup file."""
    p = Path(backup_path)
    if not p.exists():
        raise FileNotFoundError(f"Backup not found: {p}")
    p.unlink()


def purge_backups(vault_dir: str, keep: int = 5) -> List[Path]:
    """Delete old backups, keeping the *keep* most recent. Returns deleted paths."""
    if keep < 0:
        raise ValueError(f"keep must be a non-negative integer, got {keep}")
    backups = list_backups(vault_dir)
    to_delete = backups[: max(0, len(backups) - keep)]
    for p in to_delete:
        p.unlink()
    return to_delete


def get_latest_backup(vault_dir: str) -> Optional[Path]:
    """Return the most recent backup file, or None if no backups exist."""
    backups = list_backups(vault_dir)
    return backups[-1] if backups else None
