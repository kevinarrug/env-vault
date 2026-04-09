"""Tests for the CLI diff commands."""
import json
import os
import pytest
from click.testing import CliRunner
from env_vault.vault import Vault
from env_vault.cli_diff import diff_cmd


PASSPHRASE = "test-secret"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_pair(tmp_path):
    path_a = str(tmp_path / "vault_a.json")
    path_b = str(tmp_path / "vault_b.json")

    va = Vault(path_a, PASSPHRASE)
    va.set("KEY_SHARED", "same_value", PASSPHRASE)
    va.set("KEY_CHANGED", "old_value", PASSPHRASE)
    va.set("KEY_REMOVED", "gone", PASSPHRASE)

    vb = Vault(path_b, PASSPHRASE)
    vb.set("KEY_SHARED", "same_value", PASSPHRASE)
    vb.set("KEY_CHANGED", "new_value", PASSPHRASE)
    vb.set("KEY_ADDED", "fresh", PASSPHRASE)

    return path_a, path_b


@pytest.fixture
def json_pair(tmp_path):
    path_a = tmp_path / "a.json"
    path_b = tmp_path / "b.json"
    path_a.write_text(json.dumps({"FOO": "bar", "BAZ": "qux", "OLD": "x"}))
    path_b.write_text(json.dumps({"FOO": "bar", "BAZ": "changed", "NEW": "y"}))
    return str(path_a), str(path_b)


def test_compare_vaults_no_changes(runner, tmp_path):
    path_a = str(tmp_path / "va.json")
    path_b = str(tmp_path / "vb.json")
    va = Vault(path_a, PASSPHRASE)
    va.set("K", "v", PASSPHRASE)
    vb = Vault(path_b, PASSPHRASE)
    vb.set("K", "v", PASSPHRASE)

    result = runner.invoke(diff_cmd, ["vaults", path_a, path_b, "--passphrase-a", PASSPHRASE])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_compare_vaults_shows_changes(runner, vault_pair):
    path_a, path_b = vault_pair
    result = runner.invoke(diff_cmd, ["vaults", path_a, path_b, "--passphrase-a", PASSPHRASE])
    assert result.exit_code == 0
    assert "KEY_ADDED" in result.output
    assert "KEY_REMOVED" in result.output
    assert "KEY_CHANGED" in result.output


def test_compare_vaults_json_output(runner, vault_pair):
    path_a, path_b = vault_pair
    result = runner.invoke(
        diff_cmd, ["vaults", path_a, path_b, "--passphrase-a", PASSPHRASE, "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "KEY_ADDED" in data["added"]
    assert "KEY_REMOVED" in data["removed"]
    assert "KEY_CHANGED" in data["changed"]
    assert "KEY_SHARED" in data["unchanged"]


def test_compare_dicts_no_changes(runner, tmp_path):
    p = tmp_path / "same.json"
    p.write_text(json.dumps({"A": "1"}))
    result = runner.invoke(diff_cmd, ["dicts", str(p), str(p)])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_compare_dicts_shows_changes(runner, json_pair):
    path_a, path_b = json_pair
    result = runner.invoke(diff_cmd, ["dicts", path_a, path_b])
    assert result.exit_code == 0
    assert "NEW" in result.output
    assert "OLD" in result.output
    assert "BAZ" in result.output


def test_compare_dicts_json_output(runner, json_pair):
    path_a, path_b = json_pair
    result = runner.invoke(diff_cmd, ["dicts", path_a, path_b, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "NEW" in data["added"]
    assert "OLD" in data["removed"]
    assert "BAZ" in data["changed"]
    assert "FOO" in data["unchanged"]
