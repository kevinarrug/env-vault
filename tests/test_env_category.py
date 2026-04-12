"""Tests for env_vault.env_category."""
import pytest
from env_vault.env_category import (
    set_category,
    get_category,
    remove_category,
    list_categories,
    keys_in_category,
    all_category_names,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_category_returns_true_when_new(vault_dir):
    assert set_category(vault_dir, "DB_HOST", "database") is True


def test_set_category_returns_false_when_same(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    assert set_category(vault_dir, "DB_HOST", "database") is False


def test_set_category_returns_true_when_changed(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    assert set_category(vault_dir, "DB_HOST", "network") is True


def test_get_category_returns_value(vault_dir):
    set_category(vault_dir, "API_KEY", "auth")
    assert get_category(vault_dir, "API_KEY") == "auth"


def test_get_category_missing_returns_none(vault_dir):
    assert get_category(vault_dir, "NONEXISTENT") is None


def test_remove_category_returns_true_when_found(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    assert remove_category(vault_dir, "DB_HOST") is True


def test_remove_category_returns_false_when_missing(vault_dir):
    assert remove_category(vault_dir, "NONEXISTENT") is False


def test_remove_category_clears_entry(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    remove_category(vault_dir, "DB_HOST")
    assert get_category(vault_dir, "DB_HOST") is None


def test_list_categories_returns_all(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    set_category(vault_dir, "API_KEY", "auth")
    result = list_categories(vault_dir)
    assert result == {"DB_HOST": "database", "API_KEY": "auth"}


def test_list_categories_empty_when_none(vault_dir):
    assert list_categories(vault_dir) == {}


def test_keys_in_category_returns_matching_keys(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    set_category(vault_dir, "DB_PORT", "database")
    set_category(vault_dir, "API_KEY", "auth")
    result = keys_in_category(vault_dir, "database")
    assert result == ["DB_HOST", "DB_PORT"]


def test_keys_in_category_empty_for_unknown(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    assert keys_in_category(vault_dir, "nonexistent") == []


def test_keys_in_category_sorted(vault_dir):
    set_category(vault_dir, "Z_KEY", "misc")
    set_category(vault_dir, "A_KEY", "misc")
    set_category(vault_dir, "M_KEY", "misc")
    assert keys_in_category(vault_dir, "misc") == ["A_KEY", "M_KEY", "Z_KEY"]


def test_all_category_names_returns_unique_sorted(vault_dir):
    set_category(vault_dir, "DB_HOST", "database")
    set_category(vault_dir, "DB_PORT", "database")
    set_category(vault_dir, "API_KEY", "auth")
    assert all_category_names(vault_dir) == ["auth", "database"]


def test_all_category_names_empty_when_none(vault_dir):
    assert all_category_names(vault_dir) == []
