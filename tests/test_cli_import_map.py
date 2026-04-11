"""Tests for env_vault.cli_import_map CLI commands."""
from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from env_vault.cli_import_map import import_map_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(
        import_map_cmd, ["set", "OLD", "NEW", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "Added" in result.output
    assert "OLD -> NEW" in result.output


def test_set_reports_updated(runner, vault_dir):
    runner.invoke(import_map_cmd, ["set", "OLD", "NEW", "--vault-dir", vault_dir])
    result = runner.invoke(
        import_map_cmd, ["set", "OLD", "OTHER", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_list_shows_mappings(runner, vault_dir):
    runner.invoke(import_map_cmd, ["set", "A", "AA", "--vault-dir", vault_dir])
    runner.invoke(import_map_cmd, ["set", "B", "BB", "--vault-dir", vault_dir])
    result = runner.invoke(import_map_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A -> AA" in result.output
    assert "B -> BB" in result.output


def test_list_empty_message(runner, vault_dir):
    result = runner.invoke(import_map_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No mappings" in result.output


def test_remove_existing(runner, vault_dir):
    runner.invoke(import_map_cmd, ["set", "X", "Y", "--vault-dir", vault_dir])
    result = runner.invoke(import_map_cmd, ["remove", "X", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing(runner, vault_dir):
    result = runner.invoke(
        import_map_cmd, ["remove", "GHOST", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "No mapping found" in result.output


def test_apply_remaps_keys(runner, vault_dir, tmp_path):
    runner.invoke(import_map_cmd, ["set", "DB_HOST", "DATABASE_HOST", "--vault-dir", vault_dir])
    json_file = tmp_path / "data.json"
    json_file.write_text(json.dumps({"DB_HOST": "localhost", "PORT": "5432"}))
    result = runner.invoke(
        import_map_cmd, ["apply", str(json_file), "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    payload = json.loads(result.output.split("\n", 1)[1])
    assert "DATABASE_HOST" in payload
    assert payload["DATABASE_HOST"] == "localhost"
    assert "PORT" in payload  # passed through


def test_apply_strict_skips_unmapped(runner, vault_dir, tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text(json.dumps({"UNMAPPED": "value"}))
    result = runner.invoke(
        import_map_cmd,
        ["apply", str(json_file), "--vault-dir", vault_dir, "--strict"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output.split("\n", 1)[1])
    assert "UNMAPPED" not in payload
