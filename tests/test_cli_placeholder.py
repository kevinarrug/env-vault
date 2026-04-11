"""Tests for env_vault.cli_placeholder."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_placeholder import placeholder_cmd
from env_vault.vault import Vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    vault = Vault(str(tmp_path))
    vault.set("REAL_KEY", "actual_value", "pass")
    vault.set("EMPTY_KEY", "", "pass")
    vault.set("ANGLE_KEY", "<fill-me>", "pass")
    return str(tmp_path)


def test_scan_shows_all_keys(runner, vault_dir):
    result = runner.invoke(
        placeholder_cmd,
        ["scan", "--vault-dir", vault_dir, "--passphrase", "pass"],
    )
    assert result.exit_code == 0
    assert "REAL_KEY" in result.output
    assert "EMPTY_KEY" in result.output
    assert "ANGLE_KEY" in result.output


def test_list_shows_only_placeholders(runner, vault_dir):
    result = runner.invoke(
        placeholder_cmd,
        ["list", "--vault-dir", vault_dir, "--passphrase", "pass"],
    )
    assert result.exit_code == 0
    assert "EMPTY_KEY" in result.output
    assert "ANGLE_KEY" in result.output
    assert "REAL_KEY" not in result.output


def test_list_empty_vault_reports_none(runner, tmp_path):
    Vault(str(tmp_path))  # create empty vault dir
    result = runner.invoke(
        placeholder_cmd,
        ["list", "--vault-dir", str(tmp_path), "--passphrase", "pass"],
    )
    assert result.exit_code == 0
    assert "No placeholders" in result.output


def test_fill_placeholder_reports_filled(runner, vault_dir):
    result = runner.invoke(
        placeholder_cmd,
        ["fill", "ANGLE_KEY", "real-token", "--vault-dir", vault_dir, "--passphrase", "pass"],
    )
    assert result.exit_code == 0
    assert "Filled" in result.output


def test_fill_non_placeholder_reports_updated(runner, vault_dir):
    result = runner.invoke(
        placeholder_cmd,
        ["fill", "REAL_KEY", "new-value", "--vault-dir", vault_dir, "--passphrase", "pass"],
    )
    assert result.exit_code == 0
    assert "not a placeholder" in result.output
