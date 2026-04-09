"""Tests for env_vault.cli_audit CLI commands."""

import json

import pytest
from click.testing import CliRunner

from env_vault.audit import record_access
from env_vault.cli_audit import audit_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    record_access(d, "SET", "API_KEY", actor="alice")
    record_access(d, "GET", "DB_URL", actor="bob")
    return d


def test_log_shows_entries(runner, vault_dir):
    result = runner.invoke(audit_cmd, ["log", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "SET" in result.output
    assert "API_KEY" in result.output
    assert "alice" in result.output


def test_log_filter_by_key(runner, vault_dir):
    result = runner.invoke(audit_cmd, ["log", "--vault-dir", vault_dir, "--key", "DB_URL"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "API_KEY" not in result.output


def test_log_as_json(runner, vault_dir):
    result = runner.invoke(audit_cmd, ["log", "--vault-dir", vault_dir, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2
    assert "action" in data[0]


def test_log_empty_vault(runner, tmp_path):
    result = runner.invoke(audit_cmd, ["log", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No audit entries" in result.output


def test_clear_removes_entries(runner, vault_dir):
    result = runner.invoke(audit_cmd, ["clear", "--vault-dir", vault_dir], input="y\n")
    assert result.exit_code == 0
    assert "Cleared 2" in result.output
    log_result = runner.invoke(audit_cmd, ["log", "--vault-dir", vault_dir])
    assert "No audit entries" in log_result.output
