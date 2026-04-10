"""Watch a vault file for changes and notify on modifications."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass
class WatchEvent:
    """Represents a detected change in the vault file."""

    vault_dir: str
    old_mtime: float
    new_mtime: float
    changed_at: float = field(default_factory=time.time)

    def __str__(self) -> str:
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.changed_at))
        return f"[{ts}] Vault changed in '{self.vault_dir}'"


def _vault_mtime(vault_dir: str) -> Optional[float]:
    """Return the last-modified time of vault.json, or None if absent."""
    path = Path(vault_dir) / "vault.json"
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def watch(
    vault_dir: str,
    callback: Callable[[WatchEvent], None],
    interval: float = 1.0,
    timeout: Optional[float] = None,
) -> None:
    """Poll the vault file and invoke *callback* whenever it changes.

    Args:
        vault_dir: Directory containing vault.json.
        callback:  Called with a WatchEvent on each detected change.
        interval:  Polling interval in seconds.
        timeout:   Stop watching after this many seconds (None = forever).
    """
    start = time.monotonic()
    last_mtime = _vault_mtime(vault_dir)

    while True:
        if timeout is not None and (time.monotonic() - start) >= timeout:
            break

        time.sleep(interval)

        current_mtime = _vault_mtime(vault_dir)
        if current_mtime is not None and current_mtime != last_mtime:
            event = WatchEvent(
                vault_dir=vault_dir,
                old_mtime=last_mtime or 0.0,
                new_mtime=current_mtime,
            )
            callback(event)
            last_mtime = current_mtime
