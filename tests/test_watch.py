"""Tests for env_vault.watch."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from threading import Thread
from typing import List

import pytest

from env_vault.watch import WatchEvent, _vault_mtime, watch


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    """Return a temp directory with an initial vault.json."""
    vault_file = tmp_path / "vault.json"
    vault_file.write_text(json.dumps({"data": {}}))
    return tmp_path


# ---------------------------------------------------------------------------
# WatchEvent
# ---------------------------------------------------------------------------

def test_watch_event_str_contains_vault_dir(vault_dir: Path) -> None:
    event = WatchEvent(vault_dir=str(vault_dir), old_mtime=1.0, new_mtime=2.0)
    assert str(vault_dir) in str(event)


def test_watch_event_str_contains_timestamp(vault_dir: Path) -> None:
    event = WatchEvent(vault_dir=str(vault_dir), old_mtime=1.0, new_mtime=2.0)
    # ISO-like timestamp starts with year
    assert "20" in str(event)


# ---------------------------------------------------------------------------
# _vault_mtime
# ---------------------------------------------------------------------------

def test_vault_mtime_returns_float(vault_dir: Path) -> None:
    mtime = _vault_mtime(str(vault_dir))
    assert isinstance(mtime, float)


def test_vault_mtime_missing_returns_none(tmp_path: Path) -> None:
    assert _vault_mtime(str(tmp_path)) is None


# ---------------------------------------------------------------------------
# watch (integration-style, driven by a background writer)
# ---------------------------------------------------------------------------

def _modify_vault_after(vault_dir: Path, delay: float) -> None:
    """Helper: wait *delay* seconds then touch vault.json."""
    time.sleep(delay)
    vault_file = vault_dir / "vault.json"
    vault_file.write_text(json.dumps({"data": {"KEY": "val"}}))


def test_watch_detects_change(vault_dir: Path) -> None:
    events: List[WatchEvent] = []

    writer = Thread(target=_modify_vault_after, args=(vault_dir, 0.15), daemon=True)
    writer.start()

    watch(
        vault_dir=str(vault_dir),
        callback=events.append,
        interval=0.05,
        timeout=0.6,
    )

    assert len(events) == 1
    assert events[0].new_mtime > events[0].old_mtime


def test_watch_no_change_fires_no_callback(vault_dir: Path) -> None:
    events: List[WatchEvent] = []

    watch(
        vault_dir=str(vault_dir),
        callback=events.append,
        interval=0.05,
        timeout=0.25,
    )

    assert events == []
