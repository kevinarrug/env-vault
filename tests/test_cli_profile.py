"""CLI tests for profile commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_profile import profile_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_create_and_list(runner, vault_dir):
    runner.invoke(profile_cmd, ["create", "dev", "--vault-dir", vault_dir])
    result = runner.invoke(profile_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_create_reports_success(runner, vault_dir):
    result = runner.invoke(profile_cmd, ["create", "staging", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_delete_existing_profile(runner, vault_dir):
    runner.invoke(profile_cmd, ["create", "dev", "--vault-dir", vault_dir])
    result = runner.invoke(profile_cmd, ["delete", "dev", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_missing_profile_exits_nonzero(runner, vault_dir):
    result = runner.invoke(profile_cmd, ["delete", "ghost", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_assign_and_show(runner, vault_dir):
    runner.invoke(profile_cmd, ["assign", "dev", "DB_URL", "--vault-dir", vault_dir])
    result = runner.invoke(profile_cmd, ["show", "dev", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_unassign_key(runner, vault_dir):
    runner.invoke(profile_cmd, ["assign", "dev", "SECRET", "--vault-dir", vault_dir])
    result = runner.invoke(profile_cmd, ["unassign", "dev", "SECRET", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_unassign_missing_key_exits_nonzero(runner, vault_dir):
    runner.invoke(profile_cmd, ["create", "dev", "--vault-dir", vault_dir])
    result = runner.invoke(profile_cmd, ["unassign", "dev", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_which_shows_profiles(runner, vault_dir):
    runner.invoke(profile_cmd, ["assign", "dev", "API_KEY", "--vault-dir", vault_dir])
    runner.invoke(profile_cmd, ["assign", "prod", "API_KEY", "--vault-dir", vault_dir])
    result = runner.invoke(profile_cmd, ["which", "API_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(profile_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No profiles" in result.output
