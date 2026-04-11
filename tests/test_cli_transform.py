"""Tests for env_vault.cli_transform CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_transform import transform_cmd
from env_vault.vault import Vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    v = Vault(str(tmp_path))
    v.set("MY_VAR", "hello world", "secret")
    v.set("ENCODED", "dGVzdA==", "secret")  # base64 of 'test'
    return str(tmp_path)


def test_list_shows_transforms(runner):
    result = runner.invoke(transform_cmd, ["list"])
    assert result.exit_code == 0
    assert "upper" in result.output
    assert "lower" in result.output
    assert "base64_encode" in result.output


def test_apply_upper_saves_value(runner, vault_dir):
    result = runner.invoke(
        transform_cmd,
        ["apply", vault_dir, "MY_VAR", "--passphrase", "secret", "--step", "upper"],
    )
    assert result.exit_code == 0
    assert "Transformed and saved" in result.output
    v = Vault(vault_dir)
    assert v.get("MY_VAR", "secret") == "HELLO WORLD"


def test_apply_dry_run_does_not_save(runner, vault_dir):
    result = runner.invoke(
        transform_cmd,
        [
            "apply", vault_dir, "MY_VAR",
            "--passphrase", "secret",
            "--step", "upper",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert "Preview" in result.output
    v = Vault(vault_dir)
    assert v.get("MY_VAR", "secret") == "hello world"


def test_apply_unknown_step_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        transform_cmd,
        ["apply", vault_dir, "MY_VAR", "--passphrase", "secret", "--step", "bogus"],
    )
    assert result.exit_code != 0


def test_preview_shows_transformation(runner, vault_dir):
    result = runner.invoke(
        transform_cmd,
        ["preview", vault_dir, "MY_VAR", "--passphrase", "secret", "--step", "reverse"],
    )
    assert result.exit_code == 0
    assert "dlrow olleh" in result.output


def test_preview_unknown_step_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        transform_cmd,
        ["preview", vault_dir, "MY_VAR", "--passphrase", "secret", "--step", "unknown"],
    )
    assert result.exit_code != 0


def test_apply_chained_steps(runner, vault_dir):
    result = runner.invoke(
        transform_cmd,
        [
            "apply", vault_dir, "MY_VAR",
            "--passphrase", "secret",
            "--step", "strip",
            "--step", "upper",
        ],
    )
    assert result.exit_code == 0
    v = Vault(vault_dir)
    assert v.get("MY_VAR", "secret") == "HELLO WORLD"
