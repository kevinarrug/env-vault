"""Tests for env_vault/env_lock.py."""

import pytest
from pathlib import Path

from env_vault.env_lock import (
    lock_key,
    unlock_key,
    is_locked,
    list_locked,
    assert_not_locked,
    clear_locks,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_lock_key_returns_true_when_newly_locked(vault_dir):
    assert lock_key(vault_dir, "API_KEY") is True


def test_lock_key_returns_false_when_already_locked(vault_dir):
    lock_key(vault_dir, "API_KEY")
    assert lock_key(vault_dir, "API_KEY") is False


def test_is_locked_true_after_lock(vault_dir):
    lock_key(vault_dir, "SECRET")
    assert is_locked(vault_dir, "SECRET") is True


def test_is_locked_false_before_lock(vault_dir):
    assert is_locked(vault_dir, "UNKNOWN") is False


def test_unlock_key_returns_true_when_was_locked(vault_dir):
    lock_key(vault_dir, "TOKEN")
    assert unlock_key(vault_dir, "TOKEN") is True


def test_unlock_key_returns_false_when_not_locked(vault_dir):
    assert unlock_key(vault_dir, "TOKEN") is False


def test_is_locked_false_after_unlock(vault_dir):
    lock_key(vault_dir, "DB_PASS")
    unlock_key(vault_dir, "DB_PASS")
    assert is_locked(vault_dir, "DB_PASS") is False


def test_list_locked_returns_sorted(vault_dir):
    lock_key(vault_dir, "Z_KEY")
    lock_key(vault_dir, "A_KEY")
    lock_key(vault_dir, "M_KEY")
    assert list_locked(vault_dir) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_locked_empty_when_none(vault_dir):
    assert list_locked(vault_dir) == []


def test_assert_not_locked_raises_when_locked(vault_dir):
    lock_key(vault_dir, "LOCKED_KEY")
    with pytest.raises(ValueError, match="LOCKED_KEY"):
        assert_not_locked(vault_dir, "LOCKED_KEY")


def test_assert_not_locked_passes_when_unlocked(vault_dir):
    assert_not_locked(vault_dir, "FREE_KEY")  # should not raise


def test_clear_locks_returns_count(vault_dir):
    lock_key(vault_dir, "A")
    lock_key(vault_dir, "B")
    assert clear_locks(vault_dir) == 2


def test_clear_locks_removes_all(vault_dir):
    lock_key(vault_dir, "A")
    lock_key(vault_dir, "B")
    clear_locks(vault_dir)
    assert list_locked(vault_dir) == []


def test_lock_file_created_on_first_lock(vault_dir):
    lock_key(vault_dir, "KEY")
    assert Path(vault_dir, ".env_lock.json").exists()
