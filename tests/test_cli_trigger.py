"""Tests for env_vault.cli_trigger CLI commands."""
import pytest
from click.testing import CliRunner

from env_vault.cli_trigger import trigger_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_reports_added(runner, vault_dir):
    result = runner.invoke(
        trigger_cmd, ["add", "DB_URL", "echo hi", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "added" in result.output


def test_add_reports_already_registered(runner, vault_dir):
    runner.invoke(trigger_cmd, ["add", "DB_URL", "echo hi", "--vault-dir", vault_dir])
    result = runner.invoke(
        trigger_cmd, ["add", "DB_URL", "echo hi", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "already registered" in result.output


def test_remove_existing_trigger(runner, vault_dir):
    runner.invoke(trigger_cmd, ["add", "K", "cmd", "--vault-dir", vault_dir])
    result = runner.invoke(
        trigger_cmd, ["remove", "K", "cmd", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_trigger(runner, vault_dir):
    result = runner.invoke(
        trigger_cmd, ["remove", "K", "cmd", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "not found" in result.output


def test_list_shows_commands(runner, vault_dir):
    runner.invoke(trigger_cmd, ["add", "API", "notify", "--vault-dir", vault_dir])
    result = runner.invoke(trigger_cmd, ["list", "API", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "notify" in result.output


def test_list_no_triggers(runner, vault_dir):
    result = runner.invoke(trigger_cmd, ["list", "NONE", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No triggers" in result.output


def test_list_all_shows_keys(runner, vault_dir):
    runner.invoke(trigger_cmd, ["add", "A", "c1", "--vault-dir", vault_dir])
    runner.invoke(trigger_cmd, ["add", "B", "c2", "--vault-dir", vault_dir])
    result = runner.invoke(trigger_cmd, ["list-all", "--vault-dir", vault_dir])
    assert "A" in result.output
    assert "B" in result.output


def test_clear_reports_count(runner, vault_dir):
    runner.invoke(trigger_cmd, ["add", "X", "c1", "--vault-dir", vault_dir])
    runner.invoke(trigger_cmd, ["add", "X", "c2", "--vault-dir", vault_dir])
    result = runner.invoke(trigger_cmd, ["clear", "X", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "2" in result.output
