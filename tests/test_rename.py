"""Tests for env_vault.rename."""

import pytest

from env_vault.vault import Vault
from env_vault.rename import rename_key, RenameResult


PASS = "test-passphrase"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault.json"))
    v.set("DB_HOST", "localhost", PASS)
    v.set("DB_PORT", "5432", PASS)
    return v


def test_rename_returns_result_type(vault):
    result = rename_key(vault, PASS, "DB_HOST", "DATABASE_HOST")
    assert isinstance(result, RenameResult)


def test_rename_success_flag(vault):
    result = rename_key(vault, PASS, "DB_HOST", "DATABASE_HOST")
    assert result.success is True


def test_rename_new_key_exists(vault):
    result = rename_key(vault, PASS, "DB_HOST", "DATABASE_HOST")
    assert "DATABASE_HOST" in vault.list_keys()


def test_rename_old_key_removed(vault):
    rename_key(vault, PASS, "DB_HOST", "DATABASE_HOST")
    assert "DB_HOST" not in vault.list_keys()


def test_rename_value_preserved(vault):
    rename_key(vault, PASS, "DB_HOST", "DATABASE_HOST")
    assert vault.get("DATABASE_HOST", PASS) == "localhost"


def test_rename_missing_key_fails(vault):
    result = rename_key(vault, PASS, "MISSING_KEY", "NEW_KEY")
    assert result.success is False
    assert "not found" in result.message


def test_rename_existing_target_fails_without_overwrite(vault):
    result = rename_key(vault, PASS, "DB_HOST", "DB_PORT")
    assert result.success is False
    assert "already exists" in result.message


def test_rename_existing_target_succeeds_with_overwrite(vault):
    result = rename_key(vault, PASS, "DB_HOST", "DB_PORT", overwrite=True)
    assert result.success is True
    assert vault.get("DB_PORT", PASS) == "localhost"


def test_rename_str_success(vault):
    result = rename_key(vault, PASS, "DB_HOST", "DATABASE_HOST")
    assert "->" in str(result)
    assert "DATABASE_HOST" in str(result)


def test_rename_str_failure(vault):
    result = rename_key(vault, PASS, "NO_SUCH_KEY", "X")
    assert "failed" in str(result).lower()
