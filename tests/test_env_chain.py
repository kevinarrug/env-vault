"""Tests for env_vault.env_chain."""
from __future__ import annotations

import pytest
from pathlib import Path

from env_vault.vault import Vault
from env_vault.env_chain import resolve, resolve_all, ChainResult

PASS = "testpass"


@pytest.fixture()
def chain_vaults(tmp_path: Path):
    """Create two vault directories with overlapping and unique keys."""
    dirs = [str(tmp_path / "v1"), str(tmp_path / "v2")]
    v1 = Vault(dirs[0], PASS)
    v1.set("SHARED", "from-v1")
    v1.set("ONLY_V1", "alpha")

    v2 = Vault(dirs[1], PASS)
    v2.set("SHARED", "from-v2")
    v2.set("ONLY_V2", "beta")

    return dirs


def test_chain_result_found_true(chain_vaults):
    result = resolve("SHARED", chain_vaults, PASS)
    assert result.found is True


def test_chain_result_found_false(chain_vaults):
    result = resolve("MISSING", chain_vaults, PASS)
    assert result.found is False


def test_resolve_returns_first_vault_value(chain_vaults):
    result = resolve("SHARED", chain_vaults, PASS)
    assert result.value == "from-v1"
    assert result.source == chain_vaults[0]


def test_resolve_falls_back_to_second_vault(chain_vaults):
    result = resolve("ONLY_V2", chain_vaults, PASS)
    assert result.value == "beta"
    assert result.source == chain_vaults[1]


def test_resolve_records_checked_dirs(chain_vaults):
    result = resolve("ONLY_V2", chain_vaults, PASS)
    assert chain_vaults[0] in result.checked
    assert chain_vaults[1] in result.checked


def test_resolve_missing_source_is_none(chain_vaults):
    result = resolve("MISSING", chain_vaults, PASS)
    assert result.source is None


def test_chain_result_str_found(chain_vaults):
    result = resolve("ONLY_V1", chain_vaults, PASS)
    s = str(result)
    assert "ONLY_V1" in s
    assert "alpha" in s


def test_chain_result_str_not_found(chain_vaults):
    result = resolve("MISSING", chain_vaults, PASS)
    assert "not found" in str(result)


def test_resolve_all_contains_all_keys(chain_vaults):
    results = resolve_all(chain_vaults, PASS)
    assert "SHARED" in results
    assert "ONLY_V1" in results
    assert "ONLY_V2" in results


def test_resolve_all_earlier_vault_wins(chain_vaults):
    results = resolve_all(chain_vaults, PASS)
    assert results["SHARED"].value == "from-v1"
    assert results["SHARED"].source == chain_vaults[0]
