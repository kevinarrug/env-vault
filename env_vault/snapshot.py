"""Snapshot support: capture and restore full vault state at a point in time."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

_SNAPSHOT_DIR = "snapshots"


def _snapshot_dir(vault_dir: str) -> Path:
    p = Path(vault_dir) / _SNAPSHOT_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def create_snapshot(vault_dir: str, label: Optional[str] = None) -> Path:
    """Serialise the current vault data file into a timestamped snapshot."""
    vault_file = Path(vault_dir) / "vault.json"
    if not vault_file.exists():
        raise FileNotFoundError(f"No vault found at {vault_file}")

    raw = vault_file.read_text(encoding="utf-8")
    data = json.loads(raw)

    ts = int(time.time())
    slug = f"{ts}_{label}" if label else str(ts)
    snap_path = _snapshot_dir(vault_dir) / f"{slug}.json"

    snap_path.write_text(
        json.dumps({"timestamp": ts, "label": label, "vault": data}, indent=2),
        encoding="utf-8",
    )
    return snap_path


def list_snapshots(vault_dir: str) -> List[dict]:
    """Return snapshot metadata sorted newest-first."""
    sd = _snapshot_dir(vault_dir)
    results = []
    for f in sorted(sd.glob("*.json"), reverse=True):
        try:
            meta = json.loads(f.read_text(encoding="utf-8"))
            results.append(
                {
                    "file": f.name,
                    "timestamp": meta.get("timestamp"),
                    "label": meta.get("label"),
                }
            )
        except (json.JSONDecodeError, KeyError):
            continue
    return results


def restore_snapshot(vault_dir: str, filename: str) -> None:
    """Overwrite the current vault with the contents of a snapshot."""
    snap_path = _snapshot_dir(vault_dir) / filename
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot not found: {filename}")

    meta = json.loads(snap_path.read_text(encoding="utf-8"))
    vault_data = meta["vault"]

    vault_file = Path(vault_dir) / "vault.json"
    vault_file.write_text(json.dumps(vault_data, indent=2), encoding="utf-8")


def delete_snapshot(vault_dir: str, filename: str) -> bool:
    """Delete a snapshot file. Returns True if deleted, False if not found."""
    snap_path = _snapshot_dir(vault_dir) / filename
    if not snap_path.exists():
        return False
    snap_path.unlink()
    return True
