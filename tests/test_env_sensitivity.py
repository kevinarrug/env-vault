"""Tests for env_vault.env_sensitivity."""
import pytest

from env_vault.env_sensitivity import (
    LEVELS,
    get_sensitivity,
    keys_at_level,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_sensitivity_returns_true_when_new(vault_dir):
    assert set_sensitivity(vault_dir, "DB_PASSWORD", "secret") is True


def test_set_sensitivity_returns_false_when_unchanged(vault_dir):
    set_sensitivity(vault_dir, "DB_PASSWORD", "secret")
    assert set_sensitivity(vault_dir, "DB_PASSWORD", "secret") is False


def test_set_sensitivity_returns_true_when_changed(vault_dir):
    set_sensitivity(vault_dir, "DB_PASSWORD", "internal")
    assert set_sensitivity(vault_dir, "DB_PASSWORD", "secret") is True


def test_get_sensitivity_returns_level(vault_dir):
    set_sensitivity(vault_dir, "API_KEY", "confidential")
    assert get_sensitivity(vault_dir, "API_KEY") == "confidential"


def test_get_sensitivity_missing_returns_none(vault_dir):
    assert get_sensitivity(vault_dir, "MISSING") is None


def test_set_invalid_level_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid level"):
        set_sensitivity(vault_dir, "KEY", "ultra-secret")


def test_remove_sensitivity_returns_true_when_found(vault_dir):
    set_sensitivity(vault_dir, "TOKEN", "secret")
    assert remove_sensitivity(vault_dir, "TOKEN") is True


def test_remove_sensitivity_returns_false_when_missing(vault_dir):
    assert remove_sensitivity(vault_dir, "GHOST") is False


def test_remove_sensitivity_clears_entry(vault_dir):
    set_sensitivity(vault_dir, "TOKEN", "secret")
    remove_sensitivity(vault_dir, "TOKEN")
    assert get_sensitivity(vault_dir, "TOKEN") is None


def test_list_sensitivity_returns_all(vault_dir):
    set_sensitivity(vault_dir, "A", "public")
    set_sensitivity(vault_dir, "B", "secret")
    result = list_sensitivity(vault_dir)
    assert result == {"A": "public", "B": "secret"}


def test_list_sensitivity_empty_when_none(vault_dir):
    assert list_sensitivity(vault_dir) == {}


def test_keys_at_level_returns_matching(vault_dir):
    set_sensitivity(vault_dir, "A", "secret")
    set_sensitivity(vault_dir, "B", "public")
    set_sensitivity(vault_dir, "C", "secret")
    assert keys_at_level(vault_dir, "secret") == ["A", "C"]


def test_keys_at_level_empty_when_none_match(vault_dir):
    set_sensitivity(vault_dir, "A", "public")
    assert keys_at_level(vault_dir, "secret") == []


def test_keys_at_level_invalid_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid level"):
        keys_at_level(vault_dir, "top-secret")


def test_levels_constant_has_expected_values():
    assert "public" in LEVELS
    assert "secret" in LEVELS
    assert len(LEVELS) == 4
