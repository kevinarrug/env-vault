"""Tests for env_vault.env_note."""
from __future__ import annotations

import pytest

from env_vault.env_note import (
    set_note,
    get_note,
    remove_note,
    list_notes,
    clear_notes,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_note_returns_true_when_new(vault_dir):
    assert set_note(vault_dir, "API_KEY", "primary API key") is True


def test_set_note_returns_false_when_updated(vault_dir):
    set_note(vault_dir, "API_KEY", "first note")
    assert set_note(vault_dir, "API_KEY", "updated note") is False


def test_get_note_returns_value(vault_dir):
    set_note(vault_dir, "DB_URL", "database connection string")
    assert get_note(vault_dir, "DB_URL") == "database connection string"


def test_get_note_missing_returns_none(vault_dir):
    assert get_note(vault_dir, "MISSING") is None


def test_remove_note_returns_true_when_found(vault_dir):
    set_note(vault_dir, "SECRET", "some note")
    assert remove_note(vault_dir, "SECRET") is True


def test_remove_note_returns_false_when_missing(vault_dir):
    assert remove_note(vault_dir, "GHOST") is False


def test_remove_note_deletes_entry(vault_dir):
    set_note(vault_dir, "KEY", "note")
    remove_note(vault_dir, "KEY")
    assert get_note(vault_dir, "KEY") is None


def test_list_notes_returns_all(vault_dir):
    set_note(vault_dir, "B", "note b")
    set_note(vault_dir, "A", "note a")
    result = list_notes(vault_dir)
    assert result == {"A": "note a", "B": "note b"}


def test_list_notes_sorted_by_key(vault_dir):
    set_note(vault_dir, "Z", "last")
    set_note(vault_dir, "A", "first")
    keys = list(list_notes(vault_dir).keys())
    assert keys == sorted(keys)


def test_list_notes_empty(vault_dir):
    assert list_notes(vault_dir) == {}


def test_clear_notes_returns_count(vault_dir):
    set_note(vault_dir, "K1", "n1")
    set_note(vault_dir, "K2", "n2")
    assert clear_notes(vault_dir) == 2


def test_clear_notes_removes_all(vault_dir):
    set_note(vault_dir, "K1", "n1")
    clear_notes(vault_dir)
    assert list_notes(vault_dir) == {}


def test_clear_notes_empty_vault_returns_zero(vault_dir):
    assert clear_notes(vault_dir) == 0
