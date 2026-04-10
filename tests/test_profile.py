"""Tests for env_vault.profile."""

from __future__ import annotations

import pytest

from env_vault.profile import (
    assign_key,
    create_profile,
    delete_profile,
    get_profile_keys,
    key_profiles,
    list_profiles,
    unassign_key,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_create_profile_appears_in_list(vault_dir):
    create_profile(vault_dir, "dev")
    assert "dev" in list_profiles(vault_dir)


def test_create_profile_is_idempotent(vault_dir):
    create_profile(vault_dir, "dev")
    create_profile(vault_dir, "dev")  # should not raise
    assert list_profiles(vault_dir).count("dev") == 1


def test_list_profiles_sorted(vault_dir):
    create_profile(vault_dir, "staging")
    create_profile(vault_dir, "dev")
    create_profile(vault_dir, "prod")
    assert list_profiles(vault_dir) == ["dev", "prod", "staging"]


def test_delete_profile_returns_true_when_found(vault_dir):
    create_profile(vault_dir, "dev")
    assert delete_profile(vault_dir, "dev") is True
    assert "dev" not in list_profiles(vault_dir)


def test_delete_profile_returns_false_when_missing(vault_dir):
    assert delete_profile(vault_dir, "nonexistent") is False


def test_assign_key_adds_to_profile(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assert "DB_URL" in get_profile_keys(vault_dir, "dev")


def test_assign_key_creates_profile_implicitly(vault_dir):
    assign_key(vault_dir, "prod", "API_KEY")
    assert "prod" in list_profiles(vault_dir)


def test_assign_key_is_idempotent(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "dev", "DB_URL")
    assert get_profile_keys(vault_dir, "dev").count("DB_URL") == 1


def test_unassign_key_returns_true_when_found(vault_dir):
    assign_key(vault_dir, "dev", "SECRET")
    assert unassign_key(vault_dir, "dev", "SECRET") is True
    assert "SECRET" not in get_profile_keys(vault_dir, "dev")


def test_unassign_key_returns_false_when_missing(vault_dir):
    create_profile(vault_dir, "dev")
    assert unassign_key(vault_dir, "dev", "GHOST") is False


def test_get_profile_keys_missing_profile_returns_empty(vault_dir):
    assert get_profile_keys(vault_dir, "ghost") == []


def test_key_profiles_returns_all_matching(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "staging", "DB_URL")
    assign_key(vault_dir, "prod", "OTHER")
    result = key_profiles(vault_dir, "DB_URL")
    assert result == ["dev", "staging"]


def test_key_profiles_returns_empty_when_unassigned(vault_dir):
    create_profile(vault_dir, "dev")
    assert key_profiles(vault_dir, "UNSET") == []
