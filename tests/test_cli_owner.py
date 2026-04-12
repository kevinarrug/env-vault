"""Tests for env_vault.cli_owner."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_owner import owner_cmd
from env_vault.env_owner import set_owner


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(owner_cmd, ["set", "API_KEY", "alice", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "set to 'alice'" in result.output


def test_set_reports_unchanged(runner, vault_dir):
    set_owner(vault_dir, "API_KEY", "alice")
    result = runner.invoke(owner_cmd, ["set", "API_KEY", "alice", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "unchanged" in result.output


def test_remove_existing_owner(runner, vault_dir):
    set_owner(vault_dir, "TOKEN", "bob")
    result = runner.invoke(owner_cmd, ["remove", "TOKEN", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_owner(runner, vault_dir):
    result = runner.invoke(owner_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No ownership record" in result.output


def test_get_existing_owner(runner, vault_dir):
    set_owner(vault_dir, "DB_PASS", "charlie")
    result = runner.invoke(owner_cmd, ["get", "DB_PASS", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "charlie" in result.output


def test_get_missing_owner(runner, vault_dir):
    result = runner.invoke(owner_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No owner set" in result.output


def test_list_all_owners(runner, vault_dir):
    set_owner(vault_dir, "A", "alice")
    set_owner(vault_dir, "B", "bob")
    result = runner.invoke(owner_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A: alice" in result.output
    assert "B: bob" in result.output


def test_list_filter_by_owner(runner, vault_dir):
    set_owner(vault_dir, "X", "alice")
    set_owner(vault_dir, "Y", "bob")
    result = runner.invoke(owner_cmd, ["list", "--owner", "alice", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "X" in result.output
    assert "Y" not in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(owner_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No ownership records" in result.output
