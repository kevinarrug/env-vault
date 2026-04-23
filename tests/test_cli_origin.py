"""Tests for env_vault.cli_origin."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_origin import origin_cmd
from env_vault.env_origin import set_origin


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(origin_cmd, ["set", "API_KEY", "aws", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "set to 'aws'" in result.output


def test_set_reports_unchanged(runner, vault_dir):
    set_origin(vault_dir, "API_KEY", "aws")
    result = runner.invoke(origin_cmd, ["set", "API_KEY", "aws", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "unchanged" in result.output


def test_remove_existing_origin(runner, vault_dir):
    set_origin(vault_dir, "TOKEN", "github")
    result = runner.invoke(origin_cmd, ["remove", "TOKEN", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_origin(runner, vault_dir):
    result = runner.invoke(origin_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No origin found" in result.output


def test_get_existing_origin(runner, vault_dir):
    set_origin(vault_dir, "DB_PASS", "heroku")
    result = runner.invoke(origin_cmd, ["get", "DB_PASS", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "heroku" in result.output


def test_get_missing_origin_exits_nonzero(runner, vault_dir):
    result = runner.invoke(origin_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_list_shows_origins(runner, vault_dir):
    set_origin(vault_dir, "A", "aws")
    set_origin(vault_dir, "B", "gcp")
    result = runner.invoke(origin_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A: aws" in result.output
    assert "B: gcp" in result.output


def test_list_empty_vault_reports_none(runner, vault_dir):
    result = runner.invoke(origin_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No origins" in result.output


def test_filter_shows_matching_keys(runner, vault_dir):
    set_origin(vault_dir, "A", "aws")
    set_origin(vault_dir, "B", "gcp")
    set_origin(vault_dir, "C", "aws")
    result = runner.invoke(origin_cmd, ["filter", "aws", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "C" in result.output
    assert "B" not in result.output
