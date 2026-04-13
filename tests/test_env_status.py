"""Tests for env_vault.env_status."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from env_vault.env_status import KeyStatus, get_status, get_all_statuses
from env_vault.env_lock import lock_key
from env_vault.env_freeze import freeze_key
from env_vault.expiry import set_expiry
from env_vault.env_deprecate import deprecate_key
from env_vault.ttl import set_ttl


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


# --- KeyStatus unit tests ---

def test_key_status_active_by_default():
    s = KeyStatus(key="FOO")
    assert s.active is True


def test_key_status_inactive_when_expired():
    s = KeyStatus(key="FOO", expired=True)
    assert s.active is False


def test_key_status_inactive_when_deprecated():
    s = KeyStatus(key="FOO", deprecated=True)
    assert s.active is False


def test_key_status_summary_ok_when_clean():
    s = KeyStatus(key="FOO")
    assert s.summary() == "ok"


def test_key_status_summary_includes_locked():
    s = KeyStatus(key="FOO", locked=True)
    assert "locked" in s.summary()


def test_key_status_summary_includes_frozen():
    s = KeyStatus(key="FOO", frozen=True)
    assert "frozen" in s.summary()


def test_key_status_summary_includes_ttl():
    s = KeyStatus(key="FOO", ttl_remaining=120.0)
    assert "ttl=120s" in s.summary()


def test_key_status_summary_deprecated_with_message():
    s = KeyStatus(key="FOO", deprecated=True, deprecation_message="use BAR")
    assert "deprecated(use BAR)" in s.summary()


def test_key_status_str_contains_key():
    s = KeyStatus(key="MY_KEY")
    assert "MY_KEY" in str(s)


# --- get_status integration tests ---

def test_get_status_clean_key_is_active(vault_dir):
    status = get_status(vault_dir, "CLEAN_KEY")
    assert status.active is True
    assert status.summary() == "ok"


def test_get_status_reflects_lock(vault_dir):
    lock_key(vault_dir, "DB_PASS")
    status = get_status(vault_dir, "DB_PASS")
    assert status.locked is True
    assert "locked" in status.summary()


def test_get_status_reflects_freeze(vault_dir):
    freeze_key(vault_dir, "API_KEY")
    status = get_status(vault_dir, "API_KEY")
    assert status.frozen is True


def test_get_status_reflects_expiry(vault_dir):
    # Set expiry 1 second in the past by setting 1s and sleeping
    set_expiry(vault_dir, "OLD_KEY", 1)
    time.sleep(1.1)
    status = get_status(vault_dir, "OLD_KEY")
    assert status.expired is True
    assert status.active is False


def test_get_status_reflects_deprecation(vault_dir):
    deprecate_key(vault_dir, "LEGACY_KEY", message="use NEW_KEY")
    status = get_status(vault_dir, "LEGACY_KEY")
    assert status.deprecated is True
    assert status.deprecation_message == "use NEW_KEY"


def test_get_all_statuses_returns_one_per_key(vault_dir):
    keys = ["A", "B", "C"]
    statuses = get_all_statuses(vault_dir, keys)
    assert len(statuses) == 3
    assert [s.key for s in statuses] == keys
