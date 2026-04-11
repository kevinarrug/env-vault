"""Tests for env_vault.cli_cast CLI commands."""

from __future__ import annotations

import json
import os
import pytest

from click.testing import CliRunner

from env_vault.vault import Vault
from env_vault.cli_cast import cast_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    v = Vault(str(tmp_path))
    passphrase = "testpass"
    v.set("PORT", "9000", passphrase)
    v.set("DEBUG", "true", passphrase)
    v.set("RATE", "2.71", passphrase)
    v.set("TAGS", "x,y,z", passphrase)
    return str(tmp_path)


@pytest.fixture
def schema_file(tmp_path, vault_dir):
    schema = {"PORT": "int", "DEBUG": "bool", "RATE": "float", "TAGS": "list"}
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(schema))
    return str(path)


def test_get_int_success(runner, vault_dir):
    result = runner.invoke(
        cast_cmd, ["get", vault_dir, "PORT", "int", "--passphrase", "testpass"]
    )
    assert result.exit_code == 0
    assert "PORT" in result.output
    assert "int" in result.output
    assert "9000" in result.output


def test_get_bool_success(runner, vault_dir):
    result = runner.invoke(
        cast_cmd, ["get", vault_dir, "DEBUG", "bool", "--passphrase", "testpass"]
    )
    assert result.exit_code == 0
    assert "True" in result.output


def test_get_invalid_cast_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        cast_cmd, ["get", vault_dir, "TAGS", "int", "--passphrase", "testpass"]
    )
    assert result.exit_code != 0


def test_apply_outputs_all_keys(runner, vault_dir, schema_file):
    result = runner.invoke(
        cast_cmd, ["apply", vault_dir, schema_file, "--passphrase", "testpass"]
    )
    assert result.exit_code == 0
    assert "PORT" in result.output
    assert "DEBUG" in result.output


def test_apply_json_output_is_valid(runner, vault_dir, schema_file):
    result = runner.invoke(
        cast_cmd, ["apply", vault_dir, schema_file, "--passphrase", "testpass", "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["PORT"]["value"] == 9000
    assert data["DEBUG"]["value"] is True
    assert data["RATE"]["success"] is True


def test_apply_exits_nonzero_on_bad_schema(runner, vault_dir, tmp_path):
    bad_schema = tmp_path / "bad.json"
    bad_schema.write_text(json.dumps({"TAGS": "int"}))
    result = runner.invoke(
        cast_cmd, ["apply", vault_dir, str(bad_schema), "--passphrase", "testpass"]
    )
    assert result.exit_code != 0
