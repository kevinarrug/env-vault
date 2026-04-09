"""Integration tests for the export/import CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from env_vault.cli_export import export_cmd, import_cmd
from env_vault.vault import Vault


PASSPHRASE = "test-passphrase-42"


@pytest.fixture()
def populated_vault(tmp_path):
    vault_file = str(tmp_path / "test.vault")
    v = Vault(vault_file, PASSPHRASE)
    v.set("APP_ENV", "production")
    v.set("PORT", "8080")
    v.save()
    return vault_file


def test_export_dotenv_to_stdout(populated_vault):
    runner = CliRunner()
    result = runner.invoke(
        export_cmd,
        ["--vault", populated_vault, "--format", "dotenv", "--passphrase", PASSPHRASE],
    )
    assert result.exit_code == 0
    assert "APP_ENV=" in result.output
    assert "PORT=" in result.output


def test_export_json_to_file(tmp_path, populated_vault):
    out_file = str(tmp_path / "vars.json")
    runner = CliRunner()
    result = runner.invoke(
        export_cmd,
        [
            "--vault", populated_vault,
            "--format", "json",
            "--output", out_file,
            "--passphrase", PASSPHRASE,
        ],
    )
    assert result.exit_code == 0
    data = json.loads(Path(out_file).read_text())
    assert data["APP_ENV"] == "production"
    assert data["PORT"] == "8080"


def test_import_dotenv_file(tmp_path):
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text('IMPORTED_KEY="hello"\nANOTHER="world"\n')
    vault_file = str(tmp_path / "new.vault")

    runner = CliRunner()
    result = runner.invoke(
        import_cmd,
        [
            str(dotenv_file),
            "--vault", vault_file,
            "--format", "dotenv",
            "--passphrase", PASSPHRASE,
        ],
    )
    assert result.exit_code == 0
    assert "Imported 2" in result.output

    v = Vault(vault_file, PASSPHRASE)
    v.load()
    assert v.get("IMPORTED_KEY") == "hello"
    assert v.get("ANOTHER") == "world"


def test_import_json_file(tmp_path):
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"JSON_VAR": "42"}))
    vault_file = str(tmp_path / "new.vault")

    runner = CliRunner()
    result = runner.invoke(
        import_cmd,
        [
            str(json_file),
            "--vault", vault_file,
            "--format", "json",
            "--passphrase", PASSPHRASE,
        ],
    )
    assert result.exit_code == 0

    v = Vault(vault_file, PASSPHRASE)
    v.load()
    assert v.get("JSON_VAR") == "42"
