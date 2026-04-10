"""Unit tests for env_vault.alias."""

from __future__ import annotations

import pytest

from env_vault.alias import (
    add_alias,
    list_aliases,
    remove_alias,
    rename_alias,
    resolve_alias,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_alias_returns_true_when_new(vault_dir):
    assert add_alias(vault_dir, "db_pass", "DATABASE_PASSWORD") is True


def test_add_alias_returns_false_when_updated(vault_dir):
    add_alias(vault_dir, "db_pass", "DATABASE_PASSWORD")
    assert add_alias(vault_dir, "db_pass", "DB_PASSWORD") is False


def test_resolve_alias_returns_target(vault_dir):
    add_alias(vault_dir, "db_pass", "DATABASE_PASSWORD")
    assert resolve_alias(vault_dir, "db_pass") == "DATABASE_PASSWORD"


def test_resolve_alias_missing_returns_none(vault_dir):
    assert resolve_alias(vault_dir, "nonexistent") is None


def test_remove_alias_returns_true_when_found(vault_dir):
    add_alias(vault_dir, "x", "X_KEY")
    assert remove_alias(vault_dir, "x") is True


def test_remove_alias_returns_false_when_missing(vault_dir):
    assert remove_alias(vault_dir, "ghost") is False


def test_remove_alias_makes_it_unresolvable(vault_dir):
    add_alias(vault_dir, "x", "X_KEY")
    remove_alias(vault_dir, "x")
    assert resolve_alias(vault_dir, "x") is None


def test_list_aliases_empty(vault_dir):
    assert list_aliases(vault_dir) == []


def test_list_aliases_sorted(vault_dir):
    add_alias(vault_dir, "z_alias", "Z_KEY")
    add_alias(vault_dir, "a_alias", "A_KEY")
    entries = list_aliases(vault_dir)
    assert [e["alias"] for e in entries] == ["a_alias", "z_alias"]


def test_list_aliases_contains_target(vault_dir):
    add_alias(vault_dir, "token", "API_TOKEN")
    entries = list_aliases(vault_dir)
    assert entries[0]["target"] == "API_TOKEN"


def test_rename_alias_returns_true_on_success(vault_dir):
    add_alias(vault_dir, "old", "SOME_KEY")
    assert rename_alias(vault_dir, "old", "new") is True


def test_rename_alias_old_no_longer_exists(vault_dir):
    add_alias(vault_dir, "old", "SOME_KEY")
    rename_alias(vault_dir, "old", "new")
    assert resolve_alias(vault_dir, "old") is None


def test_rename_alias_new_resolves_to_same_target(vault_dir):
    add_alias(vault_dir, "old", "SOME_KEY")
    rename_alias(vault_dir, "old", "new")
    assert resolve_alias(vault_dir, "new") == "SOME_KEY"


def test_rename_alias_missing_returns_false(vault_dir):
    assert rename_alias(vault_dir, "ghost", "new") is False
