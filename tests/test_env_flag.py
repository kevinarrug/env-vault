"""Tests for env_vault.env_flag."""
import pytest
from pathlib import Path
from env_vault.env_flag import set_flag, remove_flag, get_flag, list_flags, keys_with_flag


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_flag_returns_true_when_new(vault_dir):
    assert set_flag(vault_dir, "MY_KEY", True) is True


def test_set_flag_returns_false_when_unchanged(vault_dir):
    set_flag(vault_dir, "MY_KEY", True)
    assert set_flag(vault_dir, "MY_KEY", True) is False


def test_set_flag_returns_true_when_changed(vault_dir):
    set_flag(vault_dir, "MY_KEY", True)
    assert set_flag(vault_dir, "MY_KEY", False) is True


def test_get_flag_returns_value(vault_dir):
    set_flag(vault_dir, "MY_KEY", False)
    assert get_flag(vault_dir, "MY_KEY") is False


def test_get_flag_missing_returns_none(vault_dir):
    assert get_flag(vault_dir, "MISSING") is None


def test_remove_flag_returns_true_when_found(vault_dir):
    set_flag(vault_dir, "MY_KEY", True)
    assert remove_flag(vault_dir, "MY_KEY") is True


def test_remove_flag_returns_false_when_missing(vault_dir):
    assert remove_flag(vault_dir, "GHOST") is False


def test_remove_flag_deletes_entry(vault_dir):
    set_flag(vault_dir, "MY_KEY", True)
    remove_flag(vault_dir, "MY_KEY")
    assert get_flag(vault_dir, "MY_KEY") is None


def test_list_flags_returns_all(vault_dir):
    set_flag(vault_dir, "A", True)
    set_flag(vault_dir, "B", False)
    result = list_flags(vault_dir)
    assert result == {"A": True, "B": False}


def test_list_flags_empty(vault_dir):
    assert list_flags(vault_dir) == {}


def test_keys_with_flag_true(vault_dir):
    set_flag(vault_dir, "A", True)
    set_flag(vault_dir, "B", False)
    set_flag(vault_dir, "C", True)
    assert sorted(keys_with_flag(vault_dir, True)) == ["A", "C"]


def test_keys_with_flag_false(vault_dir):
    set_flag(vault_dir, "A", True)
    set_flag(vault_dir, "B", False)
    assert keys_with_flag(vault_dir, False) == ["B"]


def test_flags_persisted_across_calls(vault_dir):
    set_flag(vault_dir, "PERSIST", True)
    assert get_flag(vault_dir, "PERSIST") is True
