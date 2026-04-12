"""Tests for env_vault.cli_note."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_note import note_cmd
from env_vault.env_note import set_note


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_reports_added(runner, vault_dir):
    result = runner.invoke(note_cmd, ["set", "API_KEY", "main key", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "added" in result.output


def test_set_reports_updated(runner, vault_dir):
    set_note(vault_dir, "API_KEY", "old")
    result = runner.invoke(note_cmd, ["set", "API_KEY", "new note", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "updated" in result.output


def test_get_existing_note(runner, vault_dir):
    set_note(vault_dir, "DB_URL", "database note")
    result = runner.invoke(note_cmd, ["get", "DB_URL", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "database note" in result.output


def test_get_missing_note_exits_nonzero(runner, vault_dir):
    result = runner.invoke(note_cmd, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_remove_existing_note(runner, vault_dir):
    set_note(vault_dir, "SECRET", "note")
    result = runner.invoke(note_cmd, ["remove", "SECRET", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_note_exits_nonzero(runner, vault_dir):
    result = runner.invoke(note_cmd, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_list_shows_notes(runner, vault_dir):
    set_note(vault_dir, "A", "note a")
    set_note(vault_dir, "B", "note b")
    result = runner.invoke(note_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "A: note a" in result.output
    assert "B: note b" in result.output


def test_list_empty_vault(runner, vault_dir):
    result = runner.invoke(note_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No notes" in result.output


def test_clear_removes_all_notes(runner, vault_dir):
    set_note(vault_dir, "K1", "n1")
    set_note(vault_dir, "K2", "n2")
    result = runner.invoke(note_cmd, ["clear", "--vault-dir", vault_dir], input="y\n")
    assert result.exit_code == 0
    assert "2" in result.output
