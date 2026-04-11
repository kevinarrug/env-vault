"""Tests for env_vault.cli_ttl."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_ttl import ttl_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_ttl_success(runner, vault_dir):
    result = runner.invoke(ttl_cmd, ["set", vault_dir, "MY_KEY", "60"])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "60s" in result.output


def test_set_ttl_invalid_seconds(runner, vault_dir):
    result = runner.invoke(ttl_cmd, ["set", vault_dir, "KEY", "0"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_set_ttl_negative_seconds(runner, vault_dir):
    result = runner.invoke(ttl_cmd, ["set", vault_dir, "KEY", "-10"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_get_ttl_shows_remaining(runner, vault_dir):
    runner.invoke(ttl_cmd, ["set", vault_dir, "KEY", "120"])
    result = runner.invoke(ttl_cmd, ["get", vault_dir, "KEY"])
    assert result.exit_code == 0
    assert "KEY" in result.output
    assert "s" in result.output


def test_get_ttl_missing_key(runner, vault_dir):
    result = runner.invoke(ttl_cmd, ["get", vault_dir, "MISSING"])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_remove_existing_ttl(runner, vault_dir):
    runner.invoke(ttl_cmd, ["set", vault_dir, "KEY", "60"])
    result = runner.invoke(ttl_cmd, ["remove", vault_dir, "KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_nonexistent_ttl(runner, vault_dir):
    result = runner.invoke(ttl_cmd, ["remove", vault_dir, "GHOST"])
    assert result.exit_code == 0
    assert "No TTL found" in result.output


def test_list_shows_all_keys(runner, vault_dir):
    runner.invoke(ttl_cmd, ["set", vault_dir, "ALPHA", "60"])
    runner.invoke(ttl_cmd, ["set", vault_dir, "BETA", "120"])
    result = runner.invoke(ttl_cmd, ["list", vault_dir])
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(ttl_cmd, ["list", vault_dir])
    assert result.exit_code == 0
    assert "No TTLs" in result.output


def test_purge_with_no_expired(runner, vault_dir):
    runner.invoke(ttl_cmd, ["set", vault_dir, "KEY", "300"])
    result = runner.invoke(ttl_cmd, ["purge", vault_dir])
    assert result.exit_code == 0
    assert "No expired" in result.output
