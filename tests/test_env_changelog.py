"""Tests for env_vault.env_changelog."""
import pytest
from env_vault.env_changelog import (
    add_entry,
    get_entries,
    remove_entries,
    list_keys,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_entry_returns_dict(vault_dir):
    entry = add_entry(vault_dir, "API_KEY", "Initial release")
    assert isinstance(entry, dict)
    assert entry["message"] == "Initial release"
    assert "timestamp" in entry


def test_add_entry_author_stored(vault_dir):
    entry = add_entry(vault_dir, "API_KEY", "Added key", author="alice")
    assert entry["author"] == "alice"


def test_add_entry_no_author_is_none(vault_dir):
    entry = add_entry(vault_dir, "API_KEY", "msg")
    assert entry["author"] is None


def test_get_entries_returns_list(vault_dir):
    add_entry(vault_dir, "DB_URL", "first")
    add_entry(vault_dir, "DB_URL", "second")
    entries = get_entries(vault_dir, "DB_URL")
    assert len(entries) == 2
    assert entries[0]["message"] == "first"
    assert entries[1]["message"] == "second"


def test_get_entries_missing_key_returns_empty(vault_dir):
    assert get_entries(vault_dir, "NONEXISTENT") == []


def test_multiple_keys_are_independent(vault_dir):
    add_entry(vault_dir, "A", "msg-a")
    add_entry(vault_dir, "B", "msg-b")
    assert get_entries(vault_dir, "A")[0]["message"] == "msg-a"
    assert get_entries(vault_dir, "B")[0]["message"] == "msg-b"


def test_remove_entries_returns_true_when_found(vault_dir):
    add_entry(vault_dir, "KEY", "some change")
    assert remove_entries(vault_dir, "KEY") is True


def test_remove_entries_clears_key(vault_dir):
    add_entry(vault_dir, "KEY", "some change")
    remove_entries(vault_dir, "KEY")
    assert get_entries(vault_dir, "KEY") == []


def test_remove_entries_returns_false_when_missing(vault_dir):
    assert remove_entries(vault_dir, "GHOST") is False


def test_list_keys_returns_sorted(vault_dir):
    add_entry(vault_dir, "Z_KEY", "z")
    add_entry(vault_dir, "A_KEY", "a")
    assert list_keys(vault_dir) == ["A_KEY", "Z_KEY"]


def test_list_keys_empty_when_none(vault_dir):
    assert list_keys(vault_dir) == []


def test_list_keys_excludes_removed_key(vault_dir):
    add_entry(vault_dir, "TEMP", "temp")
    remove_entries(vault_dir, "TEMP")
    assert "TEMP" not in list_keys(vault_dir)
