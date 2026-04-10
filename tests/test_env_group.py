"""Tests for env_vault.env_group."""

import pytest

from env_vault.env_group import (
    add_to_group,
    delete_group,
    get_groups_for_key,
    get_keys_in_group,
    list_groups,
    remove_from_group,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_to_group_returns_true_when_new(vault_dir):
    assert add_to_group(vault_dir, "backend", "DB_URL") is True


def test_add_to_group_returns_false_when_duplicate(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    assert add_to_group(vault_dir, "backend", "DB_URL") is False


def test_get_keys_in_group_returns_members(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    add_to_group(vault_dir, "backend", "API_KEY")
    assert get_keys_in_group(vault_dir, "backend") == ["API_KEY", "DB_URL"]


def test_get_keys_in_group_missing_group_returns_empty(vault_dir):
    assert get_keys_in_group(vault_dir, "nonexistent") == []


def test_get_groups_for_key_returns_all_groups(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    add_to_group(vault_dir, "shared", "DB_URL")
    groups = get_groups_for_key(vault_dir, "DB_URL")
    assert groups == ["backend", "shared"]


def test_get_groups_for_key_not_member_returns_empty(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    assert get_groups_for_key(vault_dir, "UNKNOWN_KEY") == []


def test_list_groups_sorted(vault_dir):
    add_to_group(vault_dir, "zebra", "K1")
    add_to_group(vault_dir, "alpha", "K2")
    assert list_groups(vault_dir) == ["alpha", "zebra"]


def test_list_groups_empty(vault_dir):
    assert list_groups(vault_dir) == []


def test_remove_from_group_returns_true_when_found(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    assert remove_from_group(vault_dir, "backend", "DB_URL") is True


def test_remove_from_group_returns_false_when_missing(vault_dir):
    assert remove_from_group(vault_dir, "backend", "DB_URL") is False


def test_remove_last_key_deletes_group(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    remove_from_group(vault_dir, "backend", "DB_URL")
    assert "backend" not in list_groups(vault_dir)


def test_delete_group_returns_true_when_found(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    assert delete_group(vault_dir, "backend") is True


def test_delete_group_returns_false_when_missing(vault_dir):
    assert delete_group(vault_dir, "backend") is False


def test_delete_group_removes_all_keys(vault_dir):
    add_to_group(vault_dir, "backend", "DB_URL")
    add_to_group(vault_dir, "backend", "API_KEY")
    delete_group(vault_dir, "backend")
    assert get_keys_in_group(vault_dir, "backend") == []
