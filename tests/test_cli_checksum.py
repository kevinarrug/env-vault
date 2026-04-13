"""Tests for env_vault.cli_checksum."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from env_vault.vault import Vault
from env_vault.cli_checksum import checksum_cmd
from env_vault.env_checksum import record_checksum, get_checksum


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    v = Vault(str(tmp_path), "pass")
    v.set("DB_URL", "postgres://localhost/db")
    v.set("API_KEY", "secret123")
    return str(tmp_path)


def test_record_stores_checksum(runner, vault_dir):
    result = runner.invoke(
        checksum_cmd, ["record", "DB_URL", "--vault-dir", vault_dir, "--passphrase", "pass"]
    )
    assert result.exit_code == 0
    assert "Recorded checksum" in result.output
    assert get_checksum(vault_dir, "DB_URL") is not None


def test_get_shows_digest(runner, vault_dir):
    record_checksum(vault_dir, "API_KEY", "secret123")
    result = runner.invoke(
        checksum_cmd, ["get", "API_KEY", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert len(result.output.strip()) == 64


def test_get_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        checksum_cmd, ["get", "MISSING", "--vault-dir", vault_dir]
    )
    assert result.exit_code != 0


def test_remove_existing_checksum(runner, vault_dir):
    record_checksum(vault_dir, "DB_URL", "postgres://localhost/db")
    result = runner.invoke(
        checksum_cmd, ["remove", "DB_URL", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "Removed" in result.output
    assert get_checksum(vault_dir, "DB_URL") is None


def test_verify_ok_when_unchanged(runner, vault_dir):
    record_checksum(vault_dir, "DB_URL", "postgres://localhost/db")
    result = runner.invoke(
        checksum_cmd, ["verify", "DB_URL", "--vault-dir", vault_dir, "--passphrase", "pass"]
    )
    assert result.exit_code == 0
    assert "OK" in result.output


def test_verify_exits_nonzero_when_tampered(runner, vault_dir):
    record_checksum(vault_dir, "DB_URL", "original_value")
    result = runner.invoke(
        checksum_cmd, ["verify", "DB_URL", "--vault-dir", vault_dir, "--passphrase", "pass"]
    )
    assert result.exit_code != 0
    assert "TAMPERED" in result.output


def test_verify_all_no_checksums_reports_none(runner, vault_dir):
    result = runner.invoke(
        checksum_cmd, ["verify-all", "--vault-dir", vault_dir, "--passphrase", "pass"]
    )
    assert result.exit_code == 0
    assert "No checksums" in result.output
