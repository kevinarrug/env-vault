"""Tests for env_vault.lint and env_vault.cli_lint."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.vault import Vault
from env_vault.lint import lint_vault, LintResult
from env_vault.cli_lint import lint_cmd


PASS = "s3cr3t"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault.json"))
    v.load(PASS)
    return v


def test_lint_clean_vault_passes(vault):
    vault.set("DATABASE_URL", "postgres://localhost/db", PASS)
    vault.set("API_KEY", "abc123", PASS)
    result = lint_vault(vault, PASS)
    assert result.passed
    assert result.issues == []


def test_lint_empty_vault_passes(vault):
    result = lint_vault(vault, PASS)
    assert result.passed
    assert result.issues == []


def test_lint_warns_on_lowercase_key(vault):
    vault.set("myKey", "value", PASS)
    result = lint_vault(vault, PASS)
    warnings = [i for i in result.issues if i.level == "warning" and "lowercase" in i.message]
    assert warnings, "Expected a warning about lowercase key"


def test_lint_warns_on_empty_value(vault):
    vault.set("EMPTY_VAR", "", PASS)
    result = lint_vault(vault, PASS)
    warn_msgs = [i.message for i in result.issues if i.level == "warning"]
    assert any("empty" in m.lower() for m in warn_msgs)


def test_lint_result_summary_no_issues(vault):
    result = lint_vault(vault, PASS)
    assert result.summary() == "No issues found."


def test_lint_result_summary_with_issues(vault):
    vault.set("bad-key!", "val", PASS)
    result = lint_vault(vault, PASS)
    summary = result.summary()
    assert "error" in summary.lower() or "warning" in summary.lower()


# --- CLI tests ---


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_check_clean_vault(runner, tmp_path):
    v = Vault(str(tmp_path / "vault.json"))
    v.load(PASS)
    v.set("CLEAN_KEY", "value", PASS)
    v.save(PASS)

    result = runner.invoke(lint_cmd, ["check", str(tmp_path / "vault.json"), "-p", PASS])
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_cli_check_with_warnings_exits_zero_without_strict(runner, tmp_path):
    v = Vault(str(tmp_path / "vault.json"))
    v.load(PASS)
    v.set("emptyVal", "", PASS)
    v.save(PASS)

    result = runner.invoke(lint_cmd, ["check", str(tmp_path / "vault.json"), "-p", PASS])
    assert result.exit_code == 0


def test_cli_check_json_output(runner, tmp_path):
    import json
    v = Vault(str(tmp_path / "vault.json"))
    v.load(PASS)
    v.set("GOOD", "val", PASS)
    v.save(PASS)

    result = runner.invoke(lint_cmd, ["check", str(tmp_path / "vault.json"), "-p", PASS, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
