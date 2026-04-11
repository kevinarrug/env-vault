"""Tests for env_vault.env_scope."""
from __future__ import annotations

import pytest

from env_vault.env_scope import (
    add_to_scope,
    delete_scope,
    get_keys_in_scope,
    get_scopes_for_key,
    list_scopes,
    remove_from_scope,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_to_scope_returns_true_when_new(vault_dir):
    assert add_to_scope(vault_dir, "dev", "DB_URL") is True


def test_add_to_scope_returns_false_when_duplicate(vault_dir):
    add_to_scope(vault_dir, "dev", "DB_URL")
    assert add_to_scope(vault_dir, "dev", "DB_URL") is False


def test_get_keys_in_scope_returns_members(vault_dir):
    add_to_scope(vault_dir, "prod", "API_KEY")
    add_to_scope(vault_dir, "prod", "SECRET")
    keys = get_keys_in_scope(vault_dir, "prod")
    assert "API_KEY" in keys
    assert "SECRET" in keys


def test_get_keys_in_scope_missing_scope_returns_empty(vault_dir):
    assert get_keys_in_scope(vault_dir, "nonexistent") == []


def test_remove_from_scope_returns_true_when_found(vault_dir):
    add_to_scope(vault_dir, "dev", "DB_URL")
    assert remove_from_scope(vault_dir, "dev", "DB_URL") is True


def test_remove_from_scope_returns_false_when_missing(vault_dir):
    assert remove_from_scope(vault_dir, "dev", "GHOST") is False


def test_remove_from_scope_key_no_longer_present(vault_dir):
    add_to_scope(vault_dir, "dev", "DB_URL")
    remove_from_scope(vault_dir, "dev", "DB_URL")
    assert "DB_URL" not in get_keys_in_scope(vault_dir, "dev")


def test_remove_last_key_deletes_scope(vault_dir):
    add_to_scope(vault_dir, "staging", "ONLY_KEY")
    remove_from_scope(vault_dir, "staging", "ONLY_KEY")
    assert "staging" not in list_scopes(vault_dir)


def test_get_scopes_for_key_returns_all_scopes(vault_dir):
    add_to_scope(vault_dir, "dev", "DB_URL")
    add_to_scope(vault_dir, "prod", "DB_URL")
    scopes = get_scopes_for_key(vault_dir, "DB_URL")
    assert "dev" in scopes
    assert "prod" in scopes


def test_get_scopes_for_key_missing_returns_empty(vault_dir):
    assert get_scopes_for_key(vault_dir, "UNKNOWN") == []


def test_list_scopes_sorted(vault_dir):
    add_to_scope(vault_dir, "prod", "A")
    add_to_scope(vault_dir, "dev", "B")
    add_to_scope(vault_dir, "staging", "C")
    assert list_scopes(vault_dir) == ["dev", "prod", "staging"]


def test_list_scopes_empty(vault_dir):
    assert list_scopes(vault_dir) == []


def test_delete_scope_returns_true_when_found(vault_dir):
    add_to_scope(vault_dir, "dev", "KEY")
    assert delete_scope(vault_dir, "dev") is True


def test_delete_scope_returns_false_when_missing(vault_dir):
    assert delete_scope(vault_dir, "ghost") is False


def test_delete_scope_removes_all_keys(vault_dir):
    add_to_scope(vault_dir, "dev", "A")
    add_to_scope(vault_dir, "dev", "B")
    delete_scope(vault_dir, "dev")
    assert get_keys_in_scope(vault_dir, "dev") == []
