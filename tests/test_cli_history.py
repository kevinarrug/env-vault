"""Tests for env_vault.cli_history CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_vault.cli_history import history_cmd
from env_vault.crypto import encrypt
from env_vault.history import HISTORY_FILENAME, record_change

PASSPHRASE = "test-passphrase"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_log_shows_decrypted_values(runner: CliRunner, vault_dir: Path) -> None:
    history_path = vault_dir / HISTORY_FILENAME
    enc = encrypt("postgres://localhost/db", PASSPHRASE)
    record_change(history_path, "DB_URL", enc)

    result = runner.invoke(
        history_cmd,
        ["log", "DB_URL", "--vault-dir", str(vault_dir), "--passphrase", PASSPHRASE],
    )
    assert result.exit_code == 0
    assert "postgres://localhost/db" in result.output
    assert "set" in result.output


def test_log_no_history(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        history_cmd,
        ["log", "MISSING", "--vault-dir", str(vault_dir), "--passphrase", PASSPHRASE],
    )
    assert result.exit_code == 0
    assert "No history" in result.output


def test_list_shows_keys(runner: CliRunner, vault_dir: Path) -> None:
    history_path = vault_dir / HISTORY_FILENAME
    record_change(history_path, "ALPHA", "enc_a")
    record_change(history_path, "BETA", "enc_b")

    result = runner.invoke(
        history_cmd, ["list", "--vault-dir", str(vault_dir)]
    )
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_list_empty(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        history_cmd, ["list", "--vault-dir", str(vault_dir)]
    )
    assert result.exit_code == 0
    assert "No history" in result.output


def test_purge_removes_key(runner: CliRunner, vault_dir: Path) -> None:
    history_path = vault_dir / HISTORY_FILENAME
    record_change(history_path, "PURGE_ME", "enc")

    result = runner.invoke(
        history_cmd,
        ["purge", "PURGE_ME", "--vault-dir", str(vault_dir), "--yes"],
    )
    assert result.exit_code == 0
    assert "purged" in result.output.lower()

    list_result = runner.invoke(
        history_cmd, ["list", "--vault-dir", str(vault_dir)]
    )
    assert "PURGE_ME" not in list_result.output
