"""Tests for env_vault.cli_sensitivity."""
import pytest
from click.testing import CliRunner

from env_vault.cli_sensitivity import sensitivity_cmd
from env_vault.env_sensitivity import set_sensitivity


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(sensitivity_cmd, ["set", "API_KEY", "secret", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "secret" in result.output
    assert "API_KEY" in result.output


def test_set_reports_no_change(runner, vault_dir):
    runner.invoke(sensitivity_cmd, ["set", "API_KEY", "secret", "--vault-dir", vault_dir])
    result = runner.invoke(sensitivity_cmd, ["set", "API_KEY", "secret", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "no change" in result.output


def test_get_existing_key(runner, vault_dir):
    set_sensitivity(vault_dir, "DB_PASS", "confidential")
    result = runner.invoke(sensitivity_cmd, ["get", "DB_PASS", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "confidential" in result.output


def test_get_missing_key(runner, vault_dir):
    result = runner.invoke(sensitivity_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No sensitivity level" in result.output


def test_remove_existing_key(runner, vault_dir):
    set_sensitivity(vault_dir, "TOKEN", "secret")
    result = runner.invoke(sensitivity_cmd, ["remove", "TOKEN", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_key(runner, vault_dir):
    result = runner.invoke(sensitivity_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No sensitivity level" in result.output


def test_list_shows_all(runner, vault_dir):
    set_sensitivity(vault_dir, "A", "public")
    set_sensitivity(vault_dir, "B", "secret")
    result = runner.invoke(sensitivity_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A: public" in result.output
    assert "B: secret" in result.output


def test_list_filtered_by_level(runner, vault_dir):
    set_sensitivity(vault_dir, "A", "public")
    set_sensitivity(vault_dir, "B", "secret")
    result = runner.invoke(sensitivity_cmd, ["list", "--level", "secret", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "B: secret" in result.output
    assert "public" not in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(sensitivity_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No sensitivity levels" in result.output
