"""Tests for env_vault.env_namespace."""
import pytest

from env_vault.env_namespace import (
    set_namespace,
    get_namespace,
    remove_namespace,
    list_namespaces,
    keys_in_namespace,
    list_all_namespaces,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_namespace_returns_true_when_new(vault_dir):
    assert set_namespace(vault_dir, "DB_HOST", "database") is True


def test_set_namespace_returns_false_when_unchanged(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    assert set_namespace(vault_dir, "DB_HOST", "database") is False


def test_set_namespace_returns_true_when_changed(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    assert set_namespace(vault_dir, "DB_HOST", "infra") is True


def test_get_namespace_returns_value(vault_dir):
    set_namespace(vault_dir, "API_KEY", "auth")
    assert get_namespace(vault_dir, "API_KEY") == "auth"


def test_get_namespace_missing_returns_none(vault_dir):
    assert get_namespace(vault_dir, "MISSING") is None


def test_remove_namespace_returns_true_when_found(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    assert remove_namespace(vault_dir, "DB_HOST") is True


def test_remove_namespace_returns_false_when_missing(vault_dir):
    assert remove_namespace(vault_dir, "GHOST") is False


def test_remove_namespace_clears_key(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    remove_namespace(vault_dir, "DB_HOST")
    assert get_namespace(vault_dir, "DB_HOST") is None


def test_list_namespaces_returns_all(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    set_namespace(vault_dir, "API_KEY", "auth")
    result = list_namespaces(vault_dir)
    assert result == {"DB_HOST": "database", "API_KEY": "auth"}


def test_list_namespaces_empty(vault_dir):
    assert list_namespaces(vault_dir) == {}


def test_keys_in_namespace_returns_members(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    set_namespace(vault_dir, "DB_PORT", "database")
    set_namespace(vault_dir, "API_KEY", "auth")
    assert keys_in_namespace(vault_dir, "database") == ["DB_HOST", "DB_PORT"]


def test_keys_in_namespace_missing_namespace_returns_empty(vault_dir):
    assert keys_in_namespace(vault_dir, "nonexistent") == []


def test_keys_in_namespace_sorted(vault_dir):
    set_namespace(vault_dir, "Z_KEY", "ns")
    set_namespace(vault_dir, "A_KEY", "ns")
    assert keys_in_namespace(vault_dir, "ns") == ["A_KEY", "Z_KEY"]


def test_list_all_namespaces_returns_unique_sorted(vault_dir):
    set_namespace(vault_dir, "DB_HOST", "database")
    set_namespace(vault_dir, "DB_PORT", "database")
    set_namespace(vault_dir, "API_KEY", "auth")
    assert list_all_namespaces(vault_dir) == ["auth", "database"]


def test_list_all_namespaces_empty(vault_dir):
    assert list_all_namespaces(vault_dir) == []
