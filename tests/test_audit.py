"""Tests for env_vault.audit module."""

import time

import pytest

from env_vault.audit import (
    MAX_AUDIT_ENTRIES,
    clear_audit_log,
    get_audit_log,
    record_access,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_record_and_retrieve(vault_dir):
    record_access(vault_dir, "GET", "API_KEY", actor="alice")
    entries = get_audit_log(vault_dir)
    assert len(entries) == 1
    assert entries[0]["action"] == "GET"
    assert entries[0]["key"] == "API_KEY"
    assert entries[0]["actor"] == "alice"


def test_multiple_actions_ordered(vault_dir):
    record_access(vault_dir, "SET", "FOO", actor="bob")
    time.sleep(0.01)
    record_access(vault_dir, "GET", "FOO", actor="bob")
    entries = get_audit_log(vault_dir)
    assert entries[0]["action"] == "SET"
    assert entries[1]["action"] == "GET"


def test_filter_by_key(vault_dir):
    record_access(vault_dir, "SET", "DB_URL", actor="ci")
    record_access(vault_dir, "SET", "API_KEY", actor="ci")
    filtered = get_audit_log(vault_dir, key="DB_URL")
    assert len(filtered) == 1
    assert filtered[0]["key"] == "DB_URL"


def test_clear_audit_log(vault_dir):
    record_access(vault_dir, "GET", "SECRET", actor="dev")
    record_access(vault_dir, "DELETE", "SECRET", actor="dev")
    count = clear_audit_log(vault_dir)
    assert count == 2
    assert get_audit_log(vault_dir) == []


def test_audit_capped_at_max(vault_dir):
    for i in range(MAX_AUDIT_ENTRIES + 10):
        record_access(vault_dir, "GET", f"KEY_{i}", actor="bot")
    entries = get_audit_log(vault_dir)
    assert len(entries) == MAX_AUDIT_ENTRIES
    # Oldest entries should have been dropped
    assert entries[0]["key"] == f"KEY_{10}"


def test_empty_log_returns_empty_list(vault_dir):
    assert get_audit_log(vault_dir) == []


def test_timestamp_is_recent(vault_dir):
    before = time.time()
    record_access(vault_dir, "SET", "TOKEN", actor="user")
    after = time.time()
    entry = get_audit_log(vault_dir)[0]
    assert before <= entry["timestamp"] <= after
