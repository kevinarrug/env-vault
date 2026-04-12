"""Tests for env_vault.cli_freeze CLI commands."""

import pytest
from click.testing import CliRunner

from env_vault.cli_freeze import freeze_cmd
from env_vault.env_freeze import freeze_key, is_frozen


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_freezes_key(runner, vault_dir):
    result = runner.invoke(freeze_cmd, ["set", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "frozen" in result.output
    assert is_frozen(vault_dir, "MY_KEY")


def test_set_reports_already_frozen(runner, vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    result = runner.invoke(freeze_cmd, ["set", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "already frozen" in result.output


def test_remove_unfreezes_key(runner, vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    result = runner.invoke(freeze_cmd, ["remove", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "unfrozen" in result.output
    assert not is_frozen(vault_dir, "MY_KEY")


def test_remove_reports_not_frozen(runner, vault_dir):
    result = runner.invoke(freeze_cmd, ["remove", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "not frozen" in result.output


def test_get_shows_frozen_state(runner, vault_dir):
    freeze_key(vault_dir, "MY_KEY")
    result = runner.invoke(freeze_cmd, ["get", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "frozen" in result.output


def test_get_shows_not_frozen_state(runner, vault_dir):
    result = runner.invoke(freeze_cmd, ["get", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "not frozen" in result.output


def test_list_empty_reports_none(runner, vault_dir):
    result = runner.invoke(freeze_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No frozen keys" in result.output


def test_list_shows_frozen_keys(runner, vault_dir):
    freeze_key(vault_dir, "KEY_A")
    freeze_key(vault_dir, "KEY_B")
    result = runner.invoke(freeze_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output
