"""Tests for env_vault.env_freeze."""

import pytest

from env_vault.env_freeze import (
    freeze_key,
    unfreeze_key,
    is_frozen,
    list_frozen,
    FreezeGuard,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_freeze_key_returns_true_when_new(vault_dir):
    assert freeze_key(vault_dir, "MY_KEY") is True


def test_freeze_key_returns_false_when_already_frozen(vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    assert freeze_key(vault_dir, "MY_KEY") is False


def test_is_frozen_true_after_freeze(vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    assert is_frozen(vault_dir, "MY_KEY") is True


def test_is_frozen_false_before_freeze(vault_dir):
    assert is_frozen(vault_dir, "MY_KEY") is False


def test_unfreeze_key_returns_true_when_found(vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    assert unfreeze_key(vault_dir, "MY_KEY") is True


def test_unfreeze_key_returns_false_when_not_frozen(vault_dir):
    assert unfreeze_key(vault_dir, "MY_KEY") is False


def test_is_frozen_false_after_unfreeze(vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    unfreeze_key(vault_dir, "MY_KEY")
    assert is_frozen(vault_dir, "MY_KEY") is False


def test_list_frozen_empty_when_none(vault_dir):
    assert list_frozen(vault_dir) == []


def test_list_frozen_returns_sorted_keys(vault_dir):
    freeze_key(vault_dir, "ZEBRA")
    freeze_key(vault_dir, "ALPHA")
    freeze_key(vault_dir, "MANGO")
    assert list_frozen(vault_dir) == ["ALPHA", "MANGO", "ZEBRA"]


def test_list_frozen_excludes_unfrozen_key(vault_dir):
    freeze_key(vault_dir, "KEY_A")
    freeze_key(vault_dir, "KEY_B")
    unfreeze_key(vault_dir, "KEY_A")
    assert list_frozen(vault_dir) == ["KEY_B"]


def test_freeze_guard_check_returns_none_for_unfrozen(vault_dir):
    guard = FreezeGuard(vault_dir)
    assert guard.check("MY_KEY") is None


def test_freeze_guard_check_returns_message_for_frozen(vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    guard = FreezeGuard(vault_dir)
    result = guard.check("MY_KEY")
    assert result is not None
    assert "MY_KEY" in result
    assert "frozen" in result


def test_multiple_keys_independent(vault_dir):
    freeze_key(vault_dir, "KEY_A")
    assert is_frozen(vault_dir, "KEY_A") is True
    assert is_frozen(vault_dir, "KEY_B") is False
