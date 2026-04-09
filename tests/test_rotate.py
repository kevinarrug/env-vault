"""Tests for env_vault.rotate and cli_rotate."""

from __future__ import annotations

import json
import os
import pytest
from click.testing import CliRunner

from env_vault.vault import Vault
from env_vault.rotate import rotate_passphrase, rotate_single_key
from env_vault.cli_rotate import rotate_cmd


OLD_PASS = "old-secret"
NEW_PASS = "new-secret"


@pytest.fixture()
def populated_vault(tmp_path):
    vault_file = str(tmp_path / "vault.json")
    v = Vault(vault_file)
    v.load()
    v.set("DB_URL", "postgres://localhost/db", OLD_PASS)
    v.set("API_KEY", "abc123", OLD_PASS)
    return v, vault_file


def test_rotate_passphrase_returns_all_keys(populated_vault):
    vault, _ = populated_vault
    rotated = rotate_passphrase(vault, OLD_PASS, NEW_PASS)
    assert set(rotated) == {"DB_URL", "API_KEY"}


def test_rotate_passphrase_values_readable_with_new_pass(populated_vault):
    vault, vault_file = populated_vault
    rotate_passphrase(vault, OLD_PASS, NEW_PASS)

    fresh = Vault(vault_file)
    fresh.load()
    assert fresh.get("DB_URL", NEW_PASS) == "postgres://localhost/db"
    assert fresh.get("API_KEY", NEW_PASS) == "abc123"


def test_rotate_passphrase_wrong_old_raises(populated_vault):
    vault, _ = populated_vault
    with pytest.raises((ValueError, Exception)):
        rotate_passphrase(vault, "wrong-pass", NEW_PASS)


def test_rotate_single_key_refreshes_nonce(populated_vault):
    vault, vault_file = populated_vault
    old_cipher = vault._data["secrets"]["DB_URL"]
    rotate_single_key(vault, "DB_URL", OLD_PASS)
    new_cipher = vault._data["secrets"]["DB_URL"]
    assert old_cipher != new_cipher  # nonce changed

    fresh = Vault(vault_file)
    fresh.load()
    assert fresh.get("DB_URL", OLD_PASS) == "postgres://localhost/db"


def test_rotate_single_key_missing_raises(populated_vault):
    vault, _ = populated_vault
    with pytest.raises(KeyError):
        rotate_single_key(vault, "NONEXISTENT", OLD_PASS)


def test_cli_rotate_all(populated_vault):
    _, vault_file = populated_vault
    runner = CliRunner()
    result = runner.invoke(
        rotate_cmd,
        ["all", "--vault-path", vault_file,
         "--old-passphrase", OLD_PASS,
         "--new-passphrase", NEW_PASS],
    )
    assert result.exit_code == 0, result.output
    assert "Rotated 2 key(s)" in result.output


def test_cli_rotate_key(populated_vault):
    _, vault_file = populated_vault
    runner = CliRunner()
    result = runner.invoke(
        rotate_cmd,
        ["key", "API_KEY", "--vault-path", vault_file,
         "--passphrase", OLD_PASS],
    )
    assert result.exit_code == 0, result.output
    assert "API_KEY" in result.output
