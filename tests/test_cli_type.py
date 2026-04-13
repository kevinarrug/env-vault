"""Tests for env_vault.cli_type."""
import pytest
from click.testing import CliRunner

from env_vault.cli_type import type_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(type_cmd, ["set", "PORT", "int", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Set" in result.output
    assert "PORT" in result.output


def test_set_reports_updated(runner, vault_dir):
    runner.invoke(type_cmd, ["set", "PORT", "int", "--vault-dir", vault_dir])
    result = runner.invoke(type_cmd, ["set", "PORT", "string", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_set_invalid_type_exits_nonzero(runner, vault_dir):
    result = runner.invoke(type_cmd, ["set", "K", "datetime", "--vault-dir", vault_dir])
    assert result.exit_code != 0
    assert "Invalid type" in result.output


def test_get_existing_key(runner, vault_dir):
    runner.invoke(type_cmd, ["set", "DEBUG", "bool", "--vault-dir", vault_dir])
    result = runner.invoke(type_cmd, ["get", "DEBUG", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "bool" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(type_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_remove_existing_type(runner, vault_dir):
    runner.invoke(type_cmd, ["set", "FOO", "float", "--vault-dir", vault_dir])
    result = runner.invoke(type_cmd, ["remove", "FOO", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_type(runner, vault_dir):
    result = runner.invoke(type_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No type annotation" in result.output


def test_list_shows_types(runner, vault_dir):
    runner.invoke(type_cmd, ["set", "A", "int", "--vault-dir", vault_dir])
    runner.invoke(type_cmd, ["set", "B", "bool", "--vault-dir", vault_dir])
    result = runner.invoke(type_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A: int" in result.output
    assert "B: bool" in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(type_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No type annotations" in result.output


def test_check_valid_value(runner, vault_dir):
    runner.invoke(type_cmd, ["set", "PORT", "int", "--vault-dir", vault_dir])
    result = runner.invoke(type_cmd, ["check", "PORT", "8080", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_invalid_value(runner, vault_dir):
    runner.invoke(type_cmd, ["set", "PORT", "int", "--vault-dir", vault_dir])
    result = runner.invoke(type_cmd, ["check", "PORT", "notanint", "--vault-dir", vault_dir])
    assert result.exit_code != 0
