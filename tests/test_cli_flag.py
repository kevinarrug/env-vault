"""Tests for env_vault.cli_flag."""
import pytest
from click.testing import CliRunner
from env_vault.cli_flag import flag_cmd
from env_vault.env_flag import set_flag


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(flag_cmd, ["set", "MY_KEY", "true", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "set to True" in result.output


def test_set_reports_unchanged(runner, vault_dir):
    set_flag(vault_dir, "MY_KEY", True)
    result = runner.invoke(flag_cmd, ["set", "MY_KEY", "true", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "unchanged" in result.output


def test_get_existing_flag(runner, vault_dir):
    set_flag(vault_dir, "MY_KEY", False)
    result = runner.invoke(flag_cmd, ["get", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "False" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(flag_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_remove_existing_flag(runner, vault_dir):
    set_flag(vault_dir, "MY_KEY", True)
    result = runner.invoke(flag_cmd, ["remove", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_flag_exits_nonzero(runner, vault_dir):
    result = runner.invoke(flag_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_list_shows_flags(runner, vault_dir):
    set_flag(vault_dir, "A", True)
    set_flag(vault_dir, "B", False)
    result = runner.invoke(flag_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A: True" in result.output
    assert "B: False" in result.output


def test_list_filter_true(runner, vault_dir):
    set_flag(vault_dir, "A", True)
    set_flag(vault_dir, "B", False)
    result = runner.invoke(flag_cmd, ["list", "--filter", "true", "--vault-dir", vault_dir])
    assert "A" in result.output
    assert "B" not in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(flag_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No flags" in result.output
