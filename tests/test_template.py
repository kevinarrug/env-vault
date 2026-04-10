"""Tests for env_vault.template and cli_template."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_template import template_cmd
from env_vault.template import RenderResult, render_template
from env_vault.vault import Vault

PASS = "test-pass"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path))
    v.set("DB_HOST", "localhost", PASS)
    v.set("DB_PORT", "5432", PASS)
    v.set("API_KEY", "secret-key", PASS)
    return v


# --- unit tests for render_template ---

def test_render_substitutes_known_keys(vault):
    result = render_template("host={{ DB_HOST }} port={{ DB_PORT }}", vault, PASS)
    assert result.rendered == "host=localhost port=5432"


def test_render_result_tracks_substituted(vault):
    result = render_template("{{ DB_HOST }}", vault, PASS)
    assert "DB_HOST" in result.substituted
    assert result.missing == []


def test_render_missing_key_leaves_placeholder(vault):
    result = render_template("{{ UNKNOWN }}", vault, PASS)
    assert "{{ UNKNOWN }}" in result.rendered
    assert "UNKNOWN" in result.missing


def test_render_has_missing_true_when_missing(vault):
    result = render_template("{{ NOPE }}", vault, PASS)
    assert result.has_missing is True


def test_render_has_missing_false_when_all_resolved(vault):
    result = render_template("{{ DB_HOST }}", vault, PASS)
    assert result.has_missing is False


def test_render_strict_raises_on_missing(vault):
    with pytest.raises(KeyError, match="UNKNOWN"):
        render_template("{{ UNKNOWN }}", vault, PASS, strict=True)


def test_render_no_placeholders(vault):
    result = render_template("plain text", vault, PASS)
    assert result.rendered == "plain text"
    assert result.substituted == []
    assert result.missing == []


def test_render_result_summary_no_placeholders(vault):
    result = render_template("plain", vault, PASS)
    assert result.summary() == "no placeholders found"


def test_render_result_summary_with_substituted(vault):
    result = render_template("{{ DB_HOST }}", vault, PASS)
    assert "substituted" in result.summary()
    assert "DB_HOST" in result.summary()


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_render_to_stdout(runner, vault, tmp_path):
    tmpl = tmp_path / "app.conf"
    tmpl.write_text("host={{ DB_HOST }}\nport={{ DB_PORT }}\n")
    res = runner.invoke(
        template_cmd,
        ["render", str(tmpl), "--vault-dir", str(tmp_path), "--passphrase", PASS],
    )
    assert res.exit_code == 0
    assert "host=localhost" in res.output
    assert "port=5432" in res.output


def test_cli_render_warns_on_missing(runner, vault, tmp_path):
    tmpl = tmp_path / "t.txt"
    tmpl.write_text("{{ MISSING_KEY }}")
    res = runner.invoke(
        template_cmd,
        ["render", str(tmpl), "--vault-dir", str(tmp_path), "--passphrase", PASS],
    )
    assert res.exit_code == 0
    assert "MISSING_KEY" in res.output + (res.stderr if hasattr(res, "stderr") else "")


def test_cli_render_strict_exits_nonzero(runner, vault, tmp_path):
    tmpl = tmp_path / "t.txt"
    tmpl.write_text("{{ MISSING_KEY }}")
    res = runner.invoke(
        template_cmd,
        ["render", str(tmpl), "--vault-dir", str(tmp_path), "--passphrase", PASS, "--strict"],
    )
    assert res.exit_code != 0


def test_cli_preview_command(runner, vault, tmp_path):
    res = runner.invoke(
        template_cmd,
        ["preview", "host={{ DB_HOST }}", "--vault-dir", str(tmp_path), "--passphrase", PASS],
    )
    assert res.exit_code == 0
    assert "host=localhost" in res.output
