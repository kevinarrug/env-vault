"""CLI tests for the alias command group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_alias import alias_cmd
from env_vault.alias import add_alias
from env_vault.vault import Vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    v = Vault(str(tmp_path), "secret")
    v.load()
    v.set("API_TOKEN", "abc123")
    v.save()
    return str(tmp_path)


def test_add_creates_alias(runner, vault_dir):
    result = runner.invoke(alias_cmd, ["add", "token", "API_TOKEN", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Created" in result.output


def test_add_updates_existing_alias(runner, vault_dir):
    runner.invoke(alias_cmd, ["add", "token", "API_TOKEN", "--vault-dir", vault_dir])
    result = runner.invoke(alias_cmd, ["add", "token", "OTHER_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_remove_existing_alias(runner, vault_dir):
    add_alias(vault_dir, "token", "API_TOKEN")
    result = runner.invoke(alias_cmd, ["remove", "token", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_alias_exits_nonzero(runner, vault_dir):
    result = runner.invoke(alias_cmd, ["remove", "ghost", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_list_shows_aliases(runner, vault_dir):
    add_alias(vault_dir, "tok", "API_TOKEN")
    result = runner.invoke(alias_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "tok" in result.output
    assert "API_TOKEN" in result.output


def test_list_empty_message(runner, vault_dir):
    result = runner.invoke(alias_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_resolve_prints_value(runner, vault_dir):
    add_alias(vault_dir, "tok", "API_TOKEN")
    result = runner.invoke(
        alias_cmd,
        ["resolve", "tok", "--vault-dir", vault_dir, "--passphrase", "secret"],
    )
    assert result.exit_code == 0
    assert "abc123" in result.output


def test_rename_alias_success(runner, vault_dir):
    add_alias(vault_dir, "old", "API_TOKEN")
    result = runner.invoke(alias_cmd, ["rename", "old", "new", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Renamed" in result.output
