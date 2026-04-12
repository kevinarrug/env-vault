"""Tests for env_vault.env_owner."""
from __future__ import annotations

import pytest

from env_vault.env_owner import (
    get_all_owners,
    get_owner,
    list_owned_by,
    remove_owner,
    set_owner,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_owner_returns_true_when_new(vault_dir):
    assert set_owner(vault_dir, "API_KEY", "alice") is True


def test_set_owner_returns_false_when_unchanged(vault_dir):
    set_owner(vault_dir, "API_KEY", "alice")
    assert set_owner(vault_dir, "API_KEY", "alice") is False


def test_set_owner_returns_true_when_changed(vault_dir):
    set_owner(vault_dir, "API_KEY", "alice")
    assert set_owner(vault_dir, "API_KEY", "bob") is True


def test_get_owner_returns_value(vault_dir):
    set_owner(vault_dir, "DB_PASS", "charlie")
    assert get_owner(vault_dir, "DB_PASS") == "charlie"


def test_get_owner_missing_returns_none(vault_dir):
    assert get_owner(vault_dir, "MISSING") is None


def test_remove_owner_returns_true_when_found(vault_dir):
    set_owner(vault_dir, "SECRET", "alice")
    assert remove_owner(vault_dir, "SECRET") is True


def test_remove_owner_returns_false_when_missing(vault_dir):
    assert remove_owner(vault_dir, "GHOST") is False


def test_remove_owner_clears_record(vault_dir):
    set_owner(vault_dir, "TOKEN", "alice")
    remove_owner(vault_dir, "TOKEN")
    assert get_owner(vault_dir, "TOKEN") is None


def test_list_owned_by_returns_sorted_keys(vault_dir):
    set_owner(vault_dir, "Z_KEY", "alice")
    set_owner(vault_dir, "A_KEY", "alice")
    set_owner(vault_dir, "OTHER", "bob")
    assert list_owned_by(vault_dir, "alice") == ["A_KEY", "Z_KEY"]


def test_list_owned_by_excludes_other_owners(vault_dir):
    set_owner(vault_dir, "X", "alice")
    set_owner(vault_dir, "Y", "bob")
    assert "Y" not in list_owned_by(vault_dir, "alice")


def test_list_owned_by_empty_when_no_match(vault_dir):
    set_owner(vault_dir, "K", "alice")
    assert list_owned_by(vault_dir, "nobody") == []


def test_get_all_owners_returns_full_mapping(vault_dir):
    set_owner(vault_dir, "A", "alice")
    set_owner(vault_dir, "B", "bob")
    result = get_all_owners(vault_dir)
    assert result == {"A": "alice", "B": "bob"}


def test_get_all_owners_empty_when_none(vault_dir):
    assert get_all_owners(vault_dir) == {}
