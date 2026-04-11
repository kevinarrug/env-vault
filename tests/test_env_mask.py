"""Tests for env_vault.env_mask."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.vault import Vault
from env_vault.env_mask import (
    mask_full,
    mask_partial,
    mask_value,
    mask_key,
    mask_all,
    MaskResult,
)
from env_vault.cli_mask import mask_cmd

_PASS = "test-passphrase"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path))
    v.set("API_KEY", "supersecret1234", _PASS)
    v.set("DB_PASS", "hunter2", _PASS)
    return v


# --- unit tests for masking helpers ---

def test_mask_full_returns_stars():
    assert mask_full("mysecret") == "********"


def test_mask_partial_keeps_last_four():
    result = mask_partial("supersecret1234")
    assert result.endswith("1234")
    assert "*" in result


def test_mask_partial_short_value_returns_full_mask():
    assert mask_partial("abc") == "********"


def test_mask_value_full_mode():
    assert mask_value("anything", mode="full") == "********"


def test_mask_value_none_mode_returns_original():
    assert mask_value("plaintext", mode="none") == "plaintext"


def test_mask_value_partial_mode():
    result = mask_value("abcdefgh", mode="partial")
    assert result.endswith("efgh")


def test_mask_value_invalid_mode_raises():
    with pytest.raises(ValueError, match="Unknown mask mode"):
        mask_value("val", mode="bogus")


# --- integration with Vault ---

def test_mask_key_returns_mask_result(vault):
    result = mask_key(vault, _PASS, "API_KEY")
    assert isinstance(result, MaskResult)
    assert result.key == "API_KEY"
    assert result.masked == "********"
    assert result.original == "supersecret1234"


def test_mask_all_covers_every_key(vault):
    results = mask_all(vault, _PASS)
    keys = {r.key for r in results}
    assert keys == {"API_KEY", "DB_PASS"}


def test_mask_all_sorted_by_key(vault):
    results = mask_all(vault, _PASS)
    assert results[0].key <= results[-1].key


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_get_masked_value(runner, vault, tmp_path):
    result = runner.invoke(
        mask_cmd, ["get", str(tmp_path), "API_KEY", "-p", _PASS]
    )
    assert result.exit_code == 0
    assert "API_KEY=" in result.output
    assert "supersecret" not in result.output


def test_cli_dump_all_keys(runner, vault, tmp_path):
    result = runner.invoke(
        mask_cmd, ["dump", str(tmp_path), "-p", _PASS]
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_PASS" in result.output


def test_cli_dump_reveal_shows_original(runner, vault, tmp_path):
    result = runner.invoke(
        mask_cmd, ["dump", str(tmp_path), "-p", _PASS, "--reveal"]
    )
    assert result.exit_code == 0
    assert "supersecret1234" in result.output


def test_cli_get_missing_key_exits_nonzero(runner, vault, tmp_path):
    result = runner.invoke(
        mask_cmd, ["get", str(tmp_path), "MISSING", "-p", _PASS]
    )
    assert result.exit_code != 0
