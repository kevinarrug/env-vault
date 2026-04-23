"""Tests for env_vault.env_maturity."""
import pytest
from pathlib import Path
from env_vault.env_maturity import (
    set_maturity,
    get_maturity,
    remove_maturity,
    list_maturity,
    get_keys_by_level,
    VALID_LEVELS,
)


@pytest.fixture
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_set_maturity_returns_true_when_new(vault_dir):
    assert set_maturity(vault_dir, "API_KEY", "stable") is True


def test_set_maturity_returns_false_when_unchanged(vault_dir):
    set_maturity(vault_dir, "API_KEY", "stable")
    assert set_maturity(vault_dir, "API_KEY", "stable") is False


def test_set_maturity_returns_true_when_changed(vault_dir):
    set_maturity(vault_dir, "API_KEY", "beta")
    assert set_maturity(vault_dir, "API_KEY", "stable") is True


def test_get_maturity_returns_value(vault_dir):
    set_maturity(vault_dir, "DB_URL", "experimental")
    assert get_maturity(vault_dir, "DB_URL") == "experimental"


def test_get_maturity_missing_returns_none(vault_dir):
    assert get_maturity(vault_dir, "MISSING") is None


def test_invalid_level_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid maturity level"):
        set_maturity(vault_dir, "KEY", "unknown")


def test_all_valid_levels_accepted(vault_dir):
    for level in VALID_LEVELS:
        assert set_maturity(vault_dir, f"KEY_{level.upper()}", level) is True


def test_remove_maturity_returns_true_when_found(vault_dir):
    set_maturity(vault_dir, "API_KEY", "stable")
    assert remove_maturity(vault_dir, "API_KEY") is True


def test_remove_maturity_returns_false_when_missing(vault_dir):
    assert remove_maturity(vault_dir, "GHOST") is False


def test_remove_maturity_clears_value(vault_dir):
    set_maturity(vault_dir, "API_KEY", "stable")
    remove_maturity(vault_dir, "API_KEY")
    assert get_maturity(vault_dir, "API_KEY") is None


def test_list_maturity_returns_all(vault_dir):
    set_maturity(vault_dir, "A", "stable")
    set_maturity(vault_dir, "B", "beta")
    result = list_maturity(vault_dir)
    assert result == {"A": "stable", "B": "beta"}


def test_list_maturity_empty_when_none(vault_dir):
    assert list_maturity(vault_dir) == {}


def test_get_keys_by_level_filters_correctly(vault_dir):
    set_maturity(vault_dir, "A", "stable")
    set_maturity(vault_dir, "B", "beta")
    set_maturity(vault_dir, "C", "stable")
    result = get_keys_by_level(vault_dir, "stable")
    assert result == ["A", "C"]


def test_get_keys_by_level_empty_when_none_match(vault_dir):
    set_maturity(vault_dir, "A", "beta")
    assert get_keys_by_level(vault_dir, "stable") == []
