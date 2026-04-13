"""Tests for env_vault.env_visibility."""
import pytest
from pathlib import Path
from env_vault.env_visibility import (
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
    keys_with_level,
)


@pytest.fixture
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_set_visibility_returns_true_when_new(vault_dir):
    assert set_visibility(vault_dir, "API_KEY", "private") is True


def test_set_visibility_returns_false_when_unchanged(vault_dir):
    set_visibility(vault_dir, "API_KEY", "private")
    assert set_visibility(vault_dir, "API_KEY", "private") is False


def test_set_visibility_returns_true_when_changed(vault_dir):
    set_visibility(vault_dir, "API_KEY", "private")
    assert set_visibility(vault_dir, "API_KEY", "public") is True


def test_get_visibility_returns_level(vault_dir):
    set_visibility(vault_dir, "DB_PASS", "internal")
    assert get_visibility(vault_dir, "DB_PASS") == "internal"


def test_get_visibility_missing_returns_none(vault_dir):
    assert get_visibility(vault_dir, "MISSING") is None


def test_set_visibility_invalid_level_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        set_visibility(vault_dir, "KEY", "secret")


def test_remove_visibility_returns_true_when_found(vault_dir):
    set_visibility(vault_dir, "TOKEN", "private")
    assert remove_visibility(vault_dir, "TOKEN") is True


def test_remove_visibility_returns_false_when_missing(vault_dir):
    assert remove_visibility(vault_dir, "GHOST") is False


def test_remove_visibility_clears_key(vault_dir):
    set_visibility(vault_dir, "TOKEN", "private")
    remove_visibility(vault_dir, "TOKEN")
    assert get_visibility(vault_dir, "TOKEN") is None


def test_list_visibility_returns_all(vault_dir):
    set_visibility(vault_dir, "A", "public")
    set_visibility(vault_dir, "B", "private")
    result = list_visibility(vault_dir)
    assert result == {"A": "public", "B": "private"}


def test_list_visibility_empty(vault_dir):
    assert list_visibility(vault_dir) == {}


def test_keys_with_level_returns_matching(vault_dir):
    set_visibility(vault_dir, "A", "public")
    set_visibility(vault_dir, "B", "private")
    set_visibility(vault_dir, "C", "public")
    result = keys_with_level(vault_dir, "public")
    assert sorted(result) == ["A", "C"]


def test_keys_with_level_empty_when_none_match(vault_dir):
    set_visibility(vault_dir, "A", "private")
    assert keys_with_level(vault_dir, "public") == []


def test_keys_with_level_invalid_raises(vault_dir):
    with pytest.raises(ValueError):
        keys_with_level(vault_dir, "unknown")
