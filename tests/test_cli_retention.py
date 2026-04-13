"""Tests for env_vault.cli_retention CLI commands."""
import time
import pytest
from click.testing import CliRunner
from env_vault.cli_retention import retention_cmd
from env_vault import env_retention


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(retention_cmd, ["set", "API_KEY", "30", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Set" in result.output
    assert "API_KEY" in result.output


def test_set_reports_updated(runner, vault_dir):
    runner.invoke(retention_cmd, ["set", "API_KEY", "30", "--vault-dir", vault_dir])
    result = runner.invoke(retention_cmd, ["set", "API_KEY", "60", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_set_invalid_days_exits_nonzero(runner, vault_dir):
    result = runner.invoke(retention_cmd, ["set", "API_KEY", "0", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_get_existing_key(runner, vault_dir):
    env_retention.set_retention(vault_dir, "SECRET", 7)
    result = runner.invoke(retention_cmd, ["get", "SECRET", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "7" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(retention_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_remove_existing_key(runner, vault_dir):
    env_retention.set_retention(vault_dir, "TOKEN", 14)
    result = runner.invoke(retention_cmd, ["remove", "TOKEN", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_key(runner, vault_dir):
    result = runner.invoke(retention_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No retention" in result.output


def test_list_shows_policies(runner, vault_dir):
    env_retention.set_retention(vault_dir, "A", 10)
    env_retention.set_retention(vault_dir, "B", 20)
    result = runner.invoke(retention_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_list_empty_reports_none(runner, vault_dir):
    result = runner.invoke(retention_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No retention" in result.output


def test_list_expired_flag(runner, vault_dir):
    env_retention.set_retention(vault_dir, "STALE", 1)
    data = env_retention._load_retention(vault_dir)
    data["STALE"]["set_at"] = time.time() - 5 * 86400
    env_retention._save_retention(vault_dir, data)
    result = runner.invoke(retention_cmd, ["list", "--expired", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "STALE" in result.output
