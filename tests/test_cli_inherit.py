"""Tests for env_vault.cli_inherit."""
import pytest
from click.testing import CliRunner

from env_vault.vault import Vault
from env_vault.cli_inherit import inherit_cmd

PASS = "testpass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_pair(tmp_path):
    parent_dir = tmp_path / "parent"
    child_dir = tmp_path / "child"
    parent = Vault(str(parent_dir))
    child = Vault(str(child_dir))

    parent.set("SHARED", "parent_val", PASS)
    parent.set("PARENT_ONLY", "only_in_parent", PASS)
    child.set("SHARED", "child_val", PASS)

    return str(child_dir), str(parent_dir)


def test_show_lists_all_keys(runner, vault_pair):
    child_dir, parent_dir = vault_pair
    result = runner.invoke(
        inherit_cmd, ["show", child_dir, parent_dir, "--passphrase", PASS]
    )
    assert result.exit_code == 0
    assert "SHARED" in result.output
    assert "PARENT_ONLY" in result.output


def test_show_marks_overridden_key(runner, vault_pair):
    child_dir, parent_dir = vault_pair
    result = runner.invoke(
        inherit_cmd, ["show", child_dir, parent_dir, "--passphrase", PASS]
    )
    assert "overridden" in result.output


def test_show_prints_summary(runner, vault_pair):
    child_dir, parent_dir = vault_pair
    result = runner.invoke(
        inherit_cmd, ["show", child_dir, parent_dir, "--passphrase", PASS]
    )
    assert "inherited" in result.output


def test_apply_copies_parent_keys(runner, vault_pair, tmp_path):
    child_dir, parent_dir = vault_pair
    result = runner.invoke(
        inherit_cmd, ["apply", child_dir, parent_dir, "--passphrase", PASS]
    )
    assert result.exit_code == 0
    assert "PARENT_ONLY" in result.output
    child = Vault(child_dir)
    assert child.get("PARENT_ONLY", PASS) == "only_in_parent"


def test_apply_does_not_overwrite_by_default(runner, vault_pair):
    child_dir, parent_dir = vault_pair
    runner.invoke(
        inherit_cmd, ["apply", child_dir, parent_dir, "--passphrase", PASS]
    )
    child = Vault(child_dir)
    assert child.get("SHARED", PASS) == "child_val"


def test_apply_overwrite_flag_replaces_child_key(runner, vault_pair):
    child_dir, parent_dir = vault_pair
    runner.invoke(
        inherit_cmd,
        ["apply", child_dir, parent_dir, "--passphrase", PASS, "--overwrite"],
    )
    child = Vault(child_dir)
    assert child.get("SHARED", PASS) == "parent_val"


def test_apply_nothing_to_inherit_message(runner, tmp_path):
    """When child already has all parent keys and no --overwrite, report nothing."""
    parent_dir = tmp_path / "p"
    child_dir = tmp_path / "c"
    parent = Vault(str(parent_dir))
    child = Vault(str(child_dir))
    parent.set("KEY", "val", PASS)
    child.set("KEY", "val", PASS)
    result = runner.invoke(
        inherit_cmd, ["apply", str(child_dir), str(parent_dir), "--passphrase", PASS]
    )
    assert "Nothing to inherit" in result.output
