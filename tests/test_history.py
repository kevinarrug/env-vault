"""Tests for env_vault.history."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from env_vault.history import (
    MAX_HISTORY_PER_KEY,
    get_history,
    list_keys_with_history,
    purge_key_history,
    record_change,
)


@pytest.fixture()
def history_file(tmp_path: Path) -> Path:
    return tmp_path / ".vault_history.json"


def test_record_and_retrieve(history_file: Path) -> None:
    record_change(history_file, "DB_URL", "enc_value_1")
    entries = get_history(history_file, "DB_URL")
    assert len(entries) == 1
    assert entries[0]["value"] == "enc_value_1"
    assert entries[0]["action"] == "set"


def test_multiple_records_ordered(history_file: Path) -> None:
    for i in range(3):
        record_change(history_file, "SECRET", f"enc_{i}")
    entries = get_history(history_file, "SECRET")
    assert len(entries) == 3
    assert entries[0]["value"] == "enc_0"
    assert entries[-1]["value"] == "enc_2"


def test_history_capped_at_max(history_file: Path) -> None:
    for i in range(MAX_HISTORY_PER_KEY + 5):
        record_change(history_file, "KEY", f"val_{i}")
    entries = get_history(history_file, "KEY")
    assert len(entries) == MAX_HISTORY_PER_KEY
    # Oldest entries trimmed; most recent retained
    assert entries[-1]["value"] == f"val_{MAX_HISTORY_PER_KEY + 4}"


def test_get_history_missing_key(history_file: Path) -> None:
    assert get_history(history_file, "NONEXISTENT") == []


def test_list_keys_with_history(history_file: Path) -> None:
    record_change(history_file, "A", "v1")
    record_change(history_file, "B", "v2")
    keys = list_keys_with_history(history_file)
    assert set(keys) == {"A", "B"}


def test_list_keys_empty_file(history_file: Path) -> None:
    assert list_keys_with_history(history_file) == []


def test_purge_key_history(history_file: Path) -> None:
    record_change(history_file, "TO_PURGE", "enc")
    record_change(history_file, "KEEP", "enc")
    purge_key_history(history_file, "TO_PURGE")
    assert get_history(history_file, "TO_PURGE") == []
    assert len(get_history(history_file, "KEEP")) == 1


def test_record_delete_action(history_file: Path) -> None:
    record_change(history_file, "KEY", "enc", action="delete")
    entries = get_history(history_file, "KEY")
    assert entries[0]["action"] == "delete"


def test_timestamp_is_recent(history_file: Path) -> None:
    before = time.time()
    record_change(history_file, "TS_KEY", "enc")
    after = time.time()
    ts = get_history(history_file, "TS_KEY")[0]["timestamp"]
    assert before <= ts <= after
