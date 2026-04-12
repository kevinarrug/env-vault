"""Tests for env_vault.env_access."""
import pytest

from env_vault.env_access import (
    can,
    clear_key,
    get_permissions,
    grant,
    list_accessible_keys,
    revoke,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_grant_returns_true_when_new(vault_dir):
    assert grant(vault_dir, "DB_PASSWORD", "admin", "read") is True


def test_grant_returns_false_when_duplicate(vault_dir):
    grant(vault_dir, "DB_PASSWORD", "admin", "read")
    assert grant(vault_dir, "DB_PASSWORD", "admin", "read") is False


def test_grant_invalid_permission_raises(vault_dir):
    with pytest.raises(ValueError, match="permission must be"):
        grant(vault_dir, "KEY", "admin", "execute")


def test_can_returns_true_after_grant(vault_dir):
    grant(vault_dir, "API_KEY", "dev", "read")
    assert can(vault_dir, "API_KEY", "dev", "read") is True


def test_can_returns_false_before_grant(vault_dir):
    assert can(vault_dir, "API_KEY", "dev", "read") is False


def test_can_read_does_not_imply_write(vault_dir):
    grant(vault_dir, "SECRET", "viewer", "read")
    assert can(vault_dir, "SECRET", "viewer", "write") is False


def test_revoke_returns_true_when_found(vault_dir):
    grant(vault_dir, "TOKEN", "ci", "write")
    assert revoke(vault_dir, "TOKEN", "ci", "write") is True


def test_revoke_returns_false_when_not_present(vault_dir):
    assert revoke(vault_dir, "TOKEN", "ci", "write") is False


def test_revoke_removes_permission(vault_dir):
    grant(vault_dir, "TOKEN", "ci", "write")
    revoke(vault_dir, "TOKEN", "ci", "write")
    assert can(vault_dir, "TOKEN", "ci", "write") is False


def test_get_permissions_returns_all_roles(vault_dir):
    grant(vault_dir, "DB_URL", "admin", "read")
    grant(vault_dir, "DB_URL", "admin", "write")
    grant(vault_dir, "DB_URL", "readonly", "read")
    perms = get_permissions(vault_dir, "DB_URL")
    assert set(perms["admin"]) == {"read", "write"}
    assert perms["readonly"] == ["read"]


def test_get_permissions_missing_key_returns_empty(vault_dir):
    assert get_permissions(vault_dir, "NONEXISTENT") == {}


def test_list_accessible_keys_returns_matching(vault_dir):
    grant(vault_dir, "KEY_A", "dev", "read")
    grant(vault_dir, "KEY_B", "dev", "read")
    grant(vault_dir, "KEY_C", "dev", "write")
    keys = list_accessible_keys(vault_dir, "dev", "read")
    assert "KEY_A" in keys
    assert "KEY_B" in keys
    assert "KEY_C" not in keys


def test_list_accessible_keys_empty_when_none(vault_dir):
    assert list_accessible_keys(vault_dir, "ghost", "read") == []


def test_clear_key_returns_true_when_found(vault_dir):
    grant(vault_dir, "OLD_KEY", "admin", "read")
    assert clear_key(vault_dir, "OLD_KEY") is True


def test_clear_key_returns_false_when_missing(vault_dir):
    assert clear_key(vault_dir, "GHOST_KEY") is False


def test_clear_key_removes_all_entries(vault_dir):
    grant(vault_dir, "PURGE_ME", "admin", "read")
    grant(vault_dir, "PURGE_ME", "dev", "write")
    clear_key(vault_dir, "PURGE_ME")
    assert get_permissions(vault_dir, "PURGE_ME") == {}
