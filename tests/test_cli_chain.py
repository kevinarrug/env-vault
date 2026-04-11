"""Tests for env_vault.cli_chain."""
from __future__ import annotations

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from env_vault.vault import Vault
from env_vault.cli_chain import chain_cmd

PASS = "testpass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_pair(tmp_path: Path):
    dirs = [str(tmp_path / "v1"), str(tmp_path / "v2")]
    v1 = Vault(dirs[0], PASS)
    v1.set("ALPHA", "first")
    v1.set("SHARED", "wins")

    v2 = Vault(dirs[1], PASS)
    v2.set("BETA", "second")
    v2.set("SHARED", "loses")

    return dirs


def test_get_existing_key(runner, vault_pair):
    result = runner.invoke(
        chain_cmd, ["get", "ALPHA", "--vault", vault_pair[0], "--vault", vault_pair[1],
                    "--passphrase", PASS]
    )
    assert result.exit_code == 0
    assert "first" in result.output


def test_get_fallback_key(runner, vault_pair):
    result = runner.invoke(
        chain_cmd, ["get", "BETA", "--vault", vault_pair[0], "--vault", vault_pair[1],
                    "--passphrase", PASS]
    )
    assert result.exit_code == 0
    assert "second" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_pair):
    result = runner.invoke(
        chain_cmd, ["get", "NOPE", "--vault", vault_pair[0], "--vault", vault_pair[1],
                    "--passphrase", PASS]
    )
    assert result.exit_code != 0


def test_get_as_json(runner, vault_pair):
    result = runner.invoke(
        chain_cmd, ["get", "ALPHA", "--vault", vault_pair[0], "--vault", vault_pair[1],
                    "--passphrase", PASS, "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["key"] == "ALPHA"
    assert data["found"] is True
    assert data["value"] == "first"


def test_dump_shows_all_keys(runner, vault_pair):
    result = runner.invoke(
        chain_cmd, ["dump", "--vault", vault_pair[0], "--vault", vault_pair[1],
                    "--passphrase", PASS]
    )
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output
    assert "SHARED" in result.output


def test_dump_as_json_earlier_vault_wins(runner, vault_pair):
    result = runner.invoke(
        chain_cmd, ["dump", "--vault", vault_pair[0], "--vault", vault_pair[1],
                    "--passphrase", PASS, "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["SHARED"]["value"] == "wins"
