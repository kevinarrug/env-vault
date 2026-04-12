"""Tests for env_vault.env_label."""

import pytest

from env_vault.env_label import (
    get_label,
    keys_with_label,
    list_labels,
    remove_label,
    set_label,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_label_returns_true_when_new(vault_dir):
    assert set_label(vault_dir, "DB_HOST", "Database host") is True


def test_set_label_returns_false_when_same(vault_dir):
    set_label(vault_dir, "DB_HOST", "Database host")
    assert set_label(vault_dir, "DB_HOST", "Database host") is False


def test_set_label_returns_true_when_changed(vault_dir):
    set_label(vault_dir, "DB_HOST", "Old label")
    assert set_label(vault_dir, "DB_HOST", "New label") is True


def test_get_label_returns_value(vault_dir):
    set_label(vault_dir, "API_KEY", "API secret key")
    assert get_label(vault_dir, "API_KEY") == "API secret key"


def test_get_label_missing_returns_none(vault_dir):
    assert get_label(vault_dir, "MISSING") is None


def test_remove_label_returns_true_when_found(vault_dir):
    set_label(vault_dir, "DB_HOST", "Database host")
    assert remove_label(vault_dir, "DB_HOST") is True


def test_remove_label_returns_false_when_missing(vault_dir):
    assert remove_label(vault_dir, "NONEXISTENT") is False


def test_remove_label_clears_entry(vault_dir):
    set_label(vault_dir, "DB_HOST", "Database host")
    remove_label(vault_dir, "DB_HOST")
    assert get_label(vault_dir, "DB_HOST") is None


def test_list_labels_returns_all(vault_dir):
    set_label(vault_dir, "B_KEY", "B label")
    set_label(vault_dir, "A_KEY", "A label")
    result = list_labels(vault_dir)
    assert result == {"A_KEY": "A label", "B_KEY": "B label"}


def test_list_labels_empty_when_none(vault_dir):
    assert list_labels(vault_dir) == {}


def test_list_labels_sorted_by_key(vault_dir):
    set_label(vault_dir, "Z_KEY", "Z")
    set_label(vault_dir, "A_KEY", "A")
    set_label(vault_dir, "M_KEY", "M")
    keys = list(list_labels(vault_dir).keys())
    assert keys == sorted(keys)


def test_keys_with_label_returns_matches(vault_dir):
    set_label(vault_dir, "DB_HOST", "database")
    set_label(vault_dir, "DB_PORT", "database")
    set_label(vault_dir, "API_KEY", "api")
    result = keys_with_label(vault_dir, "database")
    assert result == ["DB_HOST", "DB_PORT"]


def test_keys_with_label_empty_when_no_match(vault_dir):
    set_label(vault_dir, "API_KEY", "api")
    assert keys_with_label(vault_dir, "nonexistent") == []


def test_set_label_empty_string_raises(vault_dir):
    with pytest.raises(ValueError, match="Label must not be empty"):
        set_label(vault_dir, "DB_HOST", "")
